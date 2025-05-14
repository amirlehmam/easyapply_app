@echo off
setlocal

REM --- Check for Python ---
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed.
    echo Please download and install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM --- Create venv if not exists ---
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment!
        pause
        exit /b 1
    )
)

REM --- Upgrade pip and install requirements ---
echo Installing dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo requirements.txt not found!
    pause
    exit /b 1
)

REM --- Start HTTP server for logs and log_viewer.html ---
start "Server" cmd /k venv\Scripts\python -m http.server 8000

REM --- Wait for server to start ---
timeout /t 3 >nul

REM --- Open log viewer in default browser ---
start "" http://localhost:8000/log_viewer.html

REM --- Run the bot ---
echo Starting the EasyApply bot...
python main.py

REM --- Keep window open on error ---
if %errorlevel% neq 0 (
    echo The bot exited with an error.
    pause
)

echo All done! You can view logs at http://localhost:8000/log_viewer.html
endlocal