import os
import subprocess
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import multiprocessing
import sys
import sqlite3
import json
from datetime import datetime

# Add current directory to sys.path to ensure module resolution
sys.path.append(os.getcwd())
try:
    from backend.telegram_bot import run_telegram_bot
except ImportError:
    # Fallback if running from within backend dir or other structure issues
    from telegram_bot import run_telegram_bot

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sipes Automation Backend", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only. In prod, strict list.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
DB_PATH = "automation.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS runs
                 (run_id TEXT PRIMARY KEY, script_name TEXT, status TEXT, start_time TEXT, end_time TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, timestamp TEXT, event_type TEXT, data TEXT)''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
async def startup_event():
    # Initialize DB
    init_db()
    
    # Start Telegram Bot in a separate process
    # We check for the token inside run_telegram_bot, so safe to call.
    bot_process = multiprocessing.Process(target=run_telegram_bot, daemon=True)
    bot_process.start()
    print(f"Telegram Bot started with PID: {bot_process.pid}")

# --- Models ---

class ScriptExecutionRequest(BaseModel):
    script_name: str
    args: List[str] = []
    env_vars: Dict[str, str] = {}

class RunStart(BaseModel):
    run_id: str
    script_name: str
    status: str
    start_time: str

class RunUpdate(BaseModel):
    status: str
    end_time: str

class LogEntry(BaseModel):
    run_id: str
    timestamp: str
    event_type: str
    data: Dict[str, Any]

# --- Endpoints ---

@app.get("/")
def health_check():
    return {"status": "ok", "service": "sipes-automation-backend"}

# ... Run Tracking Endpoints ...

@app.post("/api/runs")
def register_run(run: RunStart):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO runs (run_id, script_name, status, start_time) VALUES (?, ?, ?, ?)",
                  (run.run_id, run.script_name, run.status, run.start_time))
        conn.commit()
    except Exception as e:
        print(f"DB Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
    return {"status": "registered", "run_id": run.run_id}

@app.put("/api/runs/{run_id}")
def update_run(run_id: str, update: RunUpdate):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE runs SET status = ?, end_time = ? WHERE run_id = ?",
                  (update.status, update.end_time, run_id))
        conn.commit()
    except Exception as e:
         print(f"DB Error: {e}")
         raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
    return {"status": "updated"}

@app.post("/api/logs")
def add_log(log: LogEntry):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # data is stored as JSON string
        c.execute("INSERT INTO logs (run_id, timestamp, event_type, data) VALUES (?, ?, ?, ?)",
                  (log.run_id, log.timestamp, log.event_type, json.dumps(log.data)))
        conn.commit()
    except Exception as e:
         print(f"DB Error: {e}")
         # Don't crash the script if logging fails
         pass 
    finally:
        conn.close()
    return {"status": "logged"}

@app.get("/api/runs")
def list_runs(limit: int = 50):
    conn = get_db_connection()
    runs = conn.execute("SELECT * FROM runs ORDER BY start_time DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return {"runs": [dict(r) for r in runs]}

@app.get("/api/runs/{run_id}")
def get_run_details(run_id: str):
    conn = get_db_connection()
    run = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
    logs = conn.execute("SELECT * FROM logs WHERE run_id = ? ORDER BY id ASC", (run_id,)).fetchall()
    conn.close()
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    return {
        "run": dict(run),
        "logs": [dict(l) for l in logs]
    }

# ... Execution Logic ...

def run_script_task(script_name: str, args: List[str], env_vars: Dict[str, str]):
    """
    Executes a script in the background.
    """
    # Sanitize script name to prevent command injection
    # Only allow scripts from the execution directory or its subdirectories
    safe_script_name = os.path.basename(script_name)
    script_path = os.path.join("/app/execution", safe_script_name)
    
    # Validation for local dev where path might differ
    if not os.path.exists(script_path):
        # Try local execution path
        if os.path.exists(os.path.join("execution", safe_script_name)):
             script_path = os.path.join("execution", safe_script_name)
        # Try local execution path from root
        elif os.path.exists(os.path.join(os.getcwd(), "execution", safe_script_name)):
             script_path = os.path.join(os.getcwd(), "execution", safe_script_name)
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
    # Ensure API URL is set for instrumentation
    if "API_BASE_URL" not in current_env:
        current_env["API_BASE_URL"] = "http://localhost:8000/api"

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

@app.post("/api/execute")
async def execute_script(request: ScriptExecutionRequest, background_tasks: BackgroundTasks):
    """
    Trigger a python script execution.
    """
    # Allow-list validation could be added here
    allowed_scripts = [
        "api_powerhouse.py",
        "get_new_leads.py", 
        "check_api_keys.py",
        "run_full_cycle.py"
    ]
    
    # Simple check, in production we might want stricter validation
    if request.script_name not in allowed_scripts:
        pass 

    background_tasks.add_task(run_script_task, request.script_name, request.args, request.env_vars)
    return {"status": "queued", "script": request.script_name}

@app.post("/api/leads/generate")
async def generate_leads(background_tasks: BackgroundTasks):
    """
    Specific endpoint to trigger lead generation
    """
    background_tasks.add_task(run_script_task, "api_powerhouse.py", [], {})
    return {"status": "queued", "job": "lead_generation"}
