from unittest import mock

from windows_use.tools.ps_shell import PowerShellManager


def test_powershell_command_list_and_env(monkeypatch):
    monkeypatch.setattr(
        PowerShellManager, "_validate_powershell_available", lambda self: True
    )
    manager = PowerShellManager()

    def fake_run(cmd, capture_output, text, timeout, cwd, env):
        assert isinstance(cmd, list)
        assert cmd[0] == "powershell"
        assert env.get("__PSLockdownPolicy") == "4"

        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        return R()

    with mock.patch("subprocess.run", fake_run):
        manager.execute_command("Get-Process")
