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

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.run_id"))
    timestamp = Column(String)
    event_type = Column(String)
    data = Column(Text) # JSON string

    run = relationship("Run", back_populates="logs")
