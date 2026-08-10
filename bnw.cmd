@echo off
setlocal
set "BNW_ROOT=%~dp0"

if exist "%BNW_ROOT%.venv\Scripts\python.exe" goto venv

where py >nul 2>nul
if not errorlevel 1 goto py_launcher

python "%BNW_ROOT%bnw" %*
exit /b %errorlevel%

:venv
"%BNW_ROOT%.venv\Scripts\python.exe" "%BNW_ROOT%bnw" %*
exit /b %errorlevel%

:py_launcher
py -3 "%BNW_ROOT%bnw" %*
exit /b %errorlevel%
