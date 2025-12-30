@echo off
echo Building Telescraper EXE...
rmdir /s /q build dist
py -m PyInstaller TelegramForwarder.spec
echo Build complete. The executable is in the 'dist' folder.
pause
