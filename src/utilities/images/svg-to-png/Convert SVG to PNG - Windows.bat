@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 svg_to_png.py %*
    if errorlevel 1 pause
    exit /b
)

where python >nul 2>nul
if %errorlevel%==0 (
    python svg_to_png.py %*
    if errorlevel 1 pause
    exit /b
)

echo.
echo Python 3 is not installed or was not found.
echo Install Python from https://www.python.org/downloads/
echo During installation, check "Add Python to PATH".
echo.
pause
