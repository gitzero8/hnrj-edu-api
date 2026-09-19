@echo off
title API Test
echo ============================================================
echo   Mobile Edu System API - Interface Test
echo ============================================================
echo.

if not exist "venv\Scripts\python.exe" goto noVenv
call venv\Scripts\activate.bat
python test_api.py
echo.
pause
exit /b 0

:noVenv
echo [ERROR] Virtual environment not found.
echo Please run start.bat first.
pause
exit /b 1
