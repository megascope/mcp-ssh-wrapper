from __future__ import annotations

from dataclasses import asdict, dataclass
import subprocess


@dataclass(frozen=True)
class SSHCommandResult:
    host: str
    command: str
    stdout: str
    stderr: str
    exit_code: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def execute_ssh_command(host: str, command: str, timeout_seconds: int = 0) -> SSHCommandResult:
    if not host or not host.strip():
        raise ValueError("host must be a non-empty string")
    if not command or not command.strip():
        raise ValueError("command must be a non-empty string")
    if timeout_seconds < 0:
        raise ValueError("timeout_seconds must be >= 0")

    # MCP stdio servers must not let child processes read from the same stdin pipe.
    # BatchMode forces ssh to fail instead of prompting for passwords or confirmations.
    ssh_command = ["ssh", "-o", "BatchMode=yes", host, command]
    timeout = None if timeout_seconds == 0 else timeout_seconds

    try:
        completed = subprocess.run(
            ssh_command,
            capture_output=True,
            text=True,
            check=False,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("ssh binary was not found on the host") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"ssh command timed out after {timeout_seconds} seconds"
        ) from exc

    return SSHCommandResult(
        host=host,
        command=command,
        stdout=completed.stdout,
        stderr=completed.stderr,
        exit_code=completed.returncode,
    )
