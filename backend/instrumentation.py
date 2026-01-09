import os
import requests
import functools
import traceback
import sys
import uuid
import datetime
from typing import Optional, Dict, Any

# Simple configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api")

class AutomationContext:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutomationContext, cls).__new__(cls)
            cls._instance.run_id = None
            cls._instance.script_name = None
            cls._instance.api_url = API_BASE_URL
        return cls._instance

    def initialize(self, script_name: str, run_id: str = None):
        self.script_name = script_name
        self.run_id = run_id or str(uuid.uuid4())
        # Register the run with the backend if we generated a new ID
        if not run_id:
           self._register_run()

    def _register_run(self):
         try:
            payload = {
                "run_id": self.run_id,
                "script_name": self.script_name,
                "status": "running",
                "start_time": datetime.datetime.now().isoformat()
            }
            requests.post(f"{self.api_url}/runs", json=payload, timeout=2)
         except Exception as e:
             # Fail silently so we don't break the actual script
             print(f"[Warning] Failed to register run: {e}")

    def log_step_start(self, step_name: str, step_id: str):
        self._send_event("step_start", {"step_name": step_name, "step_id": step_id})

    def log_step_end(self, step_name: str, step_id: str, status: str, output: str = ""):
        self._send_event("step_end", {"step_name": step_name, "step_id": step_id, "status": status, "output": str(output)})
        
    def log_error(self, step_name: str, error: str):
         self._send_event("error", {"step_name": step_name, "error": str(error)})

    def finish_run(self, status="completed"):
        try:
             payload = {"status": status, "end_time": datetime.datetime.now().isoformat()}
             requests.put(f"{self.api_url}/runs/{self.run_id}", json=payload, timeout=2)
        except Exception:
            pass

    def _send_event(self, event_type: str, data: Dict[str, Any]):
        if not self.run_id:
            return
        
        payload = {
            "run_id": self.run_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        try:
            requests.post(f"{self.api_url}/logs", json=payload, timeout=1)
        except Exception as e:
            # We print to stderr just in case, but usually we want to be silent in prod
            # sys.stderr.write(f"Failed to log event: {e}\n")
            pass

def step(name: str):
    """
    Decorator to wrap a function as a step in the visual automation graph.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ctx = AutomationContext()
            step_id = str(uuid.uuid4())
            
            # If not initialized (script called directly), do a lazy init
            if not ctx.run_id:
                # Try to guess script name from main file
                script_name = os.path.basename(sys.argv[0])
                ctx.initialize(script_name)

            ctx.log_step_start(name, step_id)
            
            try:
                result = func(*args, **kwargs)
                ctx.log_step_end(name, step_id, "success", output=str(result)[:500]) # Truncate output
                return result
            except Exception as e:
                ctx.log_error(name, traceback.format_exc())
                ctx.log_step_end(name, step_id, "failed", output=str(e))
                raise e
        return wrapper
    return decorator

# Initializer for the main block
def init(script_name: str):
    ctx = AutomationContext()
    ctx.initialize(script_name)
    return ctx
