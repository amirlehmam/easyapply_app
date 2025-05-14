import os
import yaml
import json
import time
import threading
import subprocess
import logging
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("easyapply-webapp")

app = FastAPI(title="EasyApply Bot Web App")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variables
bot_process = None
bot_running = False
bot_status = "stopped"
bot_output = []
config_path = "config.yaml"
logs_dir = Path("logs")

# Create logs directory if it doesn't exist
logs_dir.mkdir(exist_ok=True)

class ConfigUpdate(BaseModel):
    config_yaml: str

def read_config():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error reading config: {str(e)}")
        return {"error": str(e)}

def save_config(config_data):
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        return True
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")
        return False

def start_bot_process(background_tasks: BackgroundTasks):
    global bot_process, bot_running, bot_status, bot_output
    
    if bot_running:
        return {"status": "already_running", "message": "Bot is already running"}
    
    bot_output = []
    bot_running = True
    bot_status = "starting"
    
    # Start the bot in a separate thread to not block the API
    background_tasks.add_task(run_bot)
    
    return {"status": "started", "message": "Bot is starting"}

def run_bot():
    global bot_process, bot_running, bot_status, bot_output
    
    try:
        import os
        env = os.environ.copy()
        env["CHROME_BINARY"] = "/opt/google/chrome/chrome"

        bot_process = subprocess.Popen(
            ["python3", "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env
        )
        
        bot_status = "running"
        
        # Read output in real-time
        for line in bot_process.stdout:
            bot_output.append(line.strip())
            if len(bot_output) > 1000:  # Limit output buffer
                bot_output = bot_output[-1000:]
        
        # Process has finished
        exit_code = bot_process.wait()
        bot_running = False
        bot_status = f"stopped (exit code: {exit_code})"
        
    except Exception as e:
        logger.error(f"Error running bot: {str(e)}")
        bot_running = False
        bot_status = f"error: {str(e)}"
        bot_output.append(f"ERROR: {str(e)}")

def stop_bot():
    global bot_process, bot_running, bot_status
    
    if not bot_running or bot_process is None:
        return {"status": "not_running", "message": "Bot is not running"}
    
    try:
        bot_process.terminate()
        # Give it 5 seconds to terminate gracefully
        time_waited = 0
        while bot_process.poll() is None and time_waited < 5:
            time.sleep(0.5)
            time_waited += 0.5
            
        # If still running, force kill
        if bot_process.poll() is None:
            bot_process.kill()
            
        bot_running = False
        bot_status = "stopped (terminated)"
        return {"status": "stopped", "message": "Bot has been stopped"}
    
    except Exception as e:
        logger.error(f"Error stopping bot: {str(e)}")
        return {"status": "error", "message": f"Error stopping bot: {str(e)}"}

def read_logs(max_entries=1000):
    try:
        log_file = logs_dir / "activity.log.jsonl"
        if not log_file.exists():
            return []
        logs = []
        with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                try:
                    logs.append(json.loads(line.strip()))
                    if len(logs) >= max_entries:
                        break
                except Exception:
                    pass
        return logs
    except Exception as e:
        logger.error(f"Error reading logs: {str(e)}")
        return []

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request}
    )

@app.get("/api/status")
async def get_status():
    return {
        "running": bot_running,
        "status": bot_status,
        "output": bot_output[-100:] if bot_output else []  # Return last 100 lines
    }

@app.post("/api/start")
async def start_bot_api(background_tasks: BackgroundTasks):
    return start_bot_process(background_tasks)

@app.post("/api/stop")
async def stop_bot_api():
    return stop_bot()

@app.get("/api/config")
async def get_config():
    try:
        with open("config.yaml", 'r', encoding='utf-8', errors='replace') as f:
            config = yaml.safe_load(f)
        return JSONResponse(content=config)
    except Exception as e:
        logger.error(f"Error reading config.yaml: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/config")
async def update_config(config_update: ConfigUpdate):
    try:
        config_data = yaml.safe_load(config_update.config_yaml)
        success = save_config(config_data)
        if success:
            return {"status": "success", "message": "Configuration updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save configuration")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {str(e)}")

@app.get("/api/logs")
async def get_logs(limit: int = 1000):
    return read_logs(limit)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 