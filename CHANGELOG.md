# Changelog

All notable changes to this fork of agent-service-toolkit.

## Unreleased

### Added
- `max_tokens` field in AIAgent model for conversation context limit
- `trim_conversation()` function using LangChain's `trim_messages()` utility
- Token-based context limiting to prevent rate limit timeouts

### Changed
- Dynamic agent now trims conversation history based on `max_tokens` setting (default: 16000)

---

## 2025-11-27

### Fixed
- Neon database connection timeouts with retry logic (`50bec35`)
- Integration test updated for new dynamic agent welcome message (`94c21e7`)
- AI agents DB initialization made optional for test-docker (`042e319`)
- Tests updated to work with dynamic agent as default (`e9733a1`)
- Mypy type errors resolved in ai_agents module (`3a0b6b7`)
- Pytest import issues resolved for ai_agents module (`024b04d`)
- Unused imports removed in test files (`ca01e95`)
- Ruff lint errors resolved in ai_agents module (`db80019`)

### Changed
- Python files formatted with ruff (`3758b27`)

---

## 2025-11-26

### Added
- `src/ai_agents/` - Complete CRUD API module for AI agents management
  - `models.py` - SQLAlchemy models for AIAgent
  - `repository.py` - Repository pattern with SQLite persistence
  - `router.py` - FastAPI routes (GET, POST, PUT, DELETE)
  - `schemas.py` - Pydantic schemas for validation
- `src/agents/dynamic_agent.py` - DynamicAgent class for external integrations
  - Reads agent config from external API (core-agent)
  - Supports Bearer token authentication
- `/stream` endpoint now accepts `agent_id` query parameter
- Comprehensive test suite in `tests/ai_agents/`

### Changed
- Updated `src/agents/agents.py` to include DynamicAgent
- Added `httpx` dependency for external HTTP calls
- Port changed to 8180 to avoid conflicts
- Removed `compose.yaml` (replaced by compose.local.yaml)
- Removed streamlit_app service from local dev setup

---

## 2024-11-26

### Added
- `compose.prod.yaml` - Production stack for Docker Swarm with Traefik
- Traefik labels for `agent.buildzero.ai` with letsencryptresolver
- `CHANGELOG.md` to track customizations
- CI/CD: GitHub Actions deploy to VPS via SSH
- `scripts/setup-secrets.sh` - Interactive script to configure GitHub secrets

### Changed
- Database: Neon PostgreSQL (sa-east-1) instead of local container
- Network: Using external `network` (same as wuzapi stack)
- Format: Docker Swarm compatible (deploy, replicas, constraints)
- Registry: GHCR (ghcr.io) instead of Docker Hub
- Deploy: VPS via SSH instead of Azure Web App
- Triggers: main branch + tags (v*) + releases

### Configuration
- `DATABASE_TYPE=postgres` with Neon pooler
- `TZ=America/Sao_Paulo`
- LangSmith tracing enabled
- Domain: `agent.buildzero.ai`
- Resources: 2 CPU, 2GB RAM limit

### Secrets Required (GitHub)
- `VPS_HOST` - VPS IP address
- `VPS_USER` - SSH username
- `VPS_SSH_KEY` - SSH private key

---

## Upstream

Based on [JoshuaC215/agent-service-toolkit](https://github.com/JoshuaC215/agent-service-toolkit)

See upstream [README](./README.md) for original documentation.
