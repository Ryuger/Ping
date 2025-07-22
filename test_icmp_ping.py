#!/usr/bin/env python3
"""
Тестовый скрипт для проверки ICMP пингов через ping3
"""

from ping3 import ping
import sys

def test_icmp_ping(host):
    """Тест ICMP пинга для указанного хоста"""
    print(f"Тестирование ICMP пинга для {host}...")
    
    try:
        response_time = ping(host, timeout=3, unit='ms')
        
        if response_time is not None:
            print(f"✓ Хост {host} доступен, время отклика: {response_time:.2f}ms")
            return True
        else:
            print(f"✗ Хост {host} недоступен (нет ICMP ответа)")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка при пинге {host}: {str(e)}")
        return False

def main():
    """Основная функция для тестирования"""
    test_hosts = [
        "8.8.8.8",      # Google DNS
        "1.1.1.1",      # Cloudflare DNS
        "127.0.0.1",    # localhost
        "192.168.1.1",  # типичный роутер
        "10.0.0.1"      # еще один типичный роутер
    ]
    
    print("=== Тестирование ICMP пингов через ping3 ===")
    print("Примечание: Для ICMP пингов может потребоваться sudo")
    print()
    
    success_count = 0
    total_count = len(test_hosts)
    
    for host in test_hosts:
        if test_icmp_ping(host):
            success_count += 1
        print()
    
    print(f"Результат: {success_count}/{total_count} хостов доступны")
    
    if success_count == 0:
        print("\n⚠️  Все пинги неудачны. Возможные причины:")
        print("   - Нет прав на ICMP сокеты (попробуйте запустить с sudo)")
        print("   - Фаервол блокирует ICMP")
        print("   - Проблемы с сетью")
        print("\nПопробуйте запустить:")
        print("sudo python3 test_icmp_ping.py")

if __name__ == "__main__":
    main()