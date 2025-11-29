"""Pydantic schemas for AI Agents API."""

from datetime import datetime

from pydantic import BaseModel, Field


class AIAgentCreate(BaseModel):
    """Schema for creating a new AI Agent."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    system_prompt: str = Field(..., min_length=1)
    model: str = Field(default="claude-haiku-4-5")
    temperature: float = Field(default=0.5, ge=0, le=1)
    is_default: bool = Field(default=False)
    # Memory limits
    # max_messages: int | None = Field(default=50, ge=1, le=200)  # TODO: implement later
    max_tokens: int | None = Field(default=16000, ge=1000, le=128000)


class AIAgentUpdate(BaseModel):
    """Schema for updating an AI Agent."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    system_prompt: str | None = Field(None, min_length=1)
    model: str | None = None
    temperature: float | None = Field(None, ge=0, le=1)
    is_active: bool | None = None
    # Memory limits
    # max_messages: int | None = Field(None, ge=1, le=200)  # TODO: implement later
    max_tokens: int | None = Field(None, ge=1000, le=128000)


class AIAgentResponse(BaseModel):
    """Schema for AI Agent response."""

    id: str
    name: str
    description: str | None
    system_prompt: str
    model: str
    temperature: float
    is_default: bool
    is_active: bool
    # Memory limits
    # max_messages: int | None  # TODO: implement later
    max_tokens: int | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
