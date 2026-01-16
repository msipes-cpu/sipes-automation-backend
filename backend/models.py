from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Run(Base):
    __tablename__ = "runs"

    run_id = Column(String, primary_key=True, index=True)
    script_name = Column(String, index=True)
    status = Column(String, default="QUEUED")
    start_time = Column(String) # Keeping as string to match old schema execution, or migrate to DateTime? 
    # To keep migration simple, we'll keep as String (ISO format) for now, 
    # but normally DateTime is better. Let's stick to String to avoid migration headaches with existing data format.
    end_time = Column(String, nullable=True)
    args = Column(Text, nullable=True) # JSON Array string
    env_vars = Column(Text, nullable=True) # JSON Object string

    logs = relationship("Log", back_populates="run")
    leads = relationship("Lead", back_populates="run")

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.run_id"))
    timestamp = Column(String)
    event_type = Column(String)
    data = Column(Text) # JSON string

    run = relationship("Run", back_populates="logs")

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.run_id")) # Link to the job run
    
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    company = Column(String, nullable=True)
    title = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    location = Column(String, nullable=True)
    # Flexible store
    raw_data = Column(JSON, nullable=True)

    run = relationship("Run", back_populates="leads")

class WorkspaceConfig(Base):
    __tablename__ = "workspace_configs"
    
    workspace_id = Column(String, primary_key=True, index=True) # Mapped to user email
    apollo_api_key = Column(String, nullable=True)
    blitz_api_key = Column(String, nullable=True)
    million_verifier_api_key = Column(String, nullable=True)
    smartlead_api_key = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
