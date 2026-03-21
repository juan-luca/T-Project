@echo off
echo ============================================
echo   Cyber Command Center - Instalador
echo ============================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Este script requiere permisos de administrador.
    echo Por favor, ejecuta como Administrador.
    pause
    exit /b 1
)

echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python no encontrado. Por favor instala Python 3.10+
    echo Descarga desde: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python encontrado

echo.
echo [2/6] Verificando Node.js...
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js no encontrado. Por favor instala Node.js 18+
    echo Descarga desde: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js encontrado

echo.
echo [3/6] Instalando dependencias de Python...
cd backend
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo [ADVERTENCIA] Algunas dependencias pueden requerir compiladores C++
)
cd ..

echo.
echo [4/6] Instalando dependencias de Node.js...
cd frontend
call npm install
cd ..

echo.
echo [5/6] Creando base de datos...
cd backend
python -c "from database.models import init_db; init_db()"
cd ..

echo.
echo [6/6] Instalacion completada!
echo.
echo ============================================
echo   IMPORTANTE - Herramientas Adicionales
echo ============================================
echo.
echo Para funcionalidad completa, instala:
echo.
echo 1. Npcap (requerido para captura de paquetes):
echo    https://npcap.com/
echo.
echo 2. Aircrack-ng (para auditoría WiFi):
echo    https://www.aircrack-ng.org/
echo.
echo 3. Hashcat (para cracking de contraseñas):
echo    https://hashcat.net/hashcat/
echo.
echo ============================================
echo   Cómo Ejecutar
echo ============================================
echo.
echo Ejecuta: start.bat
echo.
pause
