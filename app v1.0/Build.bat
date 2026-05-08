@echo off
cls
echo Starting PyInstaller build for online-fix-luncher....

pyinstaller --onefile --windowed --name "online-fix-luncher" --icon="unnamed.ico" --add-data "unnamed.ico;." online-fix-luncher.py

echo.
echo ----------------------------------------------------------------------
echo Build attempt complete. Check the "dist" folder for online-fix-luncher.exe
echo ----------------------------------------------------------------------
pause