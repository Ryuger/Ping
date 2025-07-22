# Автономная работа приложения

## Описание

Приложение Network Monitor может работать полностью автономно, без подключения к интернету во время работы. Все внешние ресурсы загружаются один раз при первом запуске или могут быть загружены заранее с помощью специальных скриптов.

## Внешние ресурсы

Приложение использует следующие внешние ресурсы:

1. **Bootstrap CSS** - Фреймворк для стилизации интерфейса
2. **Bootstrap JavaScript** - JavaScript компоненты Bootstrap
3. **Font Awesome CSS** - Иконки для интерфейса
4. **Font Awesome Fonts** - Шрифты для иконок (WOFF2 формат)
5. **Socket.IO JavaScript** - WebSocket соединения для real-time обновлений

## Способы загрузки ресурсов

### 1. Автоматическая загрузка при запуске

При первом запуске приложения все ресурсы будут автоматически загружены:

```bash
python main.py
```

### 2. Ручная загрузка с помощью Python скрипта

```bash
python download_assets.py
```

### 3. Загрузка с помощью Windows batch файлов

#### Вариант 1: Полный batch файл (PowerShell)
```batch
download_external_resources.bat
```

#### Вариант 2: Простой batch файл (Python)
```batch
download_resources.cmd
```

## Структура файлов

После загрузки ресурсов будет создана следующая структура:

```
static/
├── css/
│   ├── bootstrap.min.css      # Bootstrap CSS
│   ├── fontawesome.min.css    # Font Awesome CSS
│   └── style.css              # Пользовательские стили
├── js/
│   ├── bootstrap.bundle.min.js # Bootstrap JavaScript
│   ├── socket.io.js           # Socket.IO JavaScript
│   └── app.js                 # Пользовательский JavaScript
└── fonts/
    ├── fa-solid-900.woff2     # Font Awesome Solid шрифты
    ├── fa-regular-400.woff2   # Font Awesome Regular шрифты
    └── fa-brands-400.woff2    # Font Awesome Brands шрифты
```

## Fallback система

Если локальные файлы недоступны, приложение автоматически переключается на CDN:

- Bootstrap CSS: `https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css`
- Font Awesome: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css`
- Socket.IO: `https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js`

## Преимущества автономной работы

1. **Независимость от интернета** - Приложение работает в изолированных сетях
2. **Быстродействие** - Локальные файлы загружаются быстрее
3. **Надежность** - Нет зависимости от доступности внешних CDN
4. **Безопасность** - Отсутствуют внешние запросы во время работы

## Устранение неполадок

### Ошибки загрузки ресурсов

1. Проверьте интернет-соединение
2. Убедитесь, что есть права на запись в папку `static/`
3. Проверьте антивирус (может блокировать загрузку)

### Проблемы с отображением иконок

1. Убедитесь, что файлы шрифтов загружены в `static/fonts/`
2. Проверьте, что в `fontawesome.min.css` правильные пути к шрифтам
3. Перезапустите приложение после загрузки ресурсов

## Обновление ресурсов

Для обновления ресурсов до новых версий:

1. Удалите файлы из папки `static/`
2. Запустите любой из скриптов загрузки
3. Перезапустите приложение