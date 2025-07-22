from functools import wraps
from flask import redirect, url_for, flash, request, abort
from flask_login import current_user
from models import UserRole, AuditLog

def login_required_with_role(required_role):
    """Декоратор для проверки роли пользователя"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            if current_user.is_locked():
                flash('Ваш аккаунт заблокирован. Обратитесь к администратору.', 'error')
                return redirect(url_for('login'))
            
            if not current_user.is_active:
                flash('Ваш аккаунт деактивирован. Обратитесь к администратору.', 'error')
                return redirect(url_for('login'))
            
            if not current_user.has_permission(required_role):
                flash('У вас нет доступа к этой странице.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def viewer_required(f):
    """Декоратор для роли "только просмотр" и выше"""
    return login_required_with_role(UserRole.VIEWER)(f)

def user_required(f):
    """Декоратор для роли "пользователь" и выше"""
    return login_required_with_role(UserRole.USER)(f)

def admin_required(f):
    """Декоратор для роли "администратор" и выше"""
    return login_required_with_role(UserRole.ADMIN)(f)

def superadmin_required(f):
    """Декоратор для роли "суперадмин" """
    return login_required_with_role(UserRole.SUPERADMIN)(f)

def audit_log(action):
    """Декоратор для логирования действий пользователей"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Выполнение функции
            result = f(*args, **kwargs)
            
            # Логирование действия только если пользователь аутентифицирован
            try:
                from flask_login import current_user
                from flask import request
                
                if current_user and current_user.is_authenticated:
                    user_id = current_user.id
                    ip_address = request.remote_addr
                    user_agent = request.headers.get('User-Agent', '')
                    
                    AuditLog.log_action(
                        action=action,
                        user_id=user_id,
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
            except:
                pass  # Игнорировать ошибки логирования
            
            return result
        return decorated_function
    return decorator

def rate_limit(max_attempts=5, window_minutes=15):
    """Декоратор для ограничения частоты запросов"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Базовая проверка rate limiting на основе IP
            ip_address = request.remote_addr
            
            # Здесь можно добавить более сложную логику rate limiting
            # Пока что просто проверим блокировку пользователя
            if current_user.is_authenticated and current_user.is_locked():
                flash('Слишком много неудачных попыток входа. Попробуйте позже.', 'error')
                return redirect(url_for('login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator