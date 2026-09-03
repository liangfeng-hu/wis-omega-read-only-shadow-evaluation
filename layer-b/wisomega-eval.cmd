@echo off
setlocal
python "%~dp0wisomega_eval.py" %*
exit /b %ERRORLEVEL%
