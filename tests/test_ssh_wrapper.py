from __future__ import annotations

import subprocess
from unittest import TestCase
from unittest.mock import patch

from mcp_ssh_server.ssh_wrapper import execute_ssh_command


class ExecuteSSHCommandTests(TestCase):
    @patch("mcp_ssh_server.ssh_wrapper.subprocess.run")
    def test_executes_via_local_ssh_binary(self, run_mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess(
            args=["ssh", "-o", "BatchMode=yes", "prod-box", "uname -a"],
            returncode=0,
            stdout="Linux\n",
            stderr="",
        )

        result = execute_ssh_command("prod-box", "uname -a")

        run_mock.assert_called_once_with(
            ["ssh", "-o", "BatchMode=yes", "prod-box", "uname -a"],
            capture_output=True,
            text=True,
            check=False,
            stdin=subprocess.DEVNULL,
            timeout=None,
        )
        self.assertEqual(result.stdout, "Linux\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.exit_code, 0)

    @patch("mcp_ssh_server.ssh_wrapper.subprocess.run")
    def test_passes_timeout_when_requested(self, run_mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess(
            args=["ssh", "-o", "BatchMode=yes", "prod-box", "hostname"],
            returncode=0,
            stdout="prod-box\n",
            stderr="",
        )

        execute_ssh_command("prod-box", "hostname", timeout_seconds=5)

        self.assertEqual(run_mock.call_args.kwargs["timeout"], 5)
        self.assertEqual(run_mock.call_args.kwargs["stdin"], subprocess.DEVNULL)

    def test_rejects_empty_host(self) -> None:
        with self.assertRaisesRegex(ValueError, "host must be a non-empty string"):
            execute_ssh_command("", "hostname")

    def test_rejects_empty_command(self) -> None:
        with self.assertRaisesRegex(ValueError, "command must be a non-empty string"):
            execute_ssh_command("prod-box", "")
