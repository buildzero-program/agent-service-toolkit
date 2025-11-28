"""Repository for AI Agents database operations."""

import logging
import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ai_agents.models import AIAgent, Base
from ai_agents.schemas import AIAgentCreate, AIAgentUpdate
from core.settings import settings

logger = logging.getLogger(__name__)

# Database engine and session
_engine = None
_async_session = None


def _is_db_configured() -> bool:
    """Check if database is configured."""
    return settings.POSTGRES_PASSWORD is not None


def _get_connection_string() -> str:
    """Build async PostgreSQL connection string."""
    if settings.POSTGRES_PASSWORD is None:
        raise ValueError("POSTGRES_PASSWORD is not configured")
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD.get_secret_value()}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/"
        f"{settings.POSTGRES_DB}"
    )


async def init_db() -> None:
    """Initialize database and create tables.

    If POSTGRES_PASSWORD is not configured, this will skip initialization
    and log a warning. The dynamic agent will fall back to default settings.
    """
    global _engine, _async_session

    if not _is_db_configured():
        logger.warning(
            "AI Agents database not configured (POSTGRES_PASSWORD not set). "
            "Dynamic agent will use default settings."
        )
        return

    if _engine is None:
        _engine = create_async_engine(
            _get_connection_string(),
            echo=settings.is_dev(),
            pool_size=settings.POSTGRES_MIN_CONNECTIONS_PER_POOL,
            max_overflow=settings.POSTGRES_MAX_CONNECTIONS_PER_POOL
            - settings.POSTGRES_MIN_CONNECTIONS_PER_POOL,
            pool_pre_ping=True,  # Validate connection before use (handles Neon timeouts)
            pool_recycle=300,  # Recycle connections every 5 minutes
        )
        _async_session = async_sessionmaker(_engine, expire_on_commit=False)

    # Create tables
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("AI Agents database initialized")


async def get_session() -> AsyncSession:
    """Get database session."""
    global _async_session
    if _async_session is None:
        await init_db()
    if _async_session is None:
        raise RuntimeError(
            "Database session not initialized. Ensure POSTGRES_PASSWORD is configured."
        )
    return _async_session()


def generate_id() -> str:
    """Generate a unique ID for an AI Agent."""
    return f"ai_{uuid.uuid4().hex[:12]}"


class AIAgentRepository:
    """Repository for AI Agent CRUD operations."""

    async def create(self, data: AIAgentCreate) -> AIAgent:
        """Create a new AI Agent."""
        async with await get_session() as session:
            # If this agent is default, unset other defaults
            if data.is_default:
                await session.execute(
                    update(AIAgent).where(AIAgent.is_default.is_(True)).values(is_default=False)
                )

            agent = AIAgent(
                id=generate_id(),
                name=data.name,
                description=data.description,
                system_prompt=data.system_prompt,
                model=data.model,
                temperature=data.temperature,
                is_default=data.is_default,
                is_active=True,
            )
            session.add(agent)
            await session.commit()
            await session.refresh(agent)
            return agent

    async def list_all(self) -> list[AIAgent]:
        """List all AI Agents."""
        async with await get_session() as session:
            result = await session.execute(
                select(AIAgent)
                .where(AIAgent.is_active.is_(True))
                .order_by(AIAgent.created_at.desc())
            )
            return list(result.scalars().all())

    async def get_by_id(self, agent_id: str) -> AIAgent | None:
        """Get an AI Agent by ID."""
        async with await get_session() as session:
            result = await session.execute(select(AIAgent).where(AIAgent.id == agent_id))
            return result.scalar_one_or_none()

    async def get_default(self) -> AIAgent | None:
        """Get the default AI Agent."""
        async with await get_session() as session:
            result = await session.execute(
                select(AIAgent).where(AIAgent.is_default.is_(True), AIAgent.is_active.is_(True))
            )
            return result.scalar_one_or_none()

    async def update(self, agent_id: str, data: AIAgentUpdate) -> AIAgent | None:
        """Update an AI Agent."""
        async with await get_session() as session:
            result = await session.execute(select(AIAgent).where(AIAgent.id == agent_id))
            agent = result.scalar_one_or_none()

            if not agent:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(agent, key, value)

            agent.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(agent)
            return agent

    async def delete(self, agent_id: str) -> bool:
        """Delete an AI Agent (soft delete by setting is_active=False)."""
        async with await get_session() as session:
            result = await session.execute(select(AIAgent).where(AIAgent.id == agent_id))
            agent = result.scalar_one_or_none()

            if not agent:
                return False

            agent.is_active = False
            agent.updated_at = datetime.utcnow()
            await session.commit()
            return True

    async def set_default(self, agent_id: str) -> AIAgent | None:
        """Set an AI Agent as the default."""
        async with await get_session() as session:
            # First, check if agent exists
            result = await session.execute(
                select(AIAgent).where(AIAgent.id == agent_id, AIAgent.is_active.is_(True))
            )
            agent = result.scalar_one_or_none()

            if not agent:
                return None

            # Unset all other defaults
            await session.execute(
                update(AIAgent).where(AIAgent.is_default.is_(True)).values(is_default=False)
            )

            # Set this agent as default
            agent.is_default = True
            agent.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(agent)
            return agent


# Singleton instance
repository = AIAgentRepository()


async def get_default_agent(max_retries: int = 2) -> AIAgent | None:
    """Convenience function to get the default agent.

    Returns None if database is not configured or if all retries fail.
    Uses retry logic to handle transient connection errors (e.g., Neon idle timeouts).
    """
    if not _is_db_configured():
        return None

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return await repository.get_default()
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()
            # Check if it's a connection error worth retrying
            is_connection_error = any(
                msg in error_msg
                for msg in ["connection", "closed", "timeout", "reset", "refused"]
            )

            if is_connection_error and attempt < max_retries:
                logger.warning(
                    f"Database connection error (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying..."
                )
                # Reset engine to force new connection on next attempt
                global _engine, _async_session
                if _engine is not None:
                    await _engine.dispose()
                _engine = None
                _async_session = None
                continue
            else:
                break

    # Log final error and return None as fallback
    logger.error(
        f"Failed to get default agent after {max_retries + 1} attempts: {last_error}. "
        "Using default settings."
    )
    return None
