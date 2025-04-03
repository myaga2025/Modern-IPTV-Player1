@echo off
REM filepath: n:\iptv\build.bat
echo Installing required packages...
pip install pyinstaller pillow
pip install -r requirements.txt

echo.
echo Creating directory structure...
python create_structure.py

echo.
echo Building the application...
python build_exe.py
if %ERRORLEVEL% NEQ 0 (
    echo Build failed. Check the error messages above.
    pause
    exit /b 1
)

echo.
echo Done! Build successful. 
echo You can find the executable in the dist/Modern_IPTV_Player folder.
pause