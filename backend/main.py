import os
import json
import uuid
import stripe
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

# Internal Imports
from backend.database import SessionLocal, engine, Base
from backend.models import Run, Log
from backend.tasks import run_script_task
from backend.celery_app import celery_app
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=1.0, 
    )

# Add current directory to sys.path
import sys
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Sipes Automation Backend", version="2.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://www.sipesautomation.com",
        "https://sipes-automation-site.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    # Initialize Stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    
    # Ensure Tables Exist (Safe to run on restart)
    try:
        from sqlalchemy import text
        Base.metadata.create_all(bind=engine)
        
        # Run Auto-Migrations (Column additions)
        try:
            from backend.database import run_migrations
            run_migrations()
        except Exception as e:
            print(f"Migration Error: {e}")
        
        # Auto-Migration for 'args' and 'env_vars' in 'runs' table
        with engine.connect() as conn:
            try:
                conn.execute(text("SELECT args FROM runs LIMIT 1"))
            except Exception:
                print("Migrating DB: Adding 'args' column...")
                conn.execute(text("ALTER TABLE runs ADD COLUMN args TEXT"))
                conn.commit()

            try:
                conn.execute(text("SELECT env_vars FROM runs LIMIT 1"))
            except Exception:
                print("Migrating DB: Adding 'env_vars' column...")
                conn.execute(text("ALTER TABLE runs ADD COLUMN env_vars TEXT"))
                conn.commit()
                
    except Exception as e:
        print(f"DB Init Warning: {e}")

    # Start Telegram Bot (Async)
    # Note: Telegram Bot logic might need to be decoupled if we want multiple workers,
    # but for the API server, it's fine to run one instance here.
    try:
        from backend.telegram_bot import get_bot_application
        bot_app = await get_bot_application()
        if bot_app:
            await bot_app.initialize()
            await bot_app.start()
            try:
                await bot_app.updater.start_polling()
                app.state.bot_app = bot_app
                print("Telegram Bot started successfully")
            except Exception as e:
                # Handle conflict
                 print(f"Telegram Bot Warning: {e}")
    except ImportError:
        pass
    except Exception as e:
        print(f"Telegram Bot Error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, "bot_app") and app.state.bot_app:
        print("Stopping Telegram Bot...")
        await app.state.bot_app.updater.stop()
        await app.state.bot_app.stop()
        await app.state.bot_app.shutdown()

# --- Models (Pydantic) ---

class ScriptExecutionRequest(BaseModel):
    script_name: str
    args: List[str] = []
    env_vars: Dict[str, str] = {}

class RunStart(BaseModel):
    run_id: str
    script_name: str
    status: str
    start_time: str

class LeadGenRequest(BaseModel):
    url: str
    email: str
    limit: Optional[int] = 100

class LogEntry(BaseModel):
    run_id: str
    timestamp: str
    event_type: str
    data: Dict[str, Any] # Recieved as JSON dict

from typing import Any

# --- Endpoints ---

@app.get("/")
def health_check():
    return {"status": "ok", "service": "sipes-automation-backend-v2"}

@app.get("/api/runs")
def list_runs(limit: int = 50, db: Session = Depends(get_db)):
    runs = db.query(Run).order_by(Run.start_time.desc()).limit(limit).all()
    return {"runs": runs}

@app.get("/api/runs/{run_id}")
def get_run_details(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Use ORM relationship, but sort logs?
    # relationship logs is unordered usually unless defined.
    # explicit query is safer for sorting
    logs = db.query(Log).filter(Log.run_id == run_id).order_by(Log.id.asc()).all()
    
    # Parse log data from JSON string to dict for response
    logs_data = []
    for l in logs:
        log_dict = l.__dict__.copy()
        if "data" in log_dict and isinstance(log_dict["data"], str):
             try:
                 log_dict["data"] = json.loads(log_dict["data"])
             except: pass
        # Remove SQLAlchemy internal state
        log_dict.pop("_sa_instance_state", None)
        logs_data.append(log_dict)

    return {
        "run": run,
        "logs": logs_data
    }

@app.get("/api/runs/{run_id}/leads")
def get_run_leads(run_id: str, db: Session = Depends(get_db)):
    from backend.models import Lead
    leads = db.query(Lead).filter(Lead.run_id == run_id).all()
    return {"leads": leads}

@app.post("/api/execute")
async def execute_script(request: ScriptExecutionRequest, db: Session = Depends(get_db)):
    run_id = str(uuid.uuid4())
    
    # Create Run in DB
    new_run = Run(
        run_id=run_id,
        script_name=request.script_name,
        status="QUEUED",
        start_time=datetime.utcnow().isoformat(),
        args=json.dumps(request.args),
        env_vars=json.dumps(request.env_vars)
    )
    db.add(new_run)
    db.commit()
    
    # Dispatch to Celery
    run_script_task.delay(request.script_name, request.args, request.env_vars, run_id)
    
    return {"status": "queued", "run_id": run_id}

@app.post("/api/leads/process-url")
def process_apollo_url(request: LeadGenRequest, db: Session = Depends(get_db)):
    if not request.url or not request.email:
         raise HTTPException(status_code=400, detail="URL and Email are required")

    run_id = str(uuid.uuid4())
    args = ["--url", request.url, "--email", request.email, "--limit", str(request.limit)]
    
    new_run = Run(
        run_id=run_id,
        script_name="lead_gen_orchestrator.py",
        status="QUEUED",
        start_time=datetime.utcnow().isoformat(),
        args=json.dumps(args),
        env_vars=json.dumps({})
    )
    db.add(new_run)
    db.commit()

    # Dispatch
    run_script_task.delay("lead_gen_orchestrator.py", args, {}, run_id)

    return {"status": "queued", "job": "lead_gen_orchestrator", "run_id": run_id}

@app.post("/api/leads/preview")
def preview_leads(request: LeadGenRequest):
    try:
        from execution.lead_gen_orchestrator import get_preview_leads
        leads = get_preview_leads(request.url)
        return {"leads": leads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Stripe ---

@app.post("/api/create-checkout-session")
def create_checkout_session(request: LeadGenRequest, db: Session = Depends(get_db)):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe API Key not configured")

    try:
        limit = request.limit or 100
        price_cents = int((limit / 1000) * 50)
        if price_cents < 50: price_cents = 50

        # Create Run immediately (Pending Payment)
        # This solves the Stripe Metadata 500 chars limit issue by storing the long URL in DB
        run_id = str(uuid.uuid4())
        args = ["--url", request.url, "--email", request.email, "--limit", str(limit)]
        
        new_run = Run(
            run_id=run_id,
            script_name="lead_gen_orchestrator.py",
            status="PENDING_PAYMENT",
            start_time=datetime.utcnow().isoformat(),
            args=json.dumps(args),
            env_vars=json.dumps({})
        )
        db.add(new_run)
        db.commit()

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
            success_url=os.getenv("FRONTEND_URL", "https://www.sipesautomation.com/lead-gen") + "?success=true&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=os.getenv("FRONTEND_URL", "https://www.sipesautomation.com/lead-gen") + "?canceled=true",
            metadata={
                'run_id': run_id, # Pass reference instead of full data
                'email': request.email, # Keep for quick reference in dashboard
                'limit': str(limit)
            }
        )
        return {"checkoutUrl": checkout_session.url}
    except Exception as e:
        print(f"Stripe Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    event = None

    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            data = json.loads(payload)
            event = stripe.Event.construct_from(data, stripe.api_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid Stripe payload/signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        
        # New Flow: Run ID passed
        run_id = metadata.get('run_id')
        
        # Fallback Flow (Legacy): Data passed directly (will likely fail for long URLs anyway)
        apollo_url = metadata.get('apollo_url')
        email = metadata.get('email')
        limit = metadata.get('limit')
        
        if run_id:
            print(f"[Stripe] Payment received for Run ID: {run_id}")
            # Find existing run
            run = db.query(Run).filter(Run.run_id == run_id).first()
            if run:
                run.status = "QUEUED"
                
                # Retrieve args from DB to dispatch
                args = json.loads(run.args)
                env_vars = json.loads(run.env_vars) if run.env_vars else {}
                
                # Log Session ID
                log_data = json.dumps({"session_id": session['id']})
                new_log = Log(
                    run_id=run_id,
                    timestamp=datetime.utcnow().isoformat(),
                    event_type="STRIPE_SESSION_ID",
                    data=log_data
                )
                db.add(new_log)
                db.commit()
                
                # Dispatch
                run_script_task.delay("lead_gen_orchestrator.py", args, env_vars, run_id)
                print(f"[Stripe] Job Resumed: {run_id}")
            else:
                 print(f"[Stripe] Error: Run ID {run_id} not found in DB.")

        elif apollo_url and email:
            print(f"[Stripe] Payment received for {email} (Legacy Flow)")
            run_id = str(uuid.uuid4())
            args = ["--url", apollo_url, "--email", email, "--limit", str(limit or 100)]
            
            new_run = Run(
                run_id=run_id,
                script_name="lead_gen_orchestrator.py",
                status="QUEUED",
                start_time=datetime.utcnow().isoformat(),
                args=json.dumps(args),
                env_vars=json.dumps({})
            )
            db.add(new_run)
            
            # Log Session ID for lookup
            log_data = json.dumps({"session_id": session['id']})
            new_log = Log(
                run_id=run_id,
                timestamp=datetime.utcnow().isoformat(),
                event_type="STRIPE_SESSION_ID",
                data=log_data
            )
            db.add(new_log)
            db.commit()
            
            # Dispatch
            run_script_task.delay("lead_gen_orchestrator.py", args, {}, run_id)
            
            print(f"[Stripe] Job queued: {run_id}")

    return {"status": "success"}

@app.get("/api/runs/lookup")
def lookup_run(session_id: str, db: Session = Depends(get_db)):
    # Search logs for session_id
    # Using ILIKE or similar for JSON text search implies full scan in PG unless indexed text search
    # But volume is low.
    log = db.query(Log).filter(
        Log.event_type == 'STRIPE_SESSION_ID', 
        Log.data.like(f'%"{session_id}"%')
    ).first()
    
    if log:
        return {"run_id": log.run_id}
        
    raise HTTPException(status_code=404, detail="Run not found for this session")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
