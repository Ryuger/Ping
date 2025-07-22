import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize SocketIO with better configuration
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', 
                   engineio_logger=False, socketio_logger=False,
                   ping_timeout=60, ping_interval=25)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# WebSocket event handlers for room management
@socketio.on('connect')
def handle_connect(auth):
    """Handle WebSocket connection"""
    from flask_login import current_user
    if current_user.is_authenticated:
        # Join role-specific room
        join_room(current_user.role.value)
        # Join personal room
        join_room(f'user_{current_user.id}')
        logging.info(f"User {current_user.username} connected to WebSocket")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    from flask_login import current_user
    if current_user.is_authenticated:
        # Leave role-specific room
        leave_room(current_user.role.value)
        # Leave personal room
        leave_room(f'user_{current_user.id}')
        logging.info(f"User {current_user.username} disconnected from WebSocket")

# Configure the database - use PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    import routes  # noqa: F401
    
    # Download external assets if not present
    try:
        from download_assets import download_assets
        download_assets()
    except Exception as e:
        print(f"⚠️ Не удалось загрузить внешние ресурсы: {e}")
        print("💡 Приложение будет работать с базовой функциональностью")
    
    # Initialize IP filter
    from middleware.ip_filter import init_ip_filter
    init_ip_filter(app)
    
    try:
        db.create_all()
        logging.info("Database tables created successfully")
        
        # Создание суперадмина по умолчанию
        from models import User, UserRole
        superadmin = User.query.filter_by(username='sup').first()
        if not superadmin:
            superadmin = User(username='sup', role=UserRole.SUPERADMIN)
            superadmin.set_password('sup')
            db.session.add(superadmin)
            db.session.commit()
            logging.info("Superadmin user 'sup' created successfully")
        
    except Exception as e:
        logging.error(f"Database creation failed: {str(e)}")
    
    # Add server IP to whitelist
    try:
        from services.ip_whitelist_service import IPWhitelistService
        from services.network_service import NetworkService
        
        whitelist_service = IPWhitelistService()
        network_service = NetworkService()
        
        # Get server interfaces
        interfaces = network_service.get_network_interfaces()
        for interface in interfaces:
            if interface.get('ip_address') and interface.get('ip_address') not in ['127.0.0.1', '::1', '0.0.0.0']:
                whitelist_service.add_server_ip(interface['ip_address'])
                logging.info(f"Added server IP {interface['ip_address']} to whitelist")
    except Exception as e:
        logging.error(f"Failed to add server IP to whitelist: {str(e)}")
    
    # Start the ping scheduler
    try:
        from services.ping_scheduler import start_scheduler
        start_scheduler()
        logging.info("Ping scheduler started successfully")
    except Exception as e:
        logging.error(f"Scheduler start failed: {str(e)}")

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Страница не найдена - Network Monitor</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f8f9fa;
                color: #343a40;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .error-container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 500px;
                width: 100%;
            }
            .error-code {
                font-size: 72px;
                font-weight: bold;
                color: #dc3545;
                margin: 0;
                line-height: 1;
            }
            .error-title {
                font-size: 24px;
                margin: 20px 0 10px 0;
                color: #343a40;
            }
            .error-message {
                color: #6c757d;
                margin-bottom: 30px;
                line-height: 1.5;
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 500;
                transition: background-color 0.2s;
            }
            .btn:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="error-code">404</div>
            <h1 class="error-title">Страница не найдена</h1>
            <p class="error-message">
                Запрашиваемая страница не существует или была перемещена.
            </p>
            <a href="/" class="btn">Вернуться на главную</a>
        </div>
    </body>
    </html>
    ''', 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Внутренняя ошибка сервера - Network Monitor</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f8f9fa;
                color: #343a40;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .error-container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 500px;
                width: 100%;
            }
            .error-code {
                font-size: 72px;
                font-weight: bold;
                color: #dc3545;
                margin: 0;
                line-height: 1;
            }
            .error-title {
                font-size: 24px;
                margin: 20px 0 10px 0;
                color: #343a40;
            }
            .error-message {
                color: #6c757d;
                margin-bottom: 30px;
                line-height: 1.5;
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 500;
                transition: background-color 0.2s;
                margin: 0 10px;
            }
            .btn:hover {
                background-color: #0056b3;
            }
            .btn-secondary {
                background-color: #6c757d;
            }
            .btn-secondary:hover {
                background-color: #545b62;
            }
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="error-code">500</div>
            <h1 class="error-title">Внутренняя ошибка сервера</h1>
            <p class="error-message">
                Произошла ошибка на сервере. Пожалуйста, попробуйте позже или обратитесь к администратору.
            </p>
            <a href="/" class="btn">Вернуться на главную</a>
            <a href="javascript:history.back()" class="btn btn-secondary">Назад</a>
        </div>
    </body>
    </html>
    ''', 500

@app.errorhandler(403)
def forbidden_error(error):
    from flask import request
    client_ip = request.remote_addr
    return f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Доступ запрещён - Network Monitor</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f8f9fa;
                color: #343a40;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }}
            .error-container {{
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 500px;
                width: 100%;
            }}
            .error-code {{
                font-size: 72px;
                font-weight: bold;
                color: #ffc107;
                margin: 0;
                line-height: 1;
            }}
            .error-title {{
                font-size: 24px;
                margin: 20px 0 10px 0;
                color: #343a40;
            }}
            .error-message {{
                color: #6c757d;
                margin-bottom: 30px;
                line-height: 1.5;
            }}
            .error-details {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                color: #495057;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 500;
                transition: background-color 0.2s;
            }}
            .btn:hover {{
                background-color: #0056b3;
            }}
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="error-code">403</div>
            <h1 class="error-title">Доступ запрещён</h1>
            <p class="error-message">
                У вас нет прав для доступа к этой странице. Ваш IP-адрес не находится в белом списке.
            </p>
            <div class="error-details">
                Ваш IP-адрес: {client_ip}
            </div>
            <a href="javascript:history.back()" class="btn">Назад</a>
        </div>
    </body>
    </html>
    ''', 403

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {str(e)}")
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Произошла ошибка - Network Monitor</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f8f9fa;
                color: #343a40;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .error-container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 500px;
                width: 100%;
            }
            .error-code {
                font-size: 72px;
                font-weight: bold;
                color: #dc3545;
                margin: 0;
                line-height: 1;
            }
            .error-title {
                font-size: 24px;
                margin: 20px 0 10px 0;
                color: #343a40;
            }
            .error-message {
                color: #6c757d;
                margin-bottom: 30px;
                line-height: 1.5;
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 500;
                transition: background-color 0.2s;
                margin: 0 10px;
            }
            .btn:hover {
                background-color: #0056b3;
            }
            .btn-secondary {
                background-color: #6c757d;
            }
            .btn-secondary:hover {
                background-color: #545b62;
            }
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="error-code">⚠️</div>
            <h1 class="error-title">Произошла ошибка</h1>
            <p class="error-message">
                Что-то пошло не так. Пожалуйста, попробуйте ещё раз или обратитесь к администратору.
            </p>
            <a href="/" class="btn">Вернуться на главную</a>
            <a href="javascript:history.back()" class="btn btn-secondary">Назад</a>
        </div>
    </body>
    </html>
    ''', 500
