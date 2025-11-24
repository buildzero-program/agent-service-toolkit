#!/bin/bash
# =============================================================================
# Setup GitHub Secrets for agent-service-toolkit
# =============================================================================
# Usage: ./scripts/setup-secrets.sh [.env file path]
#
# Prerequisites:
#   - gh CLI installed and authenticated (gh auth login)
#   - Inside the repo directory or set GH_REPO env var
#
# Required files:
#   - .env file with your API keys
#   - SSH private key for VPS access
#
# What this script does:
#   1. Creates 'production' environment in GitHub
#   2. Adds VPS secrets to production environment
#   3. Adds API keys to production environment
#   4. Optionally sets up VPS (creates directory, copies compose, GHCR login)
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Agent Service Toolkit - GitHub Secrets Setup          ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}\n"

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: gh CLI is not installed${NC}"
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with gh CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Get repo info
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null || echo "")
if [ -z "$REPO" ]; then
    echo -e "${RED}Error: Not in a GitHub repository${NC}"
    exit 1
fi
echo -e "${BLUE}Repository: $REPO${NC}\n"

# Load .env file
ENV_FILE="${1:-.env}"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: .env file not found at $ENV_FILE${NC}"
    echo "Usage: $0 [path-to-env-file]"
    exit 1
fi

echo -e "${YELLOW}Loading environment from: $ENV_FILE${NC}\n"

# Function to get value from .env
get_env_value() {
    local key=$1
    grep "^${key}=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2- | sed 's/^"//' | sed 's/"$//' || echo ""
}

# Function to set secret in production environment
set_secret() {
    local name=$1
    local value=$2

    if [ -n "$value" ] && [ "$value" != "" ]; then
        printf "  %-25s " "$name"
        if gh secret set "$name" --env production --body "$value" 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
        fi
    else
        printf "  %-25s ${YELLOW}skipped (empty)${NC}\n" "$name"
    fi
}

# =============================================================================
# Create production environment
# =============================================================================
echo -e "${GREEN}[1/4] Creating production environment...${NC}"
if gh api -X PUT "/repos/$REPO/environments/production" 2>/dev/null; then
    echo -e "  Environment 'production' ${GREEN}✓${NC}\n"
else
    echo -e "  Environment already exists ${GREEN}✓${NC}\n"
fi

# =============================================================================
# VPS Secrets (required for deployment)
# =============================================================================
echo -e "${GREEN}[2/4] VPS Configuration${NC}"

read -p "  VPS Host IP: " VPS_HOST
read -p "  VPS Username [root]: " VPS_USER
VPS_USER=${VPS_USER:-root}
read -p "  SSH Private Key Path: " SSH_KEY_PATH

# Expand ~ to home directory
SSH_KEY_PATH="${SSH_KEY_PATH/#\~/$HOME}"

if [ -f "$SSH_KEY_PATH" ]; then
    set_secret "VPS_HOST" "$VPS_HOST"
    set_secret "VPS_USER" "$VPS_USER"
    printf "  %-25s " "VPS_SSH_KEY"
    if gh secret set VPS_SSH_KEY --env production < "$SSH_KEY_PATH" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
else
    echo -e "  ${RED}SSH key not found at: $SSH_KEY_PATH${NC}"
    exit 1
fi

# =============================================================================
# API Keys (from .env)
# =============================================================================
echo -e "\n${GREEN}[3/4] API Keys & Observability${NC}"

set_secret "OPENAI_API_KEY" "$(get_env_value OPENAI_API_KEY)"
set_secret "ANTHROPIC_API_KEY" "$(get_env_value ANTHROPIC_API_KEY)"
set_secret "GOOGLE_API_KEY" "$(get_env_value GOOGLE_API_KEY)"
set_secret "GROQ_API_KEY" "$(get_env_value GROQ_API_KEY)"
set_secret "OPENROUTER_API_KEY" "$(get_env_value OPENROUTER_API_KEY)"
set_secret "DEEPSEEK_API_KEY" "$(get_env_value DEEPSEEK_API_KEY)"
set_secret "LANGSMITH_API_KEY" "$(get_env_value LANGSMITH_API_KEY)"

# Auth secret
AUTH_SECRET=$(get_env_value AUTH_SECRET)
if [ -z "$AUTH_SECRET" ]; then
    echo -e "\n  AUTH_SECRET not set. Generate random? [y/N]: \c"
    read -r GENERATE
    if [ "$GENERATE" = "y" ] || [ "$GENERATE" = "Y" ]; then
        AUTH_SECRET=$(openssl rand -hex 32)
        echo -e "  Generated: ${BLUE}$AUTH_SECRET${NC}"
    fi
fi
set_secret "AUTH_SECRET" "$AUTH_SECRET"

# =============================================================================
# VPS Setup (optional)
# =============================================================================
echo -e "\n${GREEN}[4/4] VPS Setup (optional)${NC}"
echo -e "  Configure VPS now? [y/N]: \c"
read -r SETUP_VPS

if [ "$SETUP_VPS" = "y" ] || [ "$SETUP_VPS" = "Y" ]; then
    echo -e "\n  ${YELLOW}Setting up VPS...${NC}"

    # Create directory and copy compose
    ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "${VPS_USER}@${VPS_HOST}" "mkdir -p /opt/agent-service-toolkit" 2>/dev/null
    scp -i "$SSH_KEY_PATH" compose.prod.yaml "${VPS_USER}@${VPS_HOST}:/opt/agent-service-toolkit/" 2>/dev/null

    # Login to GHCR
    echo -e "  ${YELLOW}Logging into GHCR on VPS...${NC}"
    GH_TOKEN=$(gh auth token)
    GH_USER=$(gh api user -q '.login')
    ssh -i "$SSH_KEY_PATH" "${VPS_USER}@${VPS_HOST}" "echo '$GH_TOKEN' | docker login ghcr.io -u $GH_USER --password-stdin" 2>/dev/null

    echo -e "  VPS setup ${GREEN}complete ✓${NC}"
fi

# =============================================================================
# Summary
# =============================================================================
echo -e "\n${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Setup Complete!                        ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}Secrets in 'production' environment:${NC}"
gh secret list --env production

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Make sure your GHCR package is public:"
echo -e "     ${BLUE}https://github.com/orgs/$(echo $REPO | cut -d'/' -f1)/packages${NC}"
echo -e "  2. Configure DNS: agent.buildzero.ai → $VPS_HOST"
echo -e "  3. Deploy:"
echo -e "     ${BLUE}git push origin main${NC}"
echo -e "     or: ${BLUE}gh workflow run deploy.yml${NC}"
echo -e "\n${GREEN}Done!${NC}"
