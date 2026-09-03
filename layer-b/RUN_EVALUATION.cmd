@echo off
setlocal
call "%~dp0wisomega-eval.cmd" run --pack cases-shadow-v1 --out "%~dp0out"
if errorlevel 1 pause & exit /b %ERRORLEVEL%
echo.
echo Open: %~dp0out\report.html
pause
