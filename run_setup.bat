@echo off
call "%~dp0env_for_icons.bat"  %*
"%WINPYDIR%\python.exe" "%WINPYDIR%\cygun\start_setup.py" %*
