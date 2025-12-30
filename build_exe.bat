@echo off
echo Building Telescraper EXE...
rmdir /s /q build dist
py -m PyInstaller Telescraper.spec
echo Build complete. The executable is in the 'dist' folder.
pause
