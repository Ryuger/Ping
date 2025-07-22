#!/usr/bin/env python3
"""
Скрипт для загрузки внешних ресурсов в локальные файлы
для обеспечения автономной работы приложения
"""

import os
import requests
import sys
from pathlib import Path

def download_file(url, local_path, description):
    """Загружает файл по URL в локальный путь"""
    try:
        # Создаем директорию если её нет
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Проверяем, существует ли файл
        if os.path.exists(local_path):
            print(f"✓ {description} уже существует: {local_path}")
            return True
        
        print(f"📥 Загружаю {description}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ {description} загружен: {local_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки {description}: {e}")
        return False

def download_assets():
    """Загружает все внешние ресурсы"""
    print("🔽 Загрузка внешних ресурсов для автономной работы...")
    print("=" * 60)
    
    # Список ресурсов для загрузки
    assets = [
        {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css',
            'path': 'static/css/bootstrap.min.css',
            'description': 'Bootstrap CSS'
        },
        {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
            'path': 'static/css/fontawesome.min.css',
            'description': 'Font Awesome CSS'
        },
        {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js',
            'path': 'static/js/bootstrap.bundle.min.js',
            'description': 'Bootstrap JavaScript'
        },
        {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js',
            'path': 'static/js/socket.io.js',
            'description': 'Socket.IO JavaScript'
        },
        {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.woff2',
            'path': 'static/fonts/fa-solid-900.woff2',
            'description': 'Font Awesome Solid WOFF2'
        },
        {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-regular-400.woff2',
            'path': 'static/fonts/fa-regular-400.woff2',
            'description': 'Font Awesome Regular WOFF2'
        },
        {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-brands-400.woff2',
            'path': 'static/fonts/fa-brands-400.woff2',
            'description': 'Font Awesome Brands WOFF2'
        }
    ]
    
    success_count = 0
    
    for asset in assets:
        if download_file(asset['url'], asset['path'], asset['description']):
            success_count += 1
    
    # Исправляем пути к шрифтам в Font Awesome CSS
    try:
        fa_css_path = 'static/css/fontawesome.min.css'
        if os.path.exists(fa_css_path):
            print("🔧 Обновляю пути к шрифтам в Font Awesome CSS...")
            with open(fa_css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # Заменяем URL на относительные пути
            css_content = css_content.replace(
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/',
                '../fonts/'
            )
            
            with open(fa_css_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            print("✓ Пути к шрифтам обновлены")
    except Exception as e:
        print(f"⚠️ Ошибка при обновлении путей к шрифтам: {e}")
    
    print("=" * 60)
    if success_count == len(assets):
        print("✅ Все ресурсы успешно загружены!")
        print("🌐 Приложение готово к работе в автономном режиме.")
    else:
        print(f"⚠️ Загружено {success_count} из {len(assets)} ресурсов")
        print("🌐 Приложение может работать с ограниченной функциональностью")
    
    return success_count == len(assets)

def check_internet_connection():
    """Проверяет наличие интернет-соединения"""
    try:
        requests.get('https://google.com', timeout=5)
        return True
    except:
        return False

if __name__ == "__main__":
    # Проверяем интернет-соединение
    if not check_internet_connection():
        print("❌ Нет интернет-соединения. Пропускаю загрузку ресурсов.")
        print("💡 Приложение будет работать с базовой функциональностью.")
        sys.exit(0)
    
    # Загружаем ресурсы
    success = download_assets()
    
    if success:
        print("\n🚀 Можно запускать приложение!")
    else:
        print("\n⚠️ Проверьте интернет-соединение и попробуйте снова.")