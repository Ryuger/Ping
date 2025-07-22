@echo off
echo =======================================
echo Downloading external resources...
echo =======================================
echo.

REM Create directories
echo Creating directories...
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "static\fonts" mkdir static\fonts
echo [OK] Directories created

echo.
echo Downloading Bootstrap CSS...
curl -L "https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" -o "static\css\bootstrap.min.css"
if exist "static\css\bootstrap.min.css" (echo [OK] Bootstrap CSS downloaded) else (echo [ERROR] Bootstrap CSS failed)

echo.
echo Downloading Font Awesome CSS...
curl -L "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" -o "static\css\fontawesome.min.css"
if exist "static\css\fontawesome.min.css" (echo [OK] Font Awesome CSS downloaded) else (echo [ERROR] Font Awesome CSS failed)

echo.
echo Downloading Bootstrap JavaScript...
curl -L "https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js" -o "static\js\bootstrap.bundle.min.js"
if exist "static\js\bootstrap.bundle.min.js" (echo [OK] Bootstrap JS downloaded) else (echo [ERROR] Bootstrap JS failed)

echo.
echo Downloading Socket.IO...
curl -L "https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js" -o "static\js\socket.io.js"
if exist "static\js\socket.io.js" (echo [OK] Socket.IO downloaded) else (echo [ERROR] Socket.IO failed)

echo.
echo Downloading Font Awesome fonts...
curl -L "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.woff2" -o "static\fonts\fa-solid-900.woff2"
if exist "static\fonts\fa-solid-900.woff2" (echo [OK] Solid fonts downloaded) else (echo [ERROR] Solid fonts failed)

curl -L "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-regular-400.woff2" -o "static\fonts\fa-regular-400.woff2"
if exist "static\fonts\fa-regular-400.woff2" (echo [OK] Regular fonts downloaded) else (echo [ERROR] Regular fonts failed)

curl -L "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-brands-400.woff2" -o "static\fonts\fa-brands-400.woff2"
if exist "static\fonts\fa-brands-400.woff2" (echo [OK] Brands fonts downloaded) else (echo [ERROR] Brands fonts failed)

echo.
echo Fixing Font Awesome CSS paths...
if exist "static\css\fontawesome.min.css" (
    powershell -Command "(Get-Content 'static\css\fontawesome.min.css' -Raw) -replace 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/', '../fonts/' | Set-Content 'static\css\fontawesome.min.css'"
    echo [OK] Font Awesome CSS paths updated
) else (
    echo [ERROR] Font Awesome CSS not found
)

echo.
echo =======================================
echo Download complete!
echo =======================================
echo.
echo Files downloaded:
dir static\css\*.css /b 2>nul
dir static\js\*.js /b 2>nul
dir static\fonts\*.woff2 /b 2>nul
echo.
echo Application ready for offline work!
echo =======================================
pause