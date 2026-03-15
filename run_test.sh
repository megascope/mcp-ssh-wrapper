#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")" && pwd)"
cd "$repo_root"

exec uv run --python 3.10 --with mcp python scripts/test_http_client.py "$@"
