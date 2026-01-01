@echo off
REM Setup development environment for File Organizer

echo Creating virtual environment...
python -m venv venv

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Failed to create virtual environment
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing development dependencies...
REM Use the venv's pip explicitly to be sure
venv\Scripts\pip.exe install -r requirements-dev.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo.
echo ========================================
echo Development environment setup complete!
echo ========================================
echo.
echo Virtual environment created at: venv\
echo.
echo To activate the virtual environment, run:
echo     venv\Scripts\activate.bat
echo.
echo To run tests:
echo     pytest
echo     python run_tests.py all
echo.
