@echo off
chcp 65001 > nul
echo =======================================
echo Download external resources for offline work
echo =======================================
echo.

REM Create directories for resources
echo Creating directories...
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "static\fonts" mkdir static\fonts
echo + Directories created

echo.
echo Downloading Font Awesome CSS...
powershell -Command "try { Invoke-WebRequest -Uri 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css' -OutFile 'static\css\fontawesome.min.css'; echo '+ Font Awesome CSS downloaded' } catch { echo '- Error downloading Font Awesome CSS' }"

echo.
echo Downloading Font Awesome fonts...
powershell -Command "try { Invoke-WebRequest -Uri 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.woff2' -OutFile 'static\fonts\fa-solid-900.woff2'; echo '+ Font Awesome Solid WOFF2 downloaded' } catch { echo '- Error downloading Font Awesome Solid WOFF2' }"

powershell -Command "try { Invoke-WebRequest -Uri 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-regular-400.woff2' -OutFile 'static\fonts\fa-regular-400.woff2'; echo '+ Font Awesome Regular WOFF2 downloaded' } catch { echo '- Error downloading Font Awesome Regular WOFF2' }"

powershell -Command "try { Invoke-WebRequest -Uri 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-brands-400.woff2' -OutFile 'static\fonts\fa-brands-400.woff2'; echo '+ Font Awesome Brands WOFF2 downloaded' } catch { echo '- Error downloading Font Awesome Brands WOFF2' }"

echo.
echo Downloading Socket.IO...
powershell -Command "try { Invoke-WebRequest -Uri 'https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js' -OutFile 'static\js\socket.io.js'; echo '+ Socket.IO JavaScript downloaded' } catch { echo '- Error downloading Socket.IO JavaScript' }"

echo.
echo Downloading Bootstrap CSS...
powershell -Command "try { Invoke-WebRequest -Uri 'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css' -OutFile 'static\css\bootstrap.min.css'; echo '+ Bootstrap CSS downloaded' } catch { echo '- Error downloading Bootstrap CSS' }"

echo.
echo Downloading Bootstrap JavaScript...
powershell -Command "try { Invoke-WebRequest -Uri 'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js' -OutFile 'static\js\bootstrap.bundle.min.js'; echo '+ Bootstrap JavaScript downloaded' } catch { echo '- Error downloading Bootstrap JavaScript' }"

echo.
echo =======================================
echo All external resources downloaded!
echo Application ready for offline work
echo =======================================
echo.
echo Updating Font Awesome CSS for local paths...
echo Updating Font Awesome CSS...

REM Update Font Awesome CSS for local paths
powershell -Command "$css = Get-Content 'static\css\fontawesome.min.css' -Raw; $css = $css -replace 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/', '../fonts/'; Set-Content 'static\css\fontawesome.min.css' $css; echo '+ Font Awesome CSS updated for local paths'"

echo.
echo =======================================
echo All done! Application can work without internet
echo =======================================
pause