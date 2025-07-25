# Сетевой Монитор

Приложение для мониторинга сетевых устройств с веб-интерфейсом, системой аутентификации и автоматическим пингом.

## Возможности

- 🌐 Мониторинг IP адресов через ICMP ping
- 🔐 Система аутентификации с ролями пользователей
- 📊 Веб-интерфейс с real-time обновлениями
- 📝 Логирование всех ping операций
- 📄 Экспорт данных в Excel
- 🔒 Принудительная смена пароля при первом входе
- 🚀 Многопоточный async ping для высокой производительности

## Локальный запуск

### Для Windows:

1. **Простой способ**: Запустите `start_monitor.bat`
2. **Или вручную**:
   ```cmd
   pip install flask flask-sqlalchemy flask-login flask-socketio ping3 netifaces apscheduler flask-wtf werkzeug openpyxl flask-bcrypt pyjwt
   python start_local.py
   ```

### Для Linux/macOS:

```bash
pip install flask flask-sqlalchemy flask-login flask-socketio ping3 netifaces apscheduler flask-wtf werkzeug openpyxl flask-bcrypt pyjwt
python start_local.py
```

### Выбор сетевого интерфейса:

При запуске вы сможете выбрать:
- **Конкретный интерфейс** (например, 192.168.1.100) - приложение будет доступно только в этой сети
- **Все интерфейсы** (0.0.0.0) - приложение будет доступно через любой IP вашего компьютера

## Первый запуск

1. Запустите приложение
2. Откройте браузер и перейдите по адресу: `http://localhost:8247`
3. Войдите с логином: `admin`, пароль: `admin123`
4. Система потребует сменить пароль по умолчанию

## Требования к новому паролю

- Минимум 8 символов
- Содержит заглавные буквы (A-Z)
- Содержит строчные буквы (a-z)
- Содержит цифры (0-9)

## Архитектура

### Технологии:
- **Backend**: Flask + SQLAlchemy + SocketIO
- **Frontend**: Bootstrap 5 + Vanilla JavaScript
- **База данных**: SQLite (локально) / PostgreSQL (продакшен)
- **Аутентификация**: Flask-Login + Flask-Bcrypt
- **Планировщик**: APScheduler

### Структура проекта:
```
├── app.py              # Главный файл приложения
├── main.py             # Точка входа для Replit
├── start_local.py      # Скрипт для локального запуска
├── start_monitor.bat   # Batch-файл для Windows
├── models.py           # Модели базы данных
├── routes.py           # Маршруты веб-приложения
├── auth_forms.py       # Формы аутентификации
├── auth_decorators.py  # Декораторы для авторизации
├── services/           # Бизнес-логика
│   ├── network_service.py
│   ├── async_ping_service.py
│   └── ping_scheduler.py
├── templates/          # HTML шаблоны
└── static/            # CSS, JS, изображения
```

## Безопасность

- Использование нестандартного порта (8247)
- Принудительная смена пароля по умолчанию
- Хеширование паролей с помощью bcrypt
- Сессии с защищенными cookie
- Аудит всех действий пользователей
- Криптографически стойкие ключи сессий
- Генератор новых ключей безопасности

### Генерация новых ключей:
```bash
python generate_keys.py
```

Этот скрипт создает файл `.env` с новыми криптографически стойкими ключами для максимальной безопасности.

## Развертывание

### Replit:
Приложение готово к работе в Replit без дополнительных настроек.

### Локальное развертывание:
1. Клонируйте репозиторий
2. Установите зависимости: `pip install -r requirements.txt`
3. Запустите: `python start_local.py`

### Продакшен:
1. Настройте PostgreSQL
2. Установите переменные окружения
3. Используйте gunicorn для запуска

## Переменные окружения

- `DATABASE_URL` - URL подключения к базе данных
- `SESSION_SECRET` - Секретный ключ для сессий
- `FLASK_ENV` - Окружение Flask (development/production)
- `APP_PORT` - Порт приложения (по умолчанию 8247)

## Лицензия

MIT License

## Поддержка

При возникновении проблем:
1. Проверьте, что Python установлен
2. Убедитесь, что все зависимости установлены
3. Проверьте, что порт 8247 свободен
4. Запустите с правами администратора (для ping операций)