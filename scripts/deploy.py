#!/usr/bin/env python3
import os
import shutil
import subprocess
import argparse
import sys

# Supported platforms
PLATFORMS = ["render", "railway", "pythonanywhere"]

def create_required_files(platform):
    """Create platform-specific configuration files"""
    
    if platform == "render":
        # Create render.yaml file
        with open("render.yaml", "w") as f:
            f.write("""
services:
  - type: web
    name: easyapply-bot
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
""")
        print("✅ Created render.yaml")
        
    elif platform == "railway":
        # Create railway.json file
        with open("railway.json", "w") as f:
            f.write("""
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
""")
        print("✅ Created railway.json")
        
    elif platform == "pythonanywhere":
        # Create wsgi.py file for PythonAnywhere
        with open("wsgi.py", "w") as f:
            f.write("""
import sys
import os
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)
from app import app as application
""")
        print("✅ Created wsgi.py for PythonAnywhere")
    
    # Create Procfile (useful for multiple platforms)
    with open("Procfile", "w") as f:
        f.write("web: python app.py")
    print("✅ Created Procfile")

def update_requirements():
    """Update requirements.txt file to include web app dependencies"""
    required_packages = [
        "selenium",
        "pyautogui",
        "webdriver_manager",
        "PyYAML",
        "validate_email",
        "openai>=1.0.0",
        "pypdf>=3.0.0",
        "fastapi",
        "uvicorn",
        "jinja2",
        "python-multipart",
        "gunicorn",  # For production WSGI server
    ]
    
    with open("requirements.txt", "w") as f:
        f.write("\n".join(required_packages))
    
    print("✅ Updated requirements.txt")

def create_deploy_readme(platform):
    """Create a README.md file with deployment instructions"""
    
    with open("DEPLOY.md", "w") as f:
        f.write(f"""# Deploying EasyApply Bot Web App on {platform.capitalize()}

## Prerequisites
- A {platform.capitalize()} account (sign up at https://{platform}.com)
- Git installed on your computer

## Deployment Steps

""")
        
        if platform == "render":
            f.write("""
1. Create a new repository on GitHub (or GitLab/Bitbucket) and push your code.
2. Log in to your Render account.
3. Click "New" and select "Blueprint" from the dropdown menu.
4. Connect your repository.
5. Render will automatically detect the render.yaml file and set up your service.
6. Click "Apply" to start the deployment.
7. Once deployed, you can access your web app at the URL provided by Render.

### Important Notes
- The free tier has limitations and your app will spin down after inactivity.
- Your bot needs to run in a headless mode (already configured in main.py).
- You may need to install additional dependencies for Chrome to run in a Linux environment.
""")
        
        elif platform == "railway":
            f.write("""
1. Create a new repository on GitHub and push your code.
2. Log in to your Railway account.
3. Create a new project and select "Deploy from GitHub repo".
4. Connect your repository.
5. Railway will automatically detect the railway.json file and deploy your app.
6. Once deployed, you can access your web app at the URL provided by Railway.

### Important Notes
- Railway provides a generous free tier but requires a credit card for verification.
- Your bot needs to run in a headless mode (already configured in main.py).
- You may need to add environment variables through the Railway dashboard.
""")
        
        elif platform == "pythonanywhere":
            f.write("""
1. Sign up for a free PythonAnywhere account.
2. Go to the "Web" tab and add a new web app.
3. Select "Manual configuration" and choose Python 3.8.
4. Set the path to your web app: /home/yourusername/easyapply_app
5. Click on "Files" and upload your project files or clone from a repository.
6. Open a Bash console and navigate to your project directory.
7. Create a virtual environment: `python -m venv venv`
8. Activate it: `source venv/bin/activate`
9. Install requirements: `pip install -r requirements.txt`
10. Go back to the "Web" tab and:
   - Set the WSGI configuration file to point to your wsgi.py
   - Set the working directory to your project directory
   - Add an environment variable: PYTHONPATH with value /home/yourusername/easyapply_app
11. Reload your web app.

### Important Notes
- PythonAnywhere free accounts have limitations on outbound connections.
- You may need to use PythonAnywhere's Selenium wrapper or pay for a premium account to use Selenium.
- Schedule your bot to run with the PythonAnywhere task scheduler.
""")
    
    print(f"✅ Created DEPLOY.md with {platform} deployment instructions")

def main():
    parser = argparse.ArgumentParser(description="Prepare EasyApply Bot for web deployment")
    parser.add_argument("platform", choices=PLATFORMS, help="Target deployment platform")
    parser.add_argument("--skip-requirements", action="store_true", help="Skip updating requirements.txt")
    
    args = parser.parse_args()
    
    print(f"🚀 Preparing for deployment to {args.platform}...")
    
    # Create platform-specific files
    create_required_files(args.platform)
    
    # Update requirements.txt
    if not args.skip_requirements:
        update_requirements()
    
    # Create deployment instructions
    create_deploy_readme(args.platform)
    
    print(f"""
✨ Deployment preparation complete! ✨

Next steps:
1. Review the DEPLOY.md file for detailed instructions
2. Test your app locally: python app.py
3. Deploy to {args.platform} following the instructions

Good luck! 🍀
""")

if __name__ == "__main__":
    main() 