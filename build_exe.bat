@echo off
echo Building Telegram Forwarder EXE...
rmdir /s /q build dist
py -m PyInstaller TelegramForwarder.spec
echo Build complete. The executable is in the 'dist' folder.
pause
