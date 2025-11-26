# Changelog

All notable changes to this fork of agent-service-toolkit.

## Unreleased

### Added
- `compose.local.yaml` - Local development compose (uses Neon PostgreSQL, no local postgres)
- AUTH_SECRET authentication configured

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
