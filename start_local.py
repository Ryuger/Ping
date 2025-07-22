#!/usr/bin/env python3
"""
Скрипт для локального запуска приложения с настройками для разработки
"""

import os
import sys
from pathlib import Path

# Добавляем директорию проекта в PATH
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Настройки переменных окружения для локального запуска
os.environ.setdefault('DATABASE_URL', 'sqlite:///network_monitor.db')
os.environ.setdefault('SESSION_SECRET', 'NetMon_K7x9P2mQ8vL4nR6tY3uI1oE5wZ0sA7bG9dF2hJ4kM8pN6qV3xC1yB5nU')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_DEBUG', 'true')

# Импортируем приложение после настройки окружения
try:
    from app import app, socketio
    from services.network_service import NetworkService
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("💡 Убедитесь, что установлены все зависимости:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

def select_interface():
    """Интерактивный выбор сетевого интерфейса"""
    try:
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
        
        print(f"0. Все интерфейсы (0.0.0.0) - доступ с любого IP компьютера")
        print("=" * 60)
        print("💡 Выберите конкретный интерфейс для работы только в этой сети")
        print("💡 Или выберите 0 для доступа со всех сетевых интерфейсов")
        
        while True:
            try:
                choice = input("Выберите интерфейс (0-{}): ".format(len(interfaces)))
                choice = int(choice)
                
                if choice == 0:
                    return "0.0.0.0"
                elif 1 <= choice <= len(interfaces):
                    selected_interface = interfaces[choice - 1]
                    return selected_interface['ip_address']
                else:
                    print("❌ Неверный выбор. Попробуйте снова.")
            except ValueError:
                print("❌ Введите число.")
            except KeyboardInterrupt:
                print("\n🛑 Операция отменена пользователем")
                sys.exit(0)
    except Exception as e:
        print(f"❌ Ошибка при определении интерфейсов: {e}")
        return "0.0.0.0"

def main():
    """Основная функция запуска"""
    print("=" * 60)
    print("🚀 ЛОКАЛЬНЫЙ ЗАПУСК СЕТЕВОГО МОНИТОРА")
    print("=" * 60)
    
    # Проверка зависимостей
    print("🔍 Проверка зависимостей...")
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import flask_socketio
        import ping3
        import netifaces
        print("✅ Все зависимости установлены")
    except ImportError as e:
        print(f"❌ Не установлена зависимость: {e}")
        print("💡 Установите зависимости командой:")
        print("   pip install flask flask-sqlalchemy flask-login flask-socketio ping3 netifaces apscheduler")
        sys.exit(1)
    
    # Выбор интерфейса (пользователь сам выбирает сеть)
    host_ip = select_interface()
    port = int(os.environ.get('APP_PORT', 8247))
    
    # Если выбран конкретный интерфейс, показываем его информацию
    if host_ip != "0.0.0.0":
        print(f"✅ Выбран интерфейс: {host_ip}")
        print(f"🌐 Сервер будет доступен только в этой сети")
    else:
        print("✅ Выбраны все интерфейсы")
        print("🌐 Сервер будет доступен на всех сетевых интерфейсах")
    
    print("\n" + "=" * 60)
    print("🔗 ЗАПУСК ПРИЛОЖЕНИЯ")
    print("=" * 60)
    if host_ip == "0.0.0.0":
        print(f"🌐 Доступ: http://localhost:{port}")
        print(f"🌐 Или через любой IP этого компьютера на порту {port}")
    else:
        print(f"🌐 Доступ: http://{host_ip}:{port}")
        print(f"🌐 Только для устройств в сети {host_ip}")
    print("=" * 60)
    print("📋 Функции:")
    print("   • Мониторинг IP адресов")
    print("   • Автоматический пинг")
    print("   • Логирование результатов")
    print("   • Экспорт в Excel")
    print("   • Система аутентификации")
    print("=" * 60)
    print("🔧 Для остановки нажмите Ctrl+C")
    print("=" * 60)
    
    try:
        # Создаем таблицы базы данных
        with app.app_context():
            from app import db
            db.create_all()
            print("✅ База данных инициализирована")
            
            # Создаем пользователя admin, если его нет
            from models import User, UserRole
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(username='admin', role=UserRole.ADMIN)
                admin_user.set_password('admin123')
                admin_user.force_password_change = True
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Создан пользователь admin с паролем admin123")
            
        # Запуск приложения
        socketio.run(app, host=host_ip, port=port, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")
        print(f"💡 Проверьте, что порт {port} свободен")
        sys.exit(1)

if __name__ == "__main__":
    main()