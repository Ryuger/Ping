from app import db
from datetime import datetime
from sqlalchemy import desc
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

class NetworkAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)  # IPv4 and IPv6 support
    group_name = db.Column(db.String(100), default='Основная')  # Group name for visual separation
    is_active = db.Column(db.Boolean, default=True)
    last_ping_time = db.Column(db.DateTime)
    last_status = db.Column(db.String(20), default='unknown')  # up, down, unknown
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to ping logs
    ping_logs = db.relationship('PingLog', backref='network_address', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<NetworkAddress {self.ip_address}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'group_name': self.group_name,
            'is_active': self.is_active,
            'last_ping_time': self.last_ping_time.isoformat() if self.last_ping_time else None,
            'last_status': self.last_status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    network_address_id = db.Column(db.Integer, db.ForeignKey('network_address.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # up, down, error
    response_time = db.Column(db.Float)  # in milliseconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<PingLog {self.network_address_id} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'network_address_id': self.network_address_id,
            'status': self.status,
            'response_time': self.response_time,
            'timestamp': self.timestamp.isoformat(),
            'error_message': self.error_message
        }
    
    @classmethod
    def get_status_changes(cls, network_address_id=None, limit=100):
        """Get logs where status changed from previous entry"""
        query = cls.query
        if network_address_id:
            query = query.filter_by(network_address_id=network_address_id)
        
        # Get all logs ordered by timestamp
        all_logs = query.order_by(cls.timestamp.desc()).limit(limit * 2).all()
        
        # Filter for status changes
        status_changes = []
        previous_status = None
        
        for log in reversed(all_logs):  # Process in chronological order
            if previous_status is None or log.status != previous_status:
                status_changes.append(log)
                previous_status = log.status
        
        return list(reversed(status_changes))[:limit]  # Return in reverse chronological order

class NetworkInterface(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    subnet = db.Column(db.String(50), nullable=False)
    is_selected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<NetworkInterface {self.name} - {self.ip_address}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'subnet': self.subnet,
            'is_selected': self.is_selected,
            'created_at': self.created_at.isoformat()
        }

class PingSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ping_interval = db.Column(db.Integer, default=30)  # seconds
    timeout = db.Column(db.Integer, default=5)  # seconds
    max_retries = db.Column(db.Integer, default=3)
    max_threads = db.Column(db.Integer, default=50)  # concurrent ping threads
    batch_size = db.Column(db.Integer, default=100)  # addresses per batch
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PingSettings interval={self.ping_interval}s>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'ping_interval': self.ping_interval,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'max_threads': self.max_threads,
            'batch_size': self.batch_size,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def get_current(cls):
        """Get current ping settings or create default"""
        settings = cls.query.filter_by(is_active=True).first()
        if not settings:
            settings = cls(ping_interval=30, timeout=5, max_retries=3, max_threads=50, batch_size=100)
            db.session.add(settings)
            db.session.commit()
        return settings

class UserRole(Enum):
    """Роли пользователей"""
    VIEWER = "viewer"  # Только просмотр
    USER = "user"      # Пользователь - может добавлять адреса
    ADMIN = "admin"    # Администратор - может изменять настройки
    SUPERADMIN = "superadmin"  # Суперадмин - полный доступ

class User(UserMixin, db.Model):
    """Модель пользователя с системой ролей"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    login_attempts = db.Column(db.Integer, default=0)  # Защита от брутфорса
    locked_until = db.Column(db.DateTime)  # Блокировка после неудачных попыток
    
    def __repr__(self):
        return f'<User {self.username} - {self.role.value}>'
    
    def set_password(self, password):
        """Установка пароля с хешированием"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверка пароля"""
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        """Проверка блокировки аккаунта"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def lock_account(self, minutes=30):
        """Блокировка аккаунта на указанное количество минут"""
        from datetime import timedelta
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        db.session.commit()
    
    def unlock_account(self):
        """Разблокировка аккаунта"""
        self.locked_until = None
        self.login_attempts = 0
        db.session.commit()
    
    def increment_login_attempts(self):
        """Увеличение счетчика неудачных попыток входа"""
        self.login_attempts += 1
        if self.login_attempts >= 5:  # Блокировка после 5 неудачных попыток
            self.lock_account()
        db.session.commit()
    
    def reset_login_attempts(self):
        """Сброс счетчика неудачных попыток"""
        self.login_attempts = 0
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def has_permission(self, required_role):
        """Проверка разрешений по роли"""
        role_hierarchy = {
            UserRole.VIEWER: 0,
            UserRole.USER: 1,
            UserRole.ADMIN: 2,
            UserRole.SUPERADMIN: 3
        }
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
    
    def can_view(self):
        """Может просматривать"""
        return self.has_permission(UserRole.VIEWER)
    
    def can_manage_addresses(self):
        """Может управлять адресами"""
        return self.has_permission(UserRole.USER)
    
    def can_change_settings(self):
        """Может изменять настройки"""
        return self.has_permission(UserRole.ADMIN)
    
    def can_manage_users(self):
        """Может управлять пользователями"""
        return self.has_permission(UserRole.SUPERADMIN)
    
    def can_manage_ip_whitelist(self):
        """Может управлять белым списком IP"""
        return self.has_permission(UserRole.ADMIN)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_locked': self.is_locked()
        }

class AuditLog(db.Model):
    """Журнал аудита для отслеживания действий пользователей"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action} by {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'System',
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def log_action(cls, action, user_id=None, details=None, ip_address=None, user_agent=None):
        """Создание записи в журнале аудита"""
        log_entry = cls(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
