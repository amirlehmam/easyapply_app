# Deploying EasyApply Bot Web App on Render

## Prerequisites
- A Render account (sign up at https://render.com)
- Git installed on your computer

## Deployment Steps


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
