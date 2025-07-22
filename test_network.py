#!/usr/bin/env python3
"""
Тестовый скрипт для проверки определения сетевого адреса
"""

import netifaces
import socket

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Try to get the IP from default gateway interface
        gws = netifaces.gateways()
        if 'default' in gws and netifaces.AF_INET in gws['default']:
            interface = gws['default'][netifaces.AF_INET][1]
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                return addrs[netifaces.AF_INET][0]['addr']
    except:
        pass
    
    # Fallback method
    try:
        # Connect to a remote server to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def show_all_interfaces():
    """Show all network interfaces"""
    print("=== Все сетевые интерфейсы ===")
    for interface in netifaces.interfaces():
        try:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    print(f"{interface}: {addr['addr']}")
        except:
            pass

if __name__ == "__main__":
    print("Тестирование определения сетевых адресов")
    print("=" * 50)
    
    # Show all interfaces
    show_all_interfaces()
    
    print("\n=== Определение основного IP ===")
    ip = get_local_ip()
    print(f"Основной IP адрес: {ip}")
    print(f"Сервер будет запущен на: http://{ip}:5000")
    
    print("\n=== Информация о шлюзах ===")
    try:
        gws = netifaces.gateways()
        print(f"Шлюзы: {gws}")
        if 'default' in gws:
            print(f"Шлюз по умолчанию: {gws['default']}")
    except Exception as e:
        print(f"Ошибка при получении шлюзов: {e}")