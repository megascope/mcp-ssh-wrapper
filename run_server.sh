#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")" && pwd)"
cd "$repo_root"

# If started outside an interactive shell, recover the macOS ssh-agent socket.
if [[ -z "${SSH_AUTH_SOCK:-}" ]] && command -v launchctl >/dev/null 2>&1; then
  ssh_auth_sock="$(launchctl getenv SSH_AUTH_SOCK 2>/dev/null || true)"
  if [[ -n "$ssh_auth_sock" ]]; then
    export SSH_AUTH_SOCK="$ssh_auth_sock"
  fi
fi

exec uv run --python 3.10 --with mcp mcp-ssh-wrapper "$@"
