#!/bin/bash

set -e

# --- Check for Python ---
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed."
    echo "Please install Python 3.10+ (e.g., via Homebrew: brew install python3) and re-run this script."
    exit 1
fi

# --- Create venv if not exists ---
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# --- Activate venv and install requirements ---
echo "Installing dependencies..."
source venv/bin/activate
python -m pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found!"
    exit 1
fi

# --- Start HTTP server for logs and log_viewer.html ---
echo "Starting HTTP server for logs at http://localhost:8000/log_viewer.html ..."
venv/bin/python -m http.server 8000 &
SERVER_PID=$!

# --- Wait for server to start ---
sleep 2

# --- Open log viewer in default browser ---
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000/log_viewer.html
elif command -v open &> /dev/null; then
    open http://localhost:8000/log_viewer.html
else
    echo "Please open http://localhost:8000/log_viewer.html in your browser."
fi

# --- Run the bot ---
echo "Starting the EasyApply bot..."
python main.py
BOT_EXIT_CODE=$?

# --- Cleanup HTTP server on exit ---
echo "Shutting down log server..."
kill $SERVER_PID 2>/dev/null || true

# --- Keep terminal open on error ---
if [ $BOT_EXIT_CODE -ne 0 ]; then
    echo "The bot exited with an error."
    read -p "Press [Enter] to close..."
fi

echo "All done! You can view logs at http://localhost:8000/log_viewer.html"