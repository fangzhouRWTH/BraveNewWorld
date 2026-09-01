@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
if defined BNW_PYTHON (
  "%BNW_PYTHON%" "%SCRIPT_DIR%Scripts\BraveNewWorld.py" %*
) else (
  py -3 "%SCRIPT_DIR%Scripts\BraveNewWorld.py" %*
)
exit /b %ERRORLEVEL%
