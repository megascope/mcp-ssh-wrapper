# mcp-ssh-wrapper

`mcp-ssh-wrapper` is a minimal MCP server that executes commands on remote hosts by delegating to the local `ssh` binary.

The server does not implement SSH authentication. It relies entirely on the host machine's existing SSH configuration, agent, identities, and host key policy.

This project runs as a streamable HTTP MCP server. It is intended to be started as a long-lived local process and then connected to by tools like Codex or Claude.

The SSH execution path is non-interactive. The server runs `ssh` in batch mode and does not allow prompts on stdin, so hosts must already be reachable using existing SSH config, keys, agent state, and known-hosts entries.

Warning: binding this server to anything other than `localhost` or `127.0.0.1` exposes a tool that can use the local machine's SSH configuration, agent, and keys over the network. Treat non-local binding as a high-risk configuration.

## Features

- Exposes a single MCP tool: `execute_command`
- Uses the system `ssh` command directly
- Returns `stdout`, `stderr`, and `exit_code`
- Supports an optional execution timeout

## Installation

```bash
pip install mcp-ssh-wrapper
```

## Running the server

After installation, run the server with:

```bash
mcp-ssh-wrapper --host 127.0.0.1 --port 8000 --mount-path /mcp
```

This exposes the MCP endpoint at `http://127.0.0.1:8000/mcp`.

You can also use the module entrypoint:

```bash
python -m mcp_ssh_wrapper --host 127.0.0.1 --port 8000 --mount-path /mcp
```

Keep this bound to localhost unless you fully understand the security implications.

### Local execution

For local development from this repository, use the helper script:

```bash
./run_server.sh --host 127.0.0.1 --port 8000 --mount-path /mcp
```

If your SSH setup depends on `ssh-agent`, `run_server.sh` will try to recover `SSH_AUTH_SOCK` automatically on macOS.

## Add to Codex

Start the server first:

```bash
mcp-ssh-wrapper --host 127.0.0.1 --port 8000 --mount-path /mcp
```

Then register the running HTTP endpoint with Codex:

```bash
codex mcp add mcp-ssh --url http://127.0.0.1:8000/mcp
```

Verify the registration:

```bash
codex mcp list
codex mcp get mcp-ssh
```

Codex will connect to the running HTTP endpoint. It does not launch the server process for you in this setup.

## Add to Claude

### Claude Code CLI

Start the server first, then register the URL with Claude Code:

```bash
claude mcp add mcp-ssh --transport http http://127.0.0.1:8000/mcp
```

Verify the registration:

```bash
claude mcp list
claude mcp get mcp-ssh
```

### Claude Desktop

Add this server entry to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-ssh": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

Claude Desktop will connect to the running local HTTP server.

## Important limitation

`run_test.sh` does not launch the server. Start `mcp-ssh-wrapper ...` or `./run_server.sh ...` first, then run the test wrapper against the live endpoint.

## Local smoke test

To verify startup, MCP initialization, and tool discovery against a running server:

```bash
./run_test.sh --skip-call
```

To target a non-default endpoint:

```bash
./run_test.sh --url http://127.0.0.1:8000/mcp --skip-call
```

To also invoke the SSH tool:

```bash
./run_test.sh --host my-host --command "uname -a"
```

## Tool

### `execute_command`

Arguments:

- `host`: SSH host or `user@host`, resolved by the local SSH client
- `command`: Command string to execute remotely
- `timeout_seconds`: Optional timeout. `0` disables timeout handling.

Result:

```json
{
  "host": "prod-box",
  "command": "uname -a",
  "stdout": "Linux ...\n",
  "stderr": "",
  "exit_code": 0
}
```

## Notes

- SSH options should be configured in `~/.ssh/config` or the host environment.
- This server invokes `ssh -o BatchMode=yes`, so password prompts and interactive confirmations are disabled.
- Authentication, host key policy, and identity selection are still handled by the local `ssh` client and its existing configuration.

## Releasing

This project is configured to publish to PyPI using GitHub Trusted Publishing via [.github/workflows/publish-pypi.yml](mcp-ssh-wrapper/.github/workflows/publish-pypi.yml).

Release flow:

1. Update `project.version` in [pyproject.toml](mcp-ssh-wrapper/pyproject.toml).
2. Commit the version bump and push it to `main`.
3. Tag the `main` commit with a matching version tag in the form `vX.Y.Z`.
4. Push the tag to GitHub.

Example for version `0.1.0`:

```bash
git checkout main
git pull
git tag v0.1.0
git push origin v0.1.0
```

The GitHub Actions workflow will:

- verify the tag points to a commit on `main`
- verify the tag matches `project.version`
- build the package
- publish it to PyPI using the GitHub `pypi` environment
