#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smoke-test a running mcp-ssh-server over streamable HTTP."
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000/mcp",
        help="MCP streamable HTTP endpoint. Defaults to http://127.0.0.1:8000/mcp.",
    )
    parser.add_argument("--host", help="Remote SSH host to target for execute_command.")
    parser.add_argument("--command", help="Remote command to execute.")
    parser.add_argument(
        "--skip-call",
        action="store_true",
        help="Only initialize the server and list tools.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=0,
        help="Timeout forwarded to execute_command.",
    )
    return parser.parse_args()


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    return value


def dump_message(title: str, message: Any) -> None:
    print(f"== {title} ==")
    print(json.dumps(to_jsonable(message), indent=2, sort_keys=True))


async def run() -> int:
    args = parse_args()

    async with streamablehttp_client(args.url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            initialize = await session.initialize()
            dump_message("initialize", initialize)

            tools = await session.list_tools()
            dump_message("tools/list", tools)

            if not args.skip_call:
                if not args.host or not args.command:
                    raise SystemExit("--host and --command are required unless --skip-call is used")

                call = await session.call_tool(
                    "execute_command",
                    {
                        "host": args.host,
                        "command": args.command,
                        "timeout_seconds": args.timeout_seconds,
                    },
                )
                dump_message("tools/call", call)

    return 0


def main() -> int:
    return asyncio.run(run())


if __name__ == "__main__":
    raise SystemExit(main())
