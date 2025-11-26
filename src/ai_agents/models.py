"""SQLAlchemy models for AI Agents."""

from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AIAgent(Base):
    """AI Agent model for storing dynamic agent configurations."""

    __tablename__ = "ai_agents"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # LLM Configuration
    system_prompt = Column(Text, nullable=False)
    model = Column(String(50), default="claude-haiku-4-5", nullable=False)
    temperature = Column(Float, default=0.5, nullable=False)

    # Status
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    def __repr__(self) -> str:
        return f"<AIAgent(id={self.id}, name={self.name}, is_default={self.is_default})>"
