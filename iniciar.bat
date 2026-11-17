@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"

set "PORT=%~1"
if "%PORT%"=="" set "PORT=8000"

echo %PORT%| findstr /R /C:"^[0-9][0-9]*$" >nul
if errorlevel 1 (
  echo [ERROR] El puerto debe ser un numero. Ejemplo: iniciar.bat 8000
  goto :error
)

call :main
if errorlevel 1 goto :error
goto :end

:main
set "PY_DIR=%~dp0python-env"
set "PY_EXE=%PY_DIR%\python.exe"

set "GTK3_DIR=%PY_DIR%\gtk3"
set "WEASYPRINT_DLL_DIRECTORIES=%GTK3_DIR%\bin"
set "FONTCONFIG_PATH=%GTK3_DIR%\etc\fonts"
set "PATH=%GTK3_DIR%\bin;%PATH%"

if not exist "%PY_EXE%" (
  where python >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] No se encontro Python embebido ni Python en PATH.
    echo Instala Python 3.11.9 o superior y agrega "python" al PATH,
    echo o instala Python embebido en "python-env".
    exit /b 1
  )
  set "PY_EXE=python"
  echo Python embebido no encontrado; usando Python del PATH.
)

call :check_port
if errorlevel 1 exit /b 1

"%PY_EXE%" -c "import django, rest_framework, rest_framework_simplejwt, sentry_sdk" >nul 2>&1
if errorlevel 1 (
  echo [ERROR] A la instalacion de Python seleccionada le faltan dependencias.
  echo Ejecuta:
  echo   "%PY_EXE%" -m pip install -r requirements.txt
  exit /b 1
)

if not exist "%~dp0.env" (
  echo Generando archivo .env...
  "%PY_EXE%" -c "import secrets; open('.env','w',encoding='utf-8').write('SECRET_KEY='+secrets.token_urlsafe(50)+'\n')"
  if errorlevel 1 (
    echo [ERROR] No se pudo generar el archivo .env.
    exit /b 1
  )
)

echo Generando migraciones...
"%PY_EXE%" manage.py makemigrations inventario usuarios --noinput
if errorlevel 1 (
  echo [ERROR] No se pudieron generar las migraciones.
  exit /b 1
)

echo Aplicando migraciones...
"%PY_EXE%" manage.py migrate --noinput
if errorlevel 1 (
  echo [ERROR] No se pudieron aplicar las migraciones.
  exit /b 1
)

echo Abriendo http://127.0.0.1:%PORT%/
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:%PORT%/"

echo Servidor corriendo en http://127.0.0.1:%PORT%/
echo Presiona Ctrl+C para detenerlo.
"%PY_EXE%" manage.py runserver --noreload 0.0.0.0:%PORT%
if errorlevel 1 exit /b 1
exit /b 0

:check_port
netstat -ano | findstr /I /C:":%PORT% " | findstr /I "LISTENING ESCUCHANDO" >nul
if not errorlevel 1 (
  echo [ERROR] El puerto %PORT% ya esta en uso.
  echo Cierra el programa que lo usa o ejecuta: iniciar.bat 8001
  exit /b 1
)
exit /b 0

:error
echo.
echo [ERROR] El proyecto no pudo iniciarse. Revisa los mensajes de arriba.
pause
exit /b 1

:end
echo.
echo Servidor detenido.
pause
endlocal
