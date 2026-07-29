@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Mode-3 Standalone Package
echo.
echo Mode-3 Multi-Loop Coupling ? standalone
echo.
where py >nul 2>nul && set PY=py -3
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo Python not found. Install Python 3.10+ and retry.
  pause
  exit /b 1
)
%PY% -c "import mode3_coupling" 2>nul
if errorlevel 1 (
  echo Installing package...
  %PY% -m pip install -e ".[dev]"
)
echo.
echo [1] demo  [2] info  [3] test  [Q] quit
set /p c=Select: 
if /I "%c%"=="1" %PY% -m mode3_coupling demo
if /I "%c%"=="2" %PY% -m mode3_coupling info
if /I "%c%"=="3" %PY% -m mode3_coupling test
if /I "%c%"=="Q" goto end
echo.
pause
:end
