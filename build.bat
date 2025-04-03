@echo off
REM filepath: f:\Modern IPTV Player\build.bat

echo Building Modern IPTV Player...
echo ============================

REM Define the Python path - using the same path you're using in your commands
set PYTHON_PATH=C:/Users/info/AppData/Local/Programs/Python/Python313/python.exe
set PIP_PATH=C:/Users/info/AppData/Local/Programs/Python/Python313/Scripts/pip.exe

REM Check if Python exists at the specified path
if not exist "%PYTHON_PATH%" (
    echo ERROR: Python executable not found at %PYTHON_PATH%
    echo Please update the PYTHON_PATH variable in this script.
    goto :error
)

echo Using Python: %PYTHON_PATH%

REM Check if pip exists at the specified path
if not exist "%PIP_PATH%" (
    echo WARNING: pip not found at the expected path. Trying to use Python's pip module instead.
    set PIP_COMMAND="%PYTHON_PATH%" -m pip
) else (
    set PIP_COMMAND="%PIP_PATH%"
)

echo.
echo Installing required packages...
%PIP_COMMAND% install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install required packages.
    goto :error
)

echo.
echo Creating directory structure...
if not exist "dist" mkdir dist
if not exist "build" mkdir build

echo.
echo Building the application...
"%PYTHON_PATH%" -m PyInstaller --clean --name "Modern IPTV Player" --icon=resources/icons/app_icon.ico --add-data "resources;resources" --noconsole --onedir main.py
if %ERRORLEVEL% neq 0 (
    echo PyInstaller build failed.
    goto :error
)

echo.
echo Copying additional files...
xcopy /E /I /Y "resources" "dist\Modern IPTV Player\resources"
if %ERRORLEVEL% neq 0 (
    echo Failed to copy resources folder.
    goto :error
)

echo.
echo Cleaning up...
rmdir /S /Q build
del "Modern IPTV Player.spec"

echo.
echo Build completed successfully!
echo The executable is located in: dist\Modern IPTV Player\Modern IPTV Player.exe
goto :end

:error
echo.
echo Build failed. Check the error messages above.
pause
exit /b 1

:end
echo.
echo Build process finished.
pause
exit /b 0