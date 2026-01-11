import os
import json
import subprocess
import sys
from datetime import datetime
from typing import List, Dict
from backend.celery_app import celery_app
from backend.database import SessionLocal
from backend.models import Run, Log
from backend.email_service import send_job_completion_email, send_job_failure_email

@celery_app.task(bind=True)
def run_script_task(self, script_name: str, args: List[str], env_vars: Dict[str, str], run_id: str):
    """
    Executes a script in the background using Celery.
    Logs output to Postgres via SQLAlchemy.
    """
    db = SessionLocal()
    
    # Sanitize script name
    safe_script_name = os.path.basename(script_name)
    script_path = os.path.join("/app/execution", safe_script_name)
    
    # Path resolution logic
    if not os.path.exists(script_path):
        # Fallbacks for different envs
        potential_paths = [
            os.path.join("execution", safe_script_name),
            os.path.join(os.getcwd(), "execution", safe_script_name),
            os.path.join("/app/inboxbench/execution", safe_script_name),
            os.path.join("inboxbench/execution", safe_script_name)
        ]
        for p in potential_paths:
            if os.path.exists(p):
                script_path = p
                break
        else:
            print(f"Error: Script {script_path} not found")
            # Log failure
            run = db.query(Run).filter(Run.run_id == run_id).first()
            if run:
                run.status = "FAILED"
                run.end_time = datetime.utcnow().isoformat()
                db.commit()
            db.close()
            return "Script Not Found"

    # Merge Env Vars
    current_env = os.environ.copy()
    current_env.update(env_vars)
    current_env["RUN_ID"] = run_id
    if "API_BASE_URL" not in current_env:
        # Default to internal container network or localhost
        current_env["API_BASE_URL"] = "http://localhost:8000/api"

    cmd = ["python3", "-u", script_path] + args
    print(f"[Celery] Starting: {' '.join(cmd)}")

    # Update Status to RUNNING
    run = db.query(Run).filter(Run.run_id == run_id).first()
    if run:
        run.status = "RUNNING"
        db.commit()

    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            env=current_env,
            bufsize=1
        )

        # Stream logs
        for line in iter(process.stdout.readline, ''):
            if not line: break
            
            # Print to worker logs
            sys.stdout.write(line)
            
            # Log to DB
            try:
                log_data = {"stdout": line.strip()}
                new_log = Log(
                    run_id=run_id,
                    timestamp=datetime.utcnow().isoformat(),
                    event_type="SCRIPT_OUTPUT",
                    data=json.dumps(log_data)
                )
                db.add(new_log)
                db.commit()
            except Exception as e:
                print(f"Log DB Error: {e}")

        process.wait()
        returncode = process.returncode
        
        # Final Update
        run = db.query(Run).filter(Run.run_id == run_id).first()
        if run:
            run.status = "COMPLETED" if returncode == 0 else "FAILED"
            run.end_time = datetime.utcnow().isoformat()
            db.commit()

        # Email Notification Logic
        if returncode == 0:
            handle_email_notification(db, run_id, args)
        else:
            handle_failure_email(db, run_id, args)

    except Exception as e:
        print(f"Exception executing script: {e}")
        run = db.query(Run).filter(Run.run_id == run_id).first()
        if run:
            run.status = "ERROR"
            run.end_time = datetime.utcnow().isoformat()
            db.commit()
    finally:
        db.close()

def handle_email_notification(db, run_id, args):
    # Extract Email
    recipient_email = None
    if "--email" in args:
        try:
            idx = args.index("--email")
            recipient_email = args[idx+1]
        except: pass

    if not recipient_email:
        return

    # Find Sheet URL in logs
    logs = db.query(Log).filter(Log.run_id == run_id, Log.event_type == "SCRIPT_OUTPUT").all()
    sheet_url = None
    for log in logs:
        try:
            content = json.loads(log.data)
            stdout = content.get('stdout', '')
            if "Sheet URL:" in stdout:
                parts = stdout.split("Sheet URL:")
                if len(parts) > 1:
                    sheet_url = parts[1].strip()
        except: pass
    
    if sheet_url:
        print(f"[Celery] Sending email to {recipient_email}")
        send_job_completion_email(recipient_email, sheet_url)

def handle_failure_email(db, run_id, args):
    recipient_email = None
    if "--email" in args:
        try:
            idx = args.index("--email")
            recipient_email = args[idx+1]
        except: pass
    
    if recipient_email:
        print(f"[Celery] Sending failure email to {recipient_email}")
        send_job_failure_email(recipient_email, "Script failed to execute correctly.")
