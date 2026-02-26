#!/bin/bash
# =============================================================================
# deploy.sh — Pull latest code for the current branch and redeploy the API
#
# Usage:
#   ./deploy.sh              → redeploy current branch
#   ./deploy.sh feature-xyz  → switch to feature-xyz and redeploy
# =============================================================================

set -euo pipefail

# ── Colour helpers ─────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${GREEN}[deploy]${NC} $*"; }
warn()    { echo -e "${YELLOW}[deploy]${NC} $*"; }
error()   { echo -e "${RED}[deploy]${NC} $*" >&2; exit 1; }

# ── Resolve script location (works even when run from another dir) ─────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Optional: switch branch ────────────────────────────────────────────────────
if [[ $# -gt 0 ]]; then
  TARGET_BRANCH="$1"
  CURRENT_BRANCH="$(git branch --show-current)"
  if [[ "$CURRENT_BRANCH" != "$TARGET_BRANCH" ]]; then
    info "Switching from '$CURRENT_BRANCH' → '$TARGET_BRANCH'"
    git fetch origin
    git checkout "$TARGET_BRANCH"
  fi
fi

BRANCH="$(git branch --show-current)"
info "Branch: $BRANCH"

# ── Pull latest code ───────────────────────────────────────────────────────────
info "Pulling latest changes..."
git pull origin "$BRANCH"

# ── Stop existing container (graceful, keeps the volume) ──────────────────────
info "Stopping current container..."
docker compose down --remove-orphans || warn "No running container to stop."

# ── Build fresh image ─────────────────────────────────────────────────────────
info "Building image..."
docker compose build --no-cache

# ── Start container ───────────────────────────────────────────────────────────
info "Starting container..."
docker compose up -d

# ── Health check ─────────────────────────────────────────────────────────────
PORT="${PORT:-8105}"
info "Waiting for API to come up on port $PORT..."
for i in {1..20}; do
  if curl -sf "http://localhost:$PORT/" > /dev/null 2>&1; then
    echo ""
    info "✅  API is up and running → http://localhost:$PORT"
    info "    Swagger docs           → http://localhost:$PORT/docs"
    docker compose logs --tail=10 api
    exit 0
  fi
  printf '.'
  sleep 2
done

echo ""
error "❌  API did not respond on port $PORT after 40 seconds. Check logs:\n    docker compose logs api"
