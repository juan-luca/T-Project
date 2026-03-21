@echo off
echo Deteniendo Cyber Command Center...

taskkill /FI "WINDOWTITLE eq CyberCommandCenter-Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq CyberCommandCenter-Frontend*" /F >nul 2>&1

echo Servicios detenidos.
pause
