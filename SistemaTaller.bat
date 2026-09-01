@echo off
title Servidor CRM Taller
cd /d "%~dp0"

:: Asegura que Python reconozca la raiz del proyecto para las importaciones
set PYTHONPATH=%~dp0

echo ===================================================
echo   Iniciando el Sistema de Inventario...
echo   No cierre esta ventana mientras use el sistema.
echo ===================================================
echo.

:: 1. Migraciones automaticas de base de datos
.\python_env\python.exe manage.py migrate --noinput

:: 2. Iniciar el servidor de produccion Waitress
.\python_env\python.exe -m waitress --host=0.0.0.0 --port=8000 config.wsgi.application

pause
