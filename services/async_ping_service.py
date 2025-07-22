import concurrent.futures
import threading
import time
from typing import List, Dict, Any
from datetime import datetime
import logging

from services.network_service import NetworkService

logger = logging.getLogger(__name__)

class AsyncPingService:
    """Асинхронный сервис для многопоточного пинга большого количества адресов"""
    
    def __init__(self, max_threads: int = 50, batch_size: int = 100):
        self.max_threads = max_threads
        self.batch_size = batch_size
        self.network_service = NetworkService()
        self._lock = threading.Lock()
        
    def ping_single_address(self, ip_address: str) -> Dict[str, Any]:
        """Пинг одного IP адреса"""
        try:
            result = self.network_service.ping_address(ip_address)
            return result
        except Exception as e:
            logger.error(f"Error pinging {ip_address}: {str(e)}")
            return {
                'ip_address': ip_address,
                'status': 'error',
                'response_time': None,
                'error_message': str(e),
                'timestamp': datetime.utcnow()
            }
    
    def ping_batch_async(self, ip_addresses: List[str]) -> List[Dict[str, Any]]:
        """Асинхронный пинг пакета IP адресов"""
        if not ip_addresses:
            return []
        
        # Ограничиваем количество потоков разумными пределами
        actual_threads = min(self.max_threads, len(ip_addresses), 200)
        
        logger.info(f"Starting async ping for {len(ip_addresses)} addresses using {actual_threads} threads")
        
        results = []
        start_time = time.time()
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=actual_threads) as executor:
                # Создаем future для каждого IP
                future_to_ip = {
                    executor.submit(self.ping_single_address, ip): ip 
                    for ip in ip_addresses
                }
                
                # Собираем результаты
                for future in concurrent.futures.as_completed(future_to_ip, timeout=30):
                    ip_address = future_to_ip[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error processing result for {ip_address}: {str(e)}")
                        results.append({
                            'ip_address': ip_address,
                            'status': 'error',
                            'response_time': None,
                            'error_message': f"Thread error: {str(e)}",
                            'timestamp': datetime.utcnow()
                        })
                        
        except concurrent.futures.TimeoutError:
            logger.warning(f"Timeout during async ping of {len(ip_addresses)} addresses")
            # Добавляем результаты для IP, которые не успели обработаться
            processed_ips = {result['ip_address'] for result in results}
            for ip in ip_addresses:
                if ip not in processed_ips:
                    results.append({
                        'ip_address': ip,
                        'status': 'error',
                        'response_time': None,
                        'error_message': 'Timeout during async ping',
                        'timestamp': datetime.utcnow()
                    })
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Async ping completed in {duration:.2f}s for {len(results)} addresses")
        
        return results
    
    def ping_all_async(self, ip_addresses: List[str], progress_callback=None) -> List[Dict[str, Any]]:
        """Асинхронный пинг всех IP адресов с разбивкой на пакеты"""
        if not ip_addresses:
            return []
        
        # Разбиваем на пакеты для оптимизации памяти и контроля
        batches = [
            ip_addresses[i:i + self.batch_size] 
            for i in range(0, len(ip_addresses), self.batch_size)
        ]
        
        logger.info(f"Processing {len(ip_addresses)} addresses in {len(batches)} batches")
        
        all_results = []
        total_start_time = time.time()
        
        for batch_num, batch in enumerate(batches, 1):
            logger.info(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} addresses)")
            
            batch_results = self.ping_batch_async(batch)
            all_results.extend(batch_results)
            
            # Вызываем callback для обновления прогресса
            if progress_callback:
                progress = (batch_num / len(batches)) * 100
                progress_callback(progress, batch_num, len(batches))
            
            # Небольшая пауза между пакетами для снижения нагрузки
            if batch_num < len(batches):
                time.sleep(0.1)
        
        total_duration = time.time() - total_start_time
        
        # Статистика
        success_count = sum(1 for r in all_results if r['status'] == 'up')
        failed_count = sum(1 for r in all_results if r['status'] == 'down')
        error_count = sum(1 for r in all_results if r['status'] == 'error')
        
        logger.info(f"Async ping completed: {len(all_results)} total, "
                   f"{success_count} up, {failed_count} down, {error_count} errors "
                   f"in {total_duration:.2f}s")
        
        return all_results
    
    def update_settings(self, max_threads: int, batch_size: int):
        """Обновление настроек сервиса"""
        with self._lock:
            # Ограничиваем разумными пределами
            self.max_threads = max(1, min(max_threads, 200))
            self.batch_size = max(10, min(batch_size, 1000))
            
        logger.info(f"Updated async ping settings: max_threads={self.max_threads}, "
                   f"batch_size={self.batch_size}")
    
    def get_recommended_settings(self, address_count: int) -> Dict[str, int]:
        """Получение рекомендуемых настроек для количества адресов"""
        if address_count <= 50:
            return {'max_threads': 20, 'batch_size': 50}
        elif address_count <= 200:
            return {'max_threads': 30, 'batch_size': 100}
        elif address_count <= 500:
            return {'max_threads': 50, 'batch_size': 100}
        elif address_count <= 1000:
            return {'max_threads': 75, 'batch_size': 200}
        elif address_count <= 5000:
            return {'max_threads': 100, 'batch_size': 500}
        else:
            return {'max_threads': 150, 'batch_size': 1000}