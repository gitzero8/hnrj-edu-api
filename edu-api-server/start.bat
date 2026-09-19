@echo off
title Edu API Server
echo ============================================================
echo   Mobile Edu System API Server
echo ============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 goto noPython

if exist "venv\Scripts\python.exe" goto hasVenv

echo [1/3] Creating virtual environment...
python -m venv venv
if errorlevel 1 goto venvFail
echo [1/3] Done.
echo.

:installDeps
echo [2/3] Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip

echo   Trying Tsinghua mirror...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if not errorlevel 1 goto installOk

echo   Tsinghua failed, trying Aliyun mirror...
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
if not errorlevel 1 goto installOk

echo   Aliyun failed, trying official PyPI...
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
if not errorlevel 1 goto installOk

goto pipFail

:installOk
echo [2/3] Dependencies installed.
echo.
goto startServer

:hasVenv
echo [1/2] Virtual environment found.
call venv\Scripts\activate.bat
echo.

:startServer
echo [START] Starting server...
echo.
echo ============================================================
echo   API URL: http://127.0.0.1:5000
echo   Accounts:
echo     Freshman: 202609011001 / Demo@2026edu
echo     Senior:   202309011002 / Demo@2026edu
echo   Press Ctrl+C to stop.
echo ============================================================
echo.
python app.py
pause
exit /b 0

:noPython
echo [ERROR] Python not found. Please install Python 3.7+
echo Download: https://www.python.org/downloads/
pause
exit /b 1

:venvFail
echo [ERROR] Failed to create virtual environment.
pause
exit /b 1

:pipFail
echo [ERROR] All mirrors failed. Please check network.
echo Or run manually:
echo   pip install flask pyjwt pycryptodome requests
pause
exit /b 1
