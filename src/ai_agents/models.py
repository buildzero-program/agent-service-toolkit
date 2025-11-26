"""SQLAlchemy models for AI Agents."""

from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


class AIAgent(Base):
    """AI Agent model for storing dynamic agent configurations."""

    __tablename__ = "ai_agents"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # LLM Configuration
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(50), default="claude-haiku-4-5", nullable=False)
    temperature: Mapped[float] = mapped_column(default=0.5, nullable=False)

    # Status
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now(), nullable=True)

    def __repr__(self) -> str:
        return f"<AIAgent(id={self.id}, name={self.name}, is_default={self.is_default})>"
