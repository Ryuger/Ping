from app import app, socketio
from services.network_service import NetworkService
from services.ip_whitelist_service import IPWhitelistService
import sys

def select_interface():
    """Интерактивный выбор сетевого интерфейса"""
    network_service = NetworkService()
    interfaces = network_service.detect_network_interfaces()
    
    if not interfaces:
        print("❌ Сетевые интерфейсы не найдены")
        return "0.0.0.0"
    
    print("\n🌐 Доступные сетевые интерфейсы:")
    print("=" * 60)
    for i, interface in enumerate(interfaces, 1):
        print(f"{i}. {interface['name']}")
        print(f"   IP: {interface['ip_address']}")
        print(f"   Подсеть: {interface['subnet']}")
        print("-" * 40)
    
    print(f"0. Использовать все интерфейсы (0.0.0.0)")
    print("=" * 60)
    
    while True:
        try:
            choice = input("Выберите интерфейс (0-{}): ".format(len(interfaces)))
            choice = int(choice)
            
            if choice == 0:
                return "0.0.0.0"
            elif 1 <= choice <= len(interfaces):
                selected_interface = interfaces[choice - 1]
                # Добавляем IP-адрес интерфейса в белый список
                whitelist_service = IPWhitelistService()
                whitelist_service.add_server_ip(selected_interface['ip_address'])
                return selected_interface['ip_address']
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
        except ValueError:
            print("❌ Введите число.")
        except KeyboardInterrupt:
            print("\n🛑 Операция отменена пользователем")
            sys.exit(0)

if __name__ == "__main__":
    # Запуск с интерактивным выбором интерфейса
    host_ip = select_interface()
    
    print("\n" + "=" * 60)
    print("🔗 ЗАПУСК СЕТЕВОГО МОНИТОРА")
    print("=" * 60)
    print(f"🌐 Сервер запущен на: http://{host_ip}:8247")
    if host_ip == "0.0.0.0":
        print("🌐 Откройте браузер и перейдите по адресу: http://localhost:8247")
    else:
        print(f"🌐 Откройте браузер и перейдите по адресу: http://{host_ip}:8247")
    print("=" * 60)
    print("📋 Функции:")
    print("   • Мониторинг IP адресов")
    print("   • Автоматический пинг каждые 30 секунд")
    print("   • Логирование результатов")
    print("   • Экспорт в Excel")
    print("   • Русский интерфейс")
    print("=" * 60)
    print("🔧 Для остановки нажмите Ctrl+C")
    print("=" * 60)
    
    try:
        socketio.run(app, host=host_ip, port=8247, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")
        print("💡 Проверьте, что порт 8247 свободен")
