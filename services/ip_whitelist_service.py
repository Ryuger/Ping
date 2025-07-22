import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from flask import request
import ipaddress

class IPWhitelistService:
    """Сервис для управления белым списком IP-адресов"""
    
    def __init__(self):
        self.config_dir = "config"
        self.whitelist_file = os.path.join(self.config_dir, "ip_whitelist.json")
        self.ensure_config_dir()
        self.ensure_whitelist_file()
    
    def ensure_config_dir(self):
        """Создание директории конфигурации если она не существует"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def ensure_whitelist_file(self):
        """Создание файла белого списка если он не существует"""
        if not os.path.exists(self.whitelist_file):
            default_config = {
                "groups": {
                    "system": {
                        "name": "Системные адреса",
                        "description": "Локальные и системные IP-адреса",
                        "addresses": [
                            "127.0.0.1",
                            "::1",
                            "0.0.0.0"
                        ],
                        "protected": True
                    }
                },
                "enabled": True,
                "last_updated": datetime.now().isoformat(),
                "updated_by": "system"
            }
            self.save_config(default_config)
    
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации белого списка"""
        try:
            with open(self.whitelist_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Ошибка загрузки конфигурации белого списка: {e}")
            return {
                "groups": {
                    "system": {
                        "name": "Системные адреса",
                        "description": "Локальные и системные IP-адреса",
                        "addresses": ["127.0.0.1", "::1", "0.0.0.0"],
                        "protected": True
                    }
                },
                "enabled": True,
                "last_updated": datetime.now().isoformat(),
                "updated_by": "system"
            }
    
    def save_config(self, config: Dict[str, Any]):
        """Сохранение конфигурации белого списка"""
        try:
            with open(self.whitelist_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Notify about file change via WebSocket
            self._notify_file_change(config)
        except Exception as e:
            logging.error(f"Ошибка сохранения конфигурации белого списка: {e}")
    
    def _notify_file_change(self, config: Dict[str, Any]):
        """Уведомление об изменении файла через WebSocket (только для суперадминов)"""
        try:
            from app import socketio
            # Отправляем уведомление только в комнату суперадминов
            socketio.emit('whitelist_file_change', {
                'config': config,
                'timestamp': datetime.now().isoformat(),
                'message': 'Файл конфигурации белого списка был изменен'
            }, room='superadmin')
        except Exception as e:
            logging.error(f"Ошибка отправки уведомления об изменении файла: {e}")
    
    def add_server_ip(self, server_ip: str):
        """Добавление IP-адреса сервера в системную группу"""
        config = self.load_config()
        
        # Обеспечиваем наличие системной группы
        if "groups" not in config:
            config["groups"] = {}
        
        if "system" not in config["groups"]:
            config["groups"]["system"] = {
                "name": "Системные адреса",
                "description": "Локальные и системные IP-адреса",
                "addresses": [],
                "protected": True
            }
        
        system_addresses = config["groups"]["system"]["addresses"]
        if server_ip not in system_addresses:
            system_addresses.append(server_ip)
            config["last_updated"] = datetime.now().isoformat()
            config["updated_by"] = "system"
            self.save_config(config)
            logging.info(f"IP-адрес сервера {server_ip} добавлен в системную группу")
    
    def get_whitelist(self) -> List[str]:
        """Получение списка разрешенных IP-адресов из всех групп"""
        config = self.load_config()
        
        # Поддержка старого формата
        if "whitelist" in config:
            return config.get("whitelist", [])
        
        # Новый формат с группами
        all_addresses = []
        groups = config.get("groups", {})
        for group_data in groups.values():
            addresses = group_data.get("addresses", [])
            all_addresses.extend(addresses)
        
        return all_addresses
    
    def get_groups(self) -> Dict[str, Any]:
        """Получение всех групп IP-адресов"""
        config = self.load_config()
        return config.get("groups", {})
    
    def is_enabled(self) -> bool:
        """Проверка включен ли белый список"""
        config = self.load_config()
        return config.get("enabled", True)
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Проверка разрешен ли IP-адрес"""
        if not self.is_enabled():
            return True
        
        whitelist = self.get_whitelist()
        
        # Проверка точного совпадения
        if ip_address in whitelist:
            return True
        
        # Проверка подсетей
        try:
            client_ip = ipaddress.ip_address(ip_address)
            for allowed_ip in whitelist:
                try:
                    # Проверка является ли адрес сетью
                    if '/' in allowed_ip:
                        network = ipaddress.ip_network(allowed_ip, strict=False)
                        if client_ip in network:
                            return True
                    else:
                        # Проверка точного совпадения
                        if client_ip == ipaddress.ip_address(allowed_ip):
                            return True
                except ValueError:
                    continue
        except ValueError:
            pass
        
        return False
    
    def add_ip(self, ip_address: str, updated_by: str = "admin") -> bool:
        """Добавление IP-адреса в белый список (в группу пользователей)"""
        try:
            # Валидация IP-адреса
            ipaddress.ip_address(ip_address)
            
            config = self.load_config()
            
            # Поддержка старого формата
            if "whitelist" in config:
                whitelist = config.get("whitelist", [])
                if ip_address not in whitelist:
                    whitelist.append(ip_address)
                    config["whitelist"] = whitelist
                    config["last_updated"] = datetime.now().isoformat()
                    config["updated_by"] = updated_by
                    self.save_config(config)
                    return True
                return False
            
            # Новый формат с группами - добавляем в группу user
            groups = config.get("groups", {})
            
            # Создаем группу пользователей если она не существует
            if "user" not in groups:
                groups["user"] = {
                    "name": "Пользовательские адреса",
                    "description": "Разрешенные пользовательские IP-адреса",
                    "addresses": [],
                    "protected": False
                }
            
            # Проверяем, что IP не существует в других группах
            for group_data in groups.values():
                if ip_address in group_data.get("addresses", []):
                    return False
            
            # Добавляем IP в пользовательскую группу
            user_addresses = groups["user"]["addresses"]
            user_addresses.append(ip_address)
            groups["user"]["addresses"] = user_addresses
            
            config["groups"] = groups
            config["last_updated"] = datetime.now().isoformat()
            config["updated_by"] = updated_by
            self.save_config(config)
            return True
            
        except ValueError:
            return False
    
    def add_server_ip(self, ip_address: str) -> bool:
        """Добавление IP-адреса сервера в системную группу"""
        try:
            # Валидация IP-адреса
            ipaddress.ip_address(ip_address)
            
            config = self.load_config()
            groups = config.get("groups", {})
            
            # Создаем системную группу если она не существует
            if "system" not in groups:
                groups["system"] = {
                    "name": "Системные адреса",
                    "description": "Защищенные системные IP-адреса",
                    "addresses": ["127.0.0.1", "::1", "0.0.0.0"],
                    "protected": True
                }
            
            # Проверяем, что IP не существует в системной группе
            system_addresses = groups["system"]["addresses"]
            if ip_address not in system_addresses:
                system_addresses.append(ip_address)
                groups["system"]["addresses"] = system_addresses
                
                config["groups"] = groups
                config["last_updated"] = datetime.now().isoformat()
                config["updated_by"] = "system"
                self.save_config(config)
                return True
            
            return False
            
        except ValueError:
            return False
    
    def remove_ip(self, ip_address: str, updated_by: str = "admin", user_role: str = "admin") -> bool:
        """Удаление IP-адреса из белого списка (из всех групп)"""
        config = self.load_config()
        
        # Поддержка старого формата
        if "whitelist" in config:
            whitelist = config.get("whitelist", [])
            if ip_address in whitelist:
                whitelist.remove(ip_address)
                config["whitelist"] = whitelist
                config["last_updated"] = datetime.now().isoformat()
                config["updated_by"] = updated_by
                self.save_config(config)
                return True
            return False
        
        # Новый формат с группами
        groups = config.get("groups", {})
        removed = False
        
        for group_name, group_data in groups.items():
            # Проверяем права доступа
            if group_data.get("protected", False) and user_role != "superadmin":
                # Обычный админ не может удалять из защищенных групп
                continue
                
            addresses = group_data.get("addresses", [])
            if ip_address in addresses:
                addresses.remove(ip_address)
                group_data["addresses"] = addresses
                removed = True
        
        if removed:
            config["groups"] = groups
            config["last_updated"] = datetime.now().isoformat()
            config["updated_by"] = updated_by
            self.save_config(config)
            return True
        
        return False
    
    def toggle_whitelist(self, enabled: bool, updated_by: str = "admin"):
        """Включение/выключение белого списка"""
        config = self.load_config()
        config["enabled"] = enabled
        config["last_updated"] = datetime.now().isoformat()
        config["updated_by"] = updated_by
        self.save_config(config)
    
    def get_client_ip(self) -> str:
        """Получение IP-адреса клиента"""
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
        elif request.environ.get('HTTP_X_REAL_IP'):
            return request.environ['HTTP_X_REAL_IP']
        else:
            return request.environ['REMOTE_ADDR']
    
    def add_ip_to_group(self, ip_address: str, group_name: str, updated_by: str = "admin") -> bool:
        """Добавление IP-адреса в указанную группу"""
        try:
            # Валидация IP-адреса
            ipaddress.ip_address(ip_address)
            
            config = self.load_config()
            groups = config.get("groups", {})
            
            if group_name not in groups:
                return False
                
            addresses = groups[group_name].get("addresses", [])
            if ip_address not in addresses:
                addresses.append(ip_address)
                groups[group_name]["addresses"] = addresses
                config["groups"] = groups
                config["last_updated"] = datetime.now().isoformat()
                config["updated_by"] = updated_by
                self.save_config(config)
                return True
            return False
        except ValueError:
            return False
    
    def remove_ip_from_group(self, ip_address: str, group_name: str, updated_by: str = "admin") -> bool:
        """Удаление IP-адреса из указанной группы"""
        config = self.load_config()
        groups = config.get("groups", {})
        
        if group_name not in groups:
            return False
            
        # Проверка защищенности группы
        if groups[group_name].get("protected", False):
            return False
            
        addresses = groups[group_name].get("addresses", [])
        if ip_address in addresses:
            addresses.remove(ip_address)
            groups[group_name]["addresses"] = addresses
            config["groups"] = groups
            config["last_updated"] = datetime.now().isoformat()
            config["updated_by"] = updated_by
            self.save_config(config)
            return True
        return False
    
    def create_group(self, group_name: str, display_name: str, description: str = "", updated_by: str = "admin") -> bool:
        """Создание новой группы IP-адресов"""
        config = self.load_config()
        groups = config.get("groups", {})
        
        if group_name in groups:
            return False
            
        groups[group_name] = {
            "name": display_name,
            "description": description,
            "addresses": [],
            "protected": False
        }
        
        config["groups"] = groups
        config["last_updated"] = datetime.now().isoformat()
        config["updated_by"] = updated_by
        self.save_config(config)
        return True
    
    def get_config_info(self) -> Dict[str, Any]:
        """Получение информации о конфигурации"""
        config = self.load_config()
        total_addresses = len(self.get_whitelist())
        
        return {
            "enabled": config.get("enabled", True),
            "whitelist_count": total_addresses,
            "groups_count": len(config.get("groups", {})),
            "last_updated": config.get("last_updated", ""),
            "updated_by": config.get("updated_by", "")
        }