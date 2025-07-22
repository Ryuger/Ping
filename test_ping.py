#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функции пинга
"""

from services.network_service import NetworkService
import time

def test_ping():
    """Тест функции пинга"""
    service = NetworkService()
    
    test_addresses = ['1.1.1.1', '8.8.8.8', '192.168.1.1']
    
    print("Тестирование функции пинга")
    print("=" * 50)
    
    for ip in test_addresses:
        print(f"\nТестируем пинг {ip}...")
        start_time = time.time()
        result = service.ping_address(ip)
        end_time = time.time()
        
        print(f"IP: {result['ip_address']}")
        print(f"Статус: {result['status']}")
        print(f"Время ответа: {result['response_time']} мс")
        print(f"Время выполнения: {(end_time - start_time)*1000:.2f} мс")
        if result['error_message']:
            print(f"Ошибка: {result['error_message']}")
        print("-" * 30)

if __name__ == "__main__":
    test_ping()