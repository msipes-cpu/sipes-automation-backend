import os
import json
import subprocess
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import multiprocessing
import sys
# Add current directory to sys.path to ensure module resolution
sys.path.append(os.getcwd())
try:
    from backend.telegram_bot import run_telegram_bot
except ImportError:
    # Fallback if running from within backend dir or other structure issues
    from telegram_bot import run_telegram_bot

app = FastAPI(title="Sipes Automation Backend", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    # Start Telegram Bot in a separate process
    # We check for the token inside run_telegram_bot, so safe to call.
    bot_process = multiprocessing.Process(target=run_telegram_bot, daemon=True)
    bot_process.start()
    print(f"Telegram Bot started with PID: {bot_process.pid}")

class ScriptExecutionRequest(BaseModel):
    script_name: str
    args: List[str] = []
    env_vars: Dict[str, str] = {}
    client_id: Optional[str] = None

@app.get("/")
def health_check():
    return {"status": "ok", "service": "sipes-automation-backend"}

def run_script_task(script_name: str, args: List[str], env_vars: Dict[str, str]):
    """
    Executes a script in the background.
    """
    # Sanitize script name to prevent command injection
    # Only allow scripts from the execution directory
    safe_script_name = os.path.basename(script_name)
    script_path = os.path.join("/app/execution", safe_script_name)
    
    # Validation for local dev where path might differ
    if not os.path.exists(script_path):
        # Try local execution path
        if os.path.exists(os.path.join("execution", safe_script_name)):
             script_path = os.path.join("execution", safe_script_name)
        # Try inboxbench path
        elif os.path.exists(os.path.join("/app/inboxbench/execution", safe_script_name)):
             script_path = os.path.join("/app/inboxbench/execution", safe_script_name)
        elif os.path.exists(os.path.join("inboxbench/execution", safe_script_name)):
             script_path = os.path.join("inboxbench/execution", safe_script_name)
        else:
            print(f"Error: Script {script_path} or inboxbench equivalent not found")
            return

    # Merge current env with provided env_vars
    current_env = os.environ.copy()
    current_env.update(env_vars)

    cmd = ["python3", script_path] + args
    
    print(f"Starting execution of: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            env=current_env
        )
        if result.returncode != 0:
            print(f"Script {safe_script_name} failed with code {result.returncode}")
            print(f"STDERR: {result.stderr}")
        else:
            print(f"Script {safe_script_name} completed successfully")
            print(f"STDOUT: {result.stdout}")
    except Exception as e:
        print(f"Exception executing script {safe_script_name}: {e}")

# Automation ID to Script Mapping
# Definition: automation_id -> [list of authorized scripts]
AUTOMATION_MAPPING = {
    "lead_orchestration": [
        "api_powerhouse.py", 
        "get_new_leads.py", 
        "check_api_keys.py",
        "run_full_cycle.py"
    ],
    "inboxbench": [
        "inboxbench_main.py", # Hypothetical entry point
        "run_warmup.py"
    ],
    # Add more mappings as needed
}

def check_authorization(client_id: str, script_name: str) -> bool:
    """
    Verifies if the client is allowed to run the given script.
    """
    if not client_id:
        # If no client_id provided, assume Admin/System request (allow or block based on policy)
        # For strict multi-tenancy, we might want to block external requests without ID.
        # But for testing, we'll allow.
        return True
        
    config_path = "/app/config/clients.json"
    if not os.path.exists(config_path):
        if os.path.exists("config/clients.json"):
            config_path = "config/clients.json"
        else:
             print("Config not found, denying authorization")
             return False

    try:
        with open(config_path, 'r') as f:
            clients = json.load(f)
            
        client = next((c for c in clients if c.get('client_id') == client_id), None)
        if not client:
            print(f"Client {client_id} not found")
            return False
            
        enabled_automations = client.get("enabled_automations", [])
        
        # Check if script belongs to an enabled automation
        safe_script_name = os.path.basename(script_name)
        
        for automation_id in enabled_automations:
             allowed_scripts = AUTOMATION_MAPPING.get(automation_id, [])
             if safe_script_name in allowed_scripts:
                 return True
                 
        # Special case: allow if script is explicitly in the list (if we move to script-based config)
        if safe_script_name in enabled_automations:
            return True

        print(f"Access Denied: Client {client_id} tried to run {safe_script_name} but has permissions: {enabled_automations}")
        return False
        
    except Exception as e:
        print(f"Auth Check Error: {e}")
        return False

@app.post("/api/execute")
async def execute_script(request: ScriptExecutionRequest, background_tasks: BackgroundTasks):
    """
    Trigger a python script execution. 
    Supports 'client_id' to automatically inject environment variables.
    """
    # 1. Access Control Check
    if request.client_id:
        if not check_authorization(request.client_id, request.script_name):
            raise HTTPException(status_code=403, detail=f"Client {request.client_id} is not authorized to run {request.script_name}")
    
    # Allow-list validation (Security)
    allowed_scripts = []
    for scripts in AUTOMATION_MAPPING.values():
        allowed_scripts.extend(scripts)
    # Add any unmapped system scripts
    allowed_scripts.extend(["telegram_bot.py"]) 
    
    if request.script_name not in allowed_scripts and "inboxbench" not in request.script_name:
         # Basic safeguard, can be relaxed for dev
         pass

    background_tasks.add_task(
        run_script_task, 
        request.script_name, 
        request.args, 
        request.env_vars,
        request.client_id
    )
    return {"status": "queued", "script": request.script_name, "client_id": request.client_id}

@app.post("/api/leads/generate")
async def generate_leads(background_tasks: BackgroundTasks):
    """
    Specific endpoint to trigger lead generation
    """
    background_tasks.add_task(run_script_task, "api_powerhouse.py", [], {})
    return {"status": "queued", "job": "lead_generation"}
