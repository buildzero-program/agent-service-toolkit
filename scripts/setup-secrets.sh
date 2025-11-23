#!/bin/bash
# =============================================================================
# Setup GitHub Secrets for agent-service-toolkit
# =============================================================================
# Usage: ./scripts/setup-secrets.sh
#
# Prerequisites:
#   - gh CLI installed and authenticated (gh auth login)
#   - Inside the repo directory or set GH_REPO env var
#
# Required files:
#   - .env file with your API keys
#   - SSH private key for VPS access
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Agent Service Toolkit - GitHub Secrets Setup ===${NC}\n"

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
    grep "^${key}=" "$ENV_FILE" | cut -d'=' -f2- | sed 's/^"//' | sed 's/"$//'
}

# Function to set secret if value exists
set_secret() {
    local name=$1
    local value=$2

    if [ -n "$value" ] && [ "$value" != "" ]; then
        echo -n "Setting $name... "
        gh secret set "$name" --body "$value" 2>/dev/null && echo -e "${GREEN}OK${NC}" || echo -e "${RED}FAILED${NC}"
    else
        echo -e "Skipping $name (empty)"
    fi
}

# =============================================================================
# VPS Secrets (required for deployment)
# =============================================================================
echo -e "\n${GREEN}--- VPS Configuration ---${NC}"

read -p "VPS Host IP: " VPS_HOST
read -p "VPS Username [root]: " VPS_USER
VPS_USER=${VPS_USER:-root}
read -p "SSH Private Key Path: " SSH_KEY_PATH

if [ -f "$SSH_KEY_PATH" ]; then
    set_secret "VPS_HOST" "$VPS_HOST"
    set_secret "VPS_USER" "$VPS_USER"
    echo -n "Setting VPS_SSH_KEY... "
    gh secret set VPS_SSH_KEY < "$SSH_KEY_PATH" && echo -e "${GREEN}OK${NC}" || echo -e "${RED}FAILED${NC}"
else
    echo -e "${RED}SSH key not found at: $SSH_KEY_PATH${NC}"
fi

# =============================================================================
# API Keys (from .env)
# =============================================================================
echo -e "\n${GREEN}--- API Keys ---${NC}"

set_secret "OPENAI_API_KEY" "$(get_env_value OPENAI_API_KEY)"
set_secret "ANTHROPIC_API_KEY" "$(get_env_value ANTHROPIC_API_KEY)"
set_secret "GOOGLE_API_KEY" "$(get_env_value GOOGLE_API_KEY)"
set_secret "GROQ_API_KEY" "$(get_env_value GROQ_API_KEY)"
set_secret "OPENROUTER_API_KEY" "$(get_env_value OPENROUTER_API_KEY)"
set_secret "DEEPSEEK_API_KEY" "$(get_env_value DEEPSEEK_API_KEY)"

# =============================================================================
# Observability
# =============================================================================
echo -e "\n${GREEN}--- Observability ---${NC}"

set_secret "LANGSMITH_API_KEY" "$(get_env_value LANGSMITH_API_KEY)"
set_secret "LANGSMITH_PROJECT" "$(get_env_value LANGSMITH_PROJECT)"

# =============================================================================
# Auth
# =============================================================================
echo -e "\n${GREEN}--- Authentication ---${NC}"

AUTH_SECRET=$(get_env_value AUTH_SECRET)
if [ -z "$AUTH_SECRET" ]; then
    echo -n "AUTH_SECRET not set. Generate random? [y/N]: "
    read -r GENERATE
    if [ "$GENERATE" = "y" ] || [ "$GENERATE" = "Y" ]; then
        AUTH_SECRET=$(openssl rand -hex 32)
        echo "Generated: $AUTH_SECRET"
    fi
fi
set_secret "AUTH_SECRET" "$AUTH_SECRET"

# =============================================================================
# Summary
# =============================================================================
echo -e "\n${GREEN}=== Secrets configured ===${NC}\n"
gh secret list

echo -e "\n${GREEN}Done!${NC}"
echo -e "Trigger deploy with: ${YELLOW}git push origin main${NC}"
echo -e "Or manually: ${YELLOW}gh workflow run deploy.yml${NC}"
