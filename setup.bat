@echo off
REM Windows Setup Script

echo Installing IAM Automation Platform...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+ from python.org
    exit /b 1
)

REM Create venv
echo Creating virtual environment...
python -m venv venv

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install packages
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ Installation complete!
echo.
echo To start:
echo   1. Run: venv\Scripts\activate.bat
echo   2. Run: streamlit run app.py
echo.
echo Browser will open to http://localhost:8501
pause
