"""Fixtures for AI Agents tests."""

import sys
from pathlib import Path
from unittest.mock import patch

# Add src to path before any imports that depend on it
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from service import app  # noqa: E402


@pytest.fixture
def test_client():
    """Fixture to create a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Fixture for authenticated requests."""
    return {"Authorization": "Bearer test-secret"}


@pytest.fixture
def mock_auth():
    """Fixture to bypass authentication."""
    with patch("service.service.settings") as mock_settings:
        mock_settings.AUTH_SECRET = None
        yield mock_settings


@pytest.fixture
def sample_ai_agent():
    """Sample AI Agent data for tests."""
    return {
        "name": "Sales Assistant",
        "description": "An AI agent specialized in sales",
        "system_prompt": "You are a helpful sales assistant. Help customers find the best products.",
        "model": "claude-haiku-4-5",
        "temperature": 0.7,
        "is_default": True,
    }


@pytest.fixture
def sample_ai_agent_update():
    """Sample AI Agent update data for tests."""
    return {
        "name": "Updated Sales Assistant",
        "temperature": 0.5,
    }
