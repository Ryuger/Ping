from flask import request, jsonify, abort
from functools import wraps
import logging
from services.ip_whitelist_service import IPWhitelistService

def ip_whitelist_required(f):
    """Декоратор для проверки IP-адреса в белом списке"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        whitelist_service = IPWhitelistService()
        
        # Получаем IP-адрес клиента
        client_ip = whitelist_service.get_client_ip()
        
        # Проверяем разрешен ли IP-адрес
        if not whitelist_service.is_ip_allowed(client_ip):
            logging.warning(f"Заблокирован доступ с IP-адреса: {client_ip}")
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function

def init_ip_filter(app):
    """Инициализация фильтра IP-адресов для всего приложения"""
    @app.before_request
    def check_ip_whitelist():
        whitelist_service = IPWhitelistService()
        
        # Пропускаем проверку для статических файлов
        if request.endpoint and request.endpoint.startswith('static'):
            return
        
        # Получаем IP-адрес клиента
        client_ip = whitelist_service.get_client_ip()
        
        # Проверяем разрешен ли IP-адрес
        if not whitelist_service.is_ip_allowed(client_ip):
            logging.warning(f"Заблокирован доступ с IP-адреса: {client_ip} к {request.path}")
            from flask import abort
            abort(403)