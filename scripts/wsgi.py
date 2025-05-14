import sys
import os

# Add your project directory to the sys.path
path = os.path.expanduser('~/easyapply_app')
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Import your app from app.py
from app import app as application
