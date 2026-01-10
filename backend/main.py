import os
import subprocess
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import multiprocessing
import sys
import sqlite3
import json
import json
from datetime import datetime
import threading
import time

# Add current directory to sys.path to ensure module resolution
sys.path.append(os.getcwd())
import stripe
# Imports for Telegram Bot handled inside startup_event to avoid top-level side effects/errors

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
                 (run_id TEXT PRIMARY KEY, script_name TEXT, status TEXT, start_time TEXT, end_time TEXT, args TEXT, env_vars TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, timestamp TEXT, event_type TEXT, data TEXT)''')
    
    # Migration for existing DBs
    try:
        c.execute("ALTER TABLE runs ADD COLUMN args TEXT")
    except: pass
    try:
        c.execute("ALTER TABLE runs ADD COLUMN env_vars TEXT")
    except: pass
                 
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
async def startup_event():
    # Initialize Stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    
    # Initialize DB
    init_db()
    
    # Start Worker Thread
    threading.Thread(target=worker_loop, daemon=True).start()

    # Start Telegram Bot (Async)
    try:
        from backend.telegram_bot import get_bot_application
    except ImportError:
        from telegram_bot import get_bot_application
        
    bot_app = await get_bot_application()
    if bot_app:
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling()
        app.state.bot_app = bot_app
        print("Telegram Bot started successfully (Async)")
    else:
        print("Telegram Bot failed to start (No Token?)")

@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, "bot_app") and app.state.bot_app:
        print("Stopping Telegram Bot...")
        await app.state.bot_app.updater.stop()
        await app.state.bot_app.stop()
        await app.state.bot_app.shutdown()

def worker_loop():
    print("Worker thread started...")
    while True:
        try:
            conn = get_db_connection()
            # FIFO Queue
            cursor = conn.execute("SELECT * FROM runs WHERE status='QUEUED' ORDER BY start_time ASC LIMIT 1")
            job = cursor.fetchone()
            conn.close()
            
            if job:
                run_id = job['run_id']
                script_name = job['script_name']
                print(f"[Worker] Picked up job {run_id} ({script_name})")
                
                # Parse args/env
                args_str = job['args']
                env_str = job['env_vars']
                args = json.loads(args_str) if args_str else []
                env_vars = json.loads(env_str) if env_str else {}
                
                # Run Task (Blocking)
                run_script_task(script_name, args, env_vars, run_id)
            else:
                time.sleep(2) # Poll delay
        except Exception as e:
            print(f"[Worker] Error: {e}")
            time.sleep(5)

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

class LeadGenRequest(BaseModel):
    url: str
    url: str
    email: str
    limit: Optional[int] = 100

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

import uuid

def run_script_task(script_name: str, args: List[str], env_vars: Dict[str, str], run_id: str = None):
    """
    Executes a script in the background. Options to log to DB if run_id provided.
    """
    # Sanitize script name to prevent command injection
    safe_script_name = os.path.basename(script_name)
    script_path = os.path.join("/app/execution", safe_script_name)
    
    # Path resolution logic (same as before)
    if not os.path.exists(script_path):
        if os.path.exists(os.path.join("execution", safe_script_name)):
             script_path = os.path.join("execution", safe_script_name)
        elif os.path.exists(os.path.join(os.getcwd(), "execution", safe_script_name)):
             script_path = os.path.join(os.getcwd(), "execution", safe_script_name)
        elif os.path.exists(os.path.join("/app/inboxbench/execution", safe_script_name)):
             script_path = os.path.join("/app/inboxbench/execution", safe_script_name)
        elif os.path.exists(os.path.join("inboxbench/execution", safe_script_name)):
             script_path = os.path.join("inboxbench/execution", safe_script_name)
        else:
            print(f"Error: Script {script_path} or inboxbench equivalent not found")
            if run_id:
                # Log error
                pass # TODO: DB log
            return

    # Merge current env with provided env_vars
    current_env = os.environ.copy()
    current_env.update(env_vars)
    if "API_BASE_URL" not in current_env:
        current_env["API_BASE_URL"] = "http://localhost:8000/api"

    cmd = ["python3", script_path] + args
    
    print(f"Starting execution of: {' '.join(cmd)}")
    
    # Update Status to RUNNING
    if run_id:
        conn = get_db_connection()
        try:
             conn.execute("UPDATE runs SET status = 'RUNNING' WHERE run_id = ?", (run_id,))
             conn.commit()
        except: pass
        finally: conn.close()
        
    try:
        # Use Popen for streaming
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            env=current_env,
            bufsize=1 # Line buffered
        )
        
        # Stream logs
        if run_id:
            conn = get_db_connection()
            for line in iter(process.stdout.readline, ''):
                if not line: break
                
                # Print local
                sys.stdout.write(line) 
                
                # Log to DB (Real-time)
                # We could batch this if performance is an issue, but for <1000 lines it's fine.
                try:
                    log_data = {"stdout": line.strip()}
                    conn.execute("INSERT INTO logs (run_id, timestamp, event_type, data) VALUES (?, ?, ?, ?)",
                              (run_id, datetime.utcnow().isoformat(), "SCRIPT_OUTPUT", json.dumps(log_data)))
                    conn.commit()
                except: pass
            conn.close()
            
        process.wait()
        returncode = process.returncode
        
        # Final Status Update
        if run_id:
            conn = get_db_connection()
            status = "COMPLETED" if returncode == 0 else "FAILED"
            conn.execute("UPDATE runs SET status = ?, end_time = ? WHERE run_id = ?",
                      (status, datetime.utcnow().isoformat(), run_id))
            conn.commit()
            conn.close()

        if returncode != 0:
            print(f"Script {safe_script_name} failed with code {returncode}")
        else:
            print(f"Script {safe_script_name} completed successfully")
            
    except Exception as e:
        print(f"Exception executing script {safe_script_name}: {e}")
        if run_id:
            conn = get_db_connection()
            conn.execute("UPDATE runs SET status = 'ERROR', end_time = ? WHERE run_id = ?",
                      (datetime.utcnow().isoformat(), run_id))
            conn.commit()
            conn.close()

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

    background_tasks.add_task(run_script_task, "api_powerhouse.py", [], {})
    return {"status": "queued", "job": "lead_generation"}

@app.post("/api/leads/process-url")
async def process_apollo_url(request: LeadGenRequest, background_tasks: BackgroundTasks):
    """
    Triggers the Apollo -> Blitz -> Sheets workflow.
    """
    # Run execution/lead_gen_orchestrator.py
    # Args: --url "..." --email "..."
    if not request.url or not request.email:
         raise HTTPException(status_code=400, detail="URL and Email are required")

    # Create valid run_id
    run_id = str(uuid.uuid4())
    
    # Register Run in DB as QUEUED with ARGS
    args = ["--url", request.url, "--email", request.email, "--limit", str(request.limit)]
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO runs (run_id, script_name, status, start_time, args, env_vars) VALUES (?, ?, ?, ?, ?, ?)",
                  (run_id, "lead_gen_orchestrator.py", "QUEUED", datetime.utcnow().isoformat(), json.dumps(args), json.dumps({})))
        conn.commit()
    finally:
        conn.close()

    # Worker will pick it up
    return {"status": "queued", "job": "lead_gen_orchestrator", "run_id": run_id}

@app.post("/api/leads/preview")
def preview_leads(request: LeadGenRequest):
    """
    Returns a preview of enriched leads without saving.
    """
    try:
        # Import here to avoid circular dependencies if any, 
        # though top-level is usually fine.
        from execution.lead_gen_orchestrator import get_preview_leads
        
        leads = get_preview_leads(request.url)
        return {"leads": leads}
    except Exception as e:
        print(f"Preview Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Stripe Endpoints ---

@app.post("/api/create-checkout-session")
async def create_checkout_session(request: LeadGenRequest):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe API Key not configured")

    try:
        # 1. Calculate Price
        limit = request.limit or 100
        # Price Logic: $0.50 per 1000 items. Minimum $0.50? Let's stick to user prompt roughly.
        # User said: "50 cents a thousand leads... If it's over 10,000 leads, it's $10... whatever you think a reasonable amount would be"
        # Let's simplify: $0.50 per 1000.
        # Price in Cents. 
        # (limit / 1000) * 0.50 dollars -> (limit / 1000) * 50 cents
        price_cents = int((limit / 1000) * 50)
        if price_cents < 50: price_cents = 50 # Minimum 50 cents charge to cover fees roughly

        # 2. Create Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Apollo Lead Generation',
                        'description': f'Scraping & Enriching {limit} leads',
                    },
                    'unit_amount': price_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            # We need the Frontend Origin.
            success_url=os.getenv("FRONTEND_URL", "https://sipes-automation-frontend-production.up.railway.app/lead-gen") + "?success=true&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=os.getenv("FRONTEND_URL", "https://sipes-automation-frontend-production.up.railway.app/lead-gen") + "?canceled=true",
            metadata={
                'apollo_url': request.url,
                'email': request.email,
                'limit': str(limit)
            }
        )
        return {"checkoutUrl": checkout_session.url}
    except Exception as e:
        print(f"Stripe Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import Request

@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    event = None

    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        else:
            # If no secret (dev), just parse raw
            # WARN: insecure for prod, but handy if user hasn't set secret yet
            data = json.loads(payload)
            event = stripe.Event.construct_from(data, stripe.api_key)
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Fulfill the purchase...
        metadata = session.get('metadata', {})
        apollo_url = metadata.get('apollo_url')
        email = metadata.get('email')
        limit = metadata.get('limit')
        
        if apollo_url and email:
            print(f"Payment received! Starting job for {email}")
            
            run_id = str(uuid.uuid4())
            # Register Run as QUEUED
            args = ["--url", apollo_url, "--email", email, "--limit", str(limit or 100)]
            conn = get_db_connection()
            try:
                conn.execute("INSERT INTO runs (run_id, script_name, status, start_time, args, env_vars) VALUES (?, ?, ?, ?, ?, ?)",
                        (run_id, "lead_gen_orchestrator.py", "QUEUED", datetime.utcnow().isoformat(), json.dumps(args), json.dumps({})))
                # Log session
                conn.execute("INSERT INTO logs (run_id, timestamp, event_type, data) VALUES (?, ?, ?, ?)",
                          (run_id, datetime.utcnow().isoformat(), "STRIPE_SESSION_ID", json.dumps({"session_id": session['id']})))
                conn.commit()
            finally:
                conn.close()

            print(f"Job queued: {run_id}")  
            # Worker will pick it up

    return {"status": "success"}

@app.get("/api/runs/lookup")
def lookup_run(session_id: str):
    conn = get_db_connection()
    try:
        # Simple LIKE query to find the session_id in the JSON data column
        cursor = conn.execute("SELECT run_id FROM logs WHERE event_type='STRIPE_SESSION_ID' AND data LIKE ?", (f'%"{session_id}"%',))
        row = cursor.fetchone()
        if row:
            return {"run_id": row[0]}
    finally:
        conn.close()
    
    raise HTTPException(status_code=404, detail="Run not found for this session")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Force Redeploy: Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
