@echo off
cd /d "%~dp0"
cls
echo [1/2] Building Optimized Release...
cargo build --release
echo [2/2] Exporting Executable...
if not exist "Output" mkdir "Output"
copy target\release\afandi_launcher.exe Output\AfandiLauncher.exe
echo.
echo ===================================
echo DONE! Files located in Output folder
echo ===================================
pause