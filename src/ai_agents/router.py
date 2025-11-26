"""FastAPI router for AI Agents API."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, status

from ai_agents.schemas import AIAgentCreate, AIAgentUpdate, AIAgentResponse
from ai_agents.repository import repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-agents", tags=["AI Agents"])


@router.post("", response_model=AIAgentResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_agent(data: AIAgentCreate) -> AIAgentResponse:
    """Create a new AI Agent."""
    agent = await repository.create(data)
    logger.info(f"Created AI Agent: {agent.id}")
    return AIAgentResponse.model_validate(agent)


@router.get("", response_model=List[AIAgentResponse])
async def list_ai_agents() -> List[AIAgentResponse]:
    """List all AI Agents."""
    agents = await repository.list_all()
    return [AIAgentResponse.model_validate(agent) for agent in agents]


@router.get("/{agent_id}", response_model=AIAgentResponse)
async def get_ai_agent(agent_id: str) -> AIAgentResponse:
    """Get an AI Agent by ID."""
    agent = await repository.get_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI Agent {agent_id} not found"
        )
    return AIAgentResponse.model_validate(agent)


@router.put("/{agent_id}", response_model=AIAgentResponse)
async def update_ai_agent(agent_id: str, data: AIAgentUpdate) -> AIAgentResponse:
    """Update an AI Agent."""
    agent = await repository.update(agent_id, data)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI Agent {agent_id} not found"
        )
    logger.info(f"Updated AI Agent: {agent_id}")
    return AIAgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai_agent(agent_id: str) -> None:
    """Delete an AI Agent."""
    deleted = await repository.delete(agent_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI Agent {agent_id} not found"
        )
    logger.info(f"Deleted AI Agent: {agent_id}")


@router.put("/{agent_id}/default", response_model=AIAgentResponse)
async def set_default_ai_agent(agent_id: str) -> AIAgentResponse:
    """Set an AI Agent as the default."""
    agent = await repository.set_default(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI Agent {agent_id} not found"
        )
    logger.info(f"Set AI Agent {agent_id} as default")
    return AIAgentResponse.model_validate(agent)
