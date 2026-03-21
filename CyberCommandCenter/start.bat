@echo off
echo ============================================
echo   Cyber Command Center - Iniciando...
echo ============================================
echo.

:: Iniciar Backend
echo [1/2] Iniciando Backend (Flask)...
cd backend
start "CyberCommandCenter-Backend" cmd /k "python app.py"
cd ..

:: Esperar un momento para que el backend inicie
timeout /t 3 /nobreak >nul

:: Iniciar Frontend
echo [2/2] Iniciando Frontend (React)...
cd frontend
start "CyberCommandCenter-Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ============================================
echo   Sistema Iniciado
echo ============================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo NOTA: Ejecuta como Administrador para 
echo       funcionalidades de red completas.
echo.
echo Presiona cualquier tecla para abrir el dashboard...
pause >nul

start http://localhost:5173
