@echo off
REM ============================================================
REM Resume Tailor Pro - Startup Script
REM ============================================================
echo.
echo ============================================================
echo   RESUME TAILOR PRO - Starting...
echo ============================================================
echo.

REM Refresh PATH to pick up newly installed tools
set "PATH=%LOCALAPPDATA%\Programs\Python\Python312\;%LOCALAPPDATA%\Programs\Python\Python312\Scripts\;%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\;%PATH%"

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Install it:
    echo   winget install Python.Python.3.12
    pause
    exit /b 1
)

REM Check pdflatex
pdflatex --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pdflatex not found! Install MiKTeX:
    echo   winget install MiKTeX.MiKTeX
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Python dependencies...
    python -m pip install -r requirements.txt
)

REM Check API keys
if "%GEMINI_API_KEY%"=="" (
    echo.
    echo [WARNING] GEMINI_API_KEY is not set.
    echo   Set it with: setx GEMINI_API_KEY "your-key-here"
    echo   Or set it in the current session: set GEMINI_API_KEY=your-key-here
    echo.
)

REM Start the app
echo Starting server...
echo.
echo   PC Local:    http://127.0.0.1:5000
echo   iPhone / LAN: Check the detected IP below (connect on same Wi-Fi)
echo.
python app.py
pause
