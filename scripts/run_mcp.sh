#!/usr/bin/env bash
# Starts the patent-client-agents MCP server with credentials from ideacheck/.env (if present).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -f "$ROOT/.env" ]]; then set -a; source "$ROOT/.env"; set +a; fi
exec "$ROOT/.venv/bin/patent-client-agents-mcp" "$@"
