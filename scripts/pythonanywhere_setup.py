#!/usr/bin/env python3
"""
PythonAnywhere Setup Helper Script

This script generates a WSGI configuration file and setup instructions
for deploying the EasyApply Bot Web App on PythonAnywhere's free tier.

Usage:
    python scripts/pythonanywhere_setup.py

This will:
1. Generate a wsgi.py file required by PythonAnywhere
2. Output step-by-step instructions for setting up the app
"""

import os
from pathlib import Path

def create_wsgi_file():
    """Create a WSGI file for PythonAnywhere"""
    wsgi_content = """import sys
import os

# Add your project directory to the sys.path
path = os.path.expanduser('~/easyapply_app')
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Import your app from app.py
from app import app as application
"""
    
    with open("wsgi.py", "w") as f:
        f.write(wsgi_content)
    
    print("✅ Created wsgi.py file")

def create_setup_bash_script():
    """Create a bash script for initial setup on PythonAnywhere"""
    setup_script = """#!/bin/bash
# Setup script for EasyApply Bot Web App on PythonAnywhere
echo "Setting up EasyApply Bot Web App..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p static/css static/js templates

# Set permissions
chmod +x scripts/deploy.py

echo "Setup complete! Now configure your web app in the PythonAnywhere dashboard."
"""
    
    script_path = Path("scripts/pythonanywhere_setup.sh")
    with open(script_path, "w") as f:
        f.write(setup_script)
    
    # Make it executable
    os.chmod(script_path, 0o755)
    print("✅ Created setup bash script at scripts/pythonanywhere_setup.sh")

def print_instructions():
    """Print step-by-step instructions for PythonAnywhere setup"""
    instructions = """
=======================================================================
PYTHONANYWHERE DEPLOYMENT INSTRUCTIONS
=======================================================================

Follow these steps to deploy your EasyApply Bot Web App on PythonAnywhere:

1. Sign up for a free PythonAnywhere account at https://www.pythonanywhere.com

2. Go to the "Consoles" tab and start a new Bash console

3. Clone your repository (or upload files via the Files tab):
   git clone https://github.com/yourusername/easyapply_app.git
   cd easyapply_app

4. Run the setup script:
   bash scripts/pythonanywhere_setup.sh

5. Go to the "Web" tab and create a new web app:
   - Select "Manual configuration"
   - Choose Python 3.9 (or latest available)

6. Configure your web app:
   - Set "Source code" to: /home/yourusername/easyapply_app
   - Set "Working directory" to: /home/yourusername/easyapply_app
   - Set "WSGI configuration file" to use the wsgi.py you created

7. Edit the WSGI configuration file in the PythonAnywhere dashboard:
   - Make sure the path in the WSGI file matches your actual path
   - Save the changes

8. Go to "Virtualenv" section and enter:
   /home/yourusername/easyapply_app/venv

9. Set up scheduled tasks (optional):
   - Go to the "Tasks" tab
   - Add a new scheduled task to periodically restart your app

10. Click the "Reload" button in the Web tab

11. Your app should now be accessible at:
    http://yourusername.pythonanywhere.com

IMPORTANT NOTES:
- PythonAnywhere free tier has limitations on outbound connections
- You may need a paid account for Selenium functionality
- You can use the PythonAnywhere API to set up scheduled tasks

=======================================================================
"""
    print(instructions)

def main():
    create_wsgi_file()
    create_setup_bash_script()
    print_instructions()

if __name__ == "__main__":
    main() 