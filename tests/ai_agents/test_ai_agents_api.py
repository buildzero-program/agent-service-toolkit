"""Tests for AI Agents API endpoints."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch


def make_agent(**kwargs):
    """Create a SimpleNamespace object that behaves like an AIAgent model."""
    defaults = {
        "id": "ai_agent_123",
        "name": "Test Agent",
        "description": "Test description",
        "system_prompt": "Test prompt",
        "model": "claude-haiku-4-5",
        "temperature": 0.5,
        "is_default": False,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


class TestCreateAIAgent:
    """Tests for POST /ai-agents endpoint."""

    def test_create_ai_agent_success(self, test_client, mock_auth, sample_ai_agent):
        """Should create a new AI agent successfully."""
        mock_repo = AsyncMock()
        mock_repo.create.return_value = make_agent(
            id="ai_agent_123",
            name=sample_ai_agent["name"],
            description=sample_ai_agent["description"],
            system_prompt=sample_ai_agent["system_prompt"],
            model=sample_ai_agent["model"],
            temperature=sample_ai_agent["temperature"],
            is_default=sample_ai_agent["is_default"],
            is_active=True,
        )

        with patch("ai_agents.router.repository", mock_repo):
            response = test_client.post("/ai-agents", json=sample_ai_agent)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "ai_agent_123"
        assert data["name"] == sample_ai_agent["name"]
        assert data["system_prompt"] == sample_ai_agent["system_prompt"]
        assert data["model"] == sample_ai_agent["model"]
        assert data["temperature"] == sample_ai_agent["temperature"]
        assert data["is_default"] is True
        assert data["is_active"] is True

    def test_create_ai_agent_validation_error(self, test_client, mock_auth):
        """Should return 422 for invalid data."""
        invalid_data = {
            "name": "",  # Empty name should fail
            "system_prompt": "test",
        }

        response = test_client.post("/ai-agents", json=invalid_data)
        assert response.status_code == 422

    def test_create_ai_agent_missing_required_fields(self, test_client, mock_auth):
        """Should return 422 when required fields are missing."""
        incomplete_data = {
            "name": "Test Agent",
            # Missing system_prompt
        }

        response = test_client.post("/ai-agents", json=incomplete_data)
        assert response.status_code == 422


class TestListAIAgents:
    """Tests for GET /ai-agents endpoint."""

    def test_list_ai_agents_success(self, test_client, mock_auth):
        """Should return list of AI agents."""
        mock_agents = [
            make_agent(
                id="ai_agent_1",
                name="Agent 1",
                description="First agent",
                system_prompt="Prompt 1",
                model="claude-haiku-4-5",
                temperature=0.5,
                is_default=True,
            ),
            make_agent(
                id="ai_agent_2",
                name="Agent 2",
                description="Second agent",
                system_prompt="Prompt 2",
                model="gpt-5-nano",
                temperature=0.7,
                is_default=False,
            ),
        ]

        mock_repo = AsyncMock()
        mock_repo.list_all.return_value = mock_agents

        with patch("ai_agents.router.repository", mock_repo):
            response = test_client.get("/ai-agents")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "ai_agent_1"
        assert data[1]["id"] == "ai_agent_2"

    def test_list_ai_agents_empty(self, test_client, mock_auth):
        """Should return empty list when no agents exist."""
        mock_repo = AsyncMock()
        mock_repo.list_all.return_value = []

        with patch("ai_agents.router.repository", mock_repo):
            response = test_client.get("/ai-agents")

        assert response.status_code == 200
        data = response.json()
        assert data == []


class TestGetAIAgent:
    """Tests for GET /ai-agents/{id} endpoint."""

    def test_get_ai_agent_success(self, test_client, mock_auth, sample_ai_agent):
        """Should return a specific AI agent."""
        mock_agent = make_agent(
            id="ai_agent_123",
            name=sample_ai_agent["name"],
            description=sample_ai_agent["description"],
            system_prompt=sample_ai_agent["system_prompt"],
            model=sample_ai_agent["model"],
            temperature=sample_ai_agent["temperature"],
            is_default=True,
        )

        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_agent

        with patch("ai_agents.router.repository", mock_repo):
            response = test_client.get("/ai-agents/ai_agent_123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "ai_agent_123"
        assert data["name"] == sample_ai_agent["name"]

    def test_get_ai_agent_not_found(self, test_client, mock_auth):
        """Should return 404 when agent not found."""
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None

        with patch("ai_agents.router.repository", mock_repo):
            response = test_client.get("/ai-agents/nonexistent_id")

        assert response.status_code == 404


class TestUpdateAIAgent:
    """Tests for PUT /ai-agents/{id} endpoint."""

    def test_update_ai_agent_success(self, test_client, mock_auth, sample_ai_agent_update):
        """Should update an AI agent successfully."""
        mock_agent = make_agent(
            id="ai_agent_123",
            name=sample_ai_agent_update["name"],
            description="Original description",
            system_prompt="Original prompt",
            model="claude-haiku-4-5",
            temperature=sample_ai_agent_update["temperature"],
            is_default=True,
            updated_at=datetime.now(),
        )

        mock_repo = AsyncMock()
        mock_repo.update.return_value = mock_agent

        with patch("ai_agents.router.repository", mock_repo):
            response = test_client.put("/ai-agents/ai_agent_123", json=sample_ai_agent_update)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_ai_agent_update["name"]
        assert data["temperature"] == sample_ai_agent_update["temperature"]

    def test_update_ai_agent_not_found(self, test_client, mock_auth, sample_ai_agent_update):
        """Should return 404 when agent not found."""
        mock_repo = AsyncMock()
        mock_repo.update.return_value = None

        with patch("ai_agents.router.repository", mock_repo):
            response = test_client.put("/ai-agents/nonexistent_id", json=sample_ai_agent_update)

        assert response.status_code == 404


class TestDeleteAIAgent:
    """Tests for DELETE /ai-agents/{id} endpoint."""

    def test_delete_ai_agent_success(self, test_client, mock_auth):
        """Should delete an AI agent successfully."""
        mock_repo = AsyncMock()
        mock_repo.delete.return_value = True

        with patch("ai_agents.router.repository", mock_repo):
            response = test_client.delete("/ai-agents/ai_agent_123")

        assert response.status_code == 204

    def test_delete_ai_agent_not_found(self, test_client, mock_auth):
        """Should return 404 when agent not found."""
        mock_repo = AsyncMock()
        mock_repo.delete.return_value = False

        with patch("ai_agents.router.repository", mock_repo):
            response = test_client.delete("/ai-agents/nonexistent_id")

        assert response.status_code == 404


class TestSetDefaultAIAgent:
    """Tests for PUT /ai-agents/{id}/default endpoint."""

    def test_set_default_ai_agent_success(self, test_client, mock_auth):
        """Should set an AI agent as default."""
        mock_agent = make_agent(
            id="ai_agent_123",
            name="Test Agent",
            description="Test",
            system_prompt="Prompt",
            is_default=True,
            updated_at=datetime.now(),
        )

        mock_repo = AsyncMock()
        mock_repo.set_default.return_value = mock_agent

        with patch("ai_agents.router.repository", mock_repo):
            response = test_client.put("/ai-agents/ai_agent_123/default")

        assert response.status_code == 200
        data = response.json()
        assert data["is_default"] is True

    def test_set_default_ai_agent_not_found(self, test_client, mock_auth):
        """Should return 404 when agent not found."""
        mock_repo = AsyncMock()
        mock_repo.set_default.return_value = None

        with patch("ai_agents.router.repository", mock_repo):
            response = test_client.put("/ai-agents/nonexistent_id/default")

        assert response.status_code == 404
