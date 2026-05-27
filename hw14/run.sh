#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$PROJECT_DIR/.server.pid"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}ℹ️${NC}  $1"; }
ok()    { echo -e "${GREEN}✅${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠️${NC}  $1"; }
fail()  { echo -e "${RED}❌${NC} $1"; }

usage() {
    echo "Usage: $0 {start|stop|clean|restart}"
    echo ""
    echo "  start    Start MCP server (default)"
    echo "  stop     Stop running server"
    echo "  clean    Remove cache, venv, build artifacts"
    echo "  restart  stop + clean + start"
    exit 1
}

cmd_start() {
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        fail ".env not found. Run: cp .env.example .env and edit it"
        exit 1
    fi

    # shellcheck source=/dev/null
    source "$PROJECT_DIR/.env" 2>/dev/null || true

    if [ -z "${OPENBCM_SDK_PATH:-}" ]; then
        warn "OPENBCM_SDK_PATH is not set in .env"
        echo "  Set it to your SDK path, e.g.:"
        echo "    OPENBCM_SDK_PATH=/home/user/openbcm/sdk-6.5.27"
        echo ""
    fi

    info "Starting OpenBCM Helper MCP Server..."
    cd "$PROJECT_DIR"
    uv run python -m src &
    PID=$!
    echo "$PID" > "$PID_FILE"
    ok "Server started (PID: $PID)"
}

cmd_stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        kill "$PID" 2>/dev/null || true
        rm -f "$PID_FILE"
        ok "Server stopped (PID: $PID)"
    else
        info "No running server found"
    fi
}

cmd_clean() {
    info "Cleaning project..."

    cd "$PROJECT_DIR"

    # Virtual environment
    if [ -d ".venv" ]; then
        rm -rf .venv/
        ok "Removed .venv/"
    fi

    # Cache and build artifacts
    rm -rf cache/ htmlcov/ .mypy_cache/ .ruff_cache/
    ok "Removed cache/, htmlcov/, .mypy_cache/, .ruff_cache/"

    # Python bytecode
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    ok "Removed __pycache__ and .pyc files"

    # Database files
    find . -type f -name "*.db" -delete
    ok "Removed *.db files"

    # PID file if left behind
    rm -f "$PID_FILE"

    ok "Clean complete"
}

case "${1:-start}" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    clean)
        cmd_clean
        ;;
    restart)
        cmd_stop
        cmd_clean
        cmd_start
        ;;
    *)
        usage
        ;;
esac