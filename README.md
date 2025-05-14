# LinkedIn EasyApply Bot Web App

A web application that allows you to run the LinkedIn EasyApply Bot from anywhere through a browser interface.

## Features

- 🌐 **Web Interface**: Control the bot from any device with a web browser
- 📊 **Dashboard**: View application statistics and logs
- ⚙️ **Configuration Editor**: Edit bot settings directly in the browser
- 🚀 **Remote Operation**: Start and stop the bot remotely
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🔐 **Deployment Options**: Deploy for free on various platforms

## Prerequisites

- Python 3.7+
- Chrome browser installed (for the Selenium driver)
- A LinkedIn account
- Job search criteria

## Installation

1. Clone this repository
   ```
   git clone https://github.com/yourusername/easyapply_app.git
   cd easyapply_app
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Configure your LinkedIn credentials and job preferences by updating `config.yaml`

## Running Locally

To start the web app locally:

```
python app.py
```

Then open your browser and go to http://localhost:8000

## Web App Usage

### Dashboard Tab
- View application statistics
- Browse detailed job application logs
- Filter and search through past applications
- Export logs as CSV or JSON

### Configuration Tab
- Edit your LinkedIn credentials
- Update job search criteria
- Configure resume and other application settings
- Save changes to apply on next bot run

### Bot Control Tab
- Start and stop the bot remotely
- View real-time output from the bot
- Monitor bot status

## Deployment

You can deploy this web app for free on various platforms:

### Render
Run the deployment preparation script:
```
python scripts/deploy.py render
```
Follow the instructions in the generated `DEPLOY.md` file.

### Railway
Run the deployment preparation script:
```
python scripts/deploy.py railway
```
Follow the instructions in the generated `DEPLOY.md` file.

### PythonAnywhere
Run the deployment preparation script:
```
python scripts/deploy.py pythonanywhere
```
Follow the instructions in the generated `DEPLOY.md` file.

## Important Notes

- The bot runs headless (no visible browser) when deployed to web platforms
- Free hosting platforms may have limitations for Selenium-based automation
- Keep your LinkedIn credentials secure
- Use the bot responsibly and in accordance with LinkedIn's terms of service

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.