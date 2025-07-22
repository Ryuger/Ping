#!/usr/bin/env python3
"""
Генератор криптографически стойких ключей для сетевого монитора
"""

import secrets
import string
import os
from datetime import datetime

def generate_session_key(length=64):
    """Генерирует надежный ключ для сессий"""
    alphabet = string.ascii_letters + string.digits + '_-'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secret_key(length=32):
    """Генерирует секретный ключ в hex формате"""
    return secrets.token_hex(length)

def generate_database_password(length=16):
    """Генерирует надежный пароль для базы данных"""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file():
    """Создает файл .env с новыми ключами"""
    session_key = generate_session_key()
    secret_key = generate_secret_key()
    db_password = generate_database_password()
    
    env_content = f"""# Network Monitor - Environment Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Database Configuration
DATABASE_URL=sqlite:///network_monitor.db
# For PostgreSQL: postgresql://username:{db_password}@localhost/network_monitor

# Security Keys
SESSION_SECRET={session_key}
SECRET_KEY={secret_key}

# Flask Settings
FLASK_ENV=development
FLASK_DEBUG=true

# Application Settings
APP_PORT=8247

# Optional: Database Password (for PostgreSQL)
DB_PASSWORD={db_password}

# Optional: JWT Secret (for API tokens)
JWT_SECRET={generate_secret_key()}

# Note: Keep this file secure and never commit it to version control!
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    return {
        'session_key': session_key,
        'secret_key': secret_key,
        'db_password': db_password
    }

def main():
    """Основная функция"""
    print("=" * 60)
    print("🔐 ГЕНЕРАТОР КЛЮЧЕЙ БЕЗОПАСНОСТИ")
    print("=" * 60)
    
    # Проверяем существование файла .env
    if os.path.exists('.env'):
        response = input("Файл .env уже существует. Перезаписать? (y/N): ")
        if response.lower() != 'y':
            print("❌ Операция отменена")
            return
    
    # Генерируем ключи
    print("🔧 Генерация новых ключей...")
    keys = create_env_file()
    
    print("✅ Файл .env создан с новыми ключами")
    print("=" * 60)
    print("🔑 СГЕНЕРИРОВАННЫЕ КЛЮЧИ:")
    print("=" * 60)
    print(f"Session Key: {keys['session_key'][:20]}...")
    print(f"Secret Key:  {keys['secret_key'][:20]}...")
    print(f"DB Password: {keys['db_password']}")
    print("=" * 60)
    print("⚠️  ВАЖНО:")
    print("• Сохраните эти ключи в безопасном месте")
    print("• Никогда не публикуйте их в открытом доступе")
    print("• Не добавляйте .env файл в систему контроля версий")
    print("• Используйте разные ключи для разработки и продакшена")
    print("=" * 60)
    
    # Создаем .gitignore если его нет
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write("# Environment files\n.env\n.env.local\n.env.production\n")
        print("✅ Создан .gitignore файл")

if __name__ == "__main__":
    main()