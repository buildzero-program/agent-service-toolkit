# Changelog

All notable changes to this fork of agent-service-toolkit.

## Unreleased

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
