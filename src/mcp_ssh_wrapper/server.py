from __future__ import annotations

import argparse
import asyncio
import logging

from mcp.server.fastmcp import FastMCP

from mcp_ssh_wrapper.ssh_wrapper import execute_ssh_command


INSTRUCTIONS = (
    "Execute commands on remote hosts by invoking the local ssh binary. "
    "Use the host environment's existing SSH config, identities, agent, and host key policy."
)

LOGGER = logging.getLogger(__name__)
LOCAL_ONLY_HOSTS = {"127.0.0.1", "localhost"}
NON_LOCAL_BIND_WARNING = (
    "Binding this server to anything other than localhost or 127.0.0.1 "
    "exposes a tool that can use the local machine's SSH configuration, agent, and keys "
    "over the network. Treat non-local binding as a high-risk configuration."
)


def build_server(host: str = "127.0.0.1", port: int = 8000, mount_path: str = "/mcp") -> FastMCP:
    mcp = FastMCP(
        name="mcp-ssh-wrapper",
        instructions=INSTRUCTIONS,
        host=host,
        port=port,
        mount_path=mount_path,
        streamable_http_path=mount_path,
    )

    @mcp.tool()
    def execute_command(host: str, command: str, timeout_seconds: int = 0) -> dict[str, object]:
        """Execute a command on a remote host through the local ssh binary."""
        return execute_ssh_command(
            host=host,
            command=command,
            timeout_seconds=timeout_seconds,
        ).to_dict()

    return mcp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the MCP SSH server.")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host for the HTTP server. Defaults to 127.0.0.1.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind port for the HTTP server. Defaults to 8000.",
    )
    parser.add_argument(
        "--mount-path",
        default="/mcp",
        help="HTTP mount path for streamable HTTP mode. Defaults to /mcp.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.host not in LOCAL_ONLY_HOSTS:
        logging.basicConfig(level=logging.INFO)
        LOGGER.warning(NON_LOCAL_BIND_WARNING)
    mcp = build_server(
        host=args.host,
        port=args.port,
        mount_path=args.mount_path,
    )
    try:
        mcp.run(transport="streamable-http", mount_path=args.mount_path)
    except (KeyboardInterrupt, asyncio.CancelledError):
        return


if __name__ == "__main__":
    main()
