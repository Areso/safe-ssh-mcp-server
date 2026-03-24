"""Tests that every MCP tool handler passes the correct command to run_ssh_command."""
import pytest

import mcp_ssh


# ============================================================
# 18 simple tools — each is a thin wrapper around run_ssh_command
# ============================================================

@pytest.mark.parametrize("tool_func, expected_cmd", [
    (mcp_ssh.get_disk_free, "df -h"),
    (mcp_ssh.get_inode_usage, "df -i"),
    (mcp_ssh.get_dmesg, "dmesg"),
    (mcp_ssh.get_uptime, "uptime"),
    (mcp_ssh.get_current_datetime, "date"),
    (mcp_ssh.get_distroname_version, "cat /etc/os-release"),
    (mcp_ssh.get_systemd_list_all, "systemctl list-units --all --no-pager"),
    (mcp_ssh.get_systemd_list_failed, "systemctl list-units --state=failed --no-pager"),
    (mcp_ssh.get_systemd_list_timers, "systemctl list-timers --no-pager"),
    (mcp_ssh.get_ps_aux_top_cpu_consumers, "ps aux --sort=-%cpu | head -n 10"),
    (mcp_ssh.get_ps_aux_top_mem_consumers, "ps aux --sort=-%mem | head -n 10"),
    (mcp_ssh.get_free_memory, "free -h && echo && cat /proc/meminfo"),
    (mcp_ssh.get_memory_pressure, "cat /proc/pressure/memory 2>/dev/null || echo 'PSI not supported'"),
    (mcp_ssh.get_top, "top -b -n 1 -c"),
    (mcp_ssh.get_lsblk, "lsblk"),
    (mcp_ssh.get_docker_ps_all, "docker ps --all"),
    (mcp_ssh.get_crontab_tasks, "crontab -l"),
    (mcp_ssh.get_listening_sockets, "ss -tulpn"),
])
def test_simple_tool_sends_correct_command(tool_func, expected_cmd, mock_run_ssh_command):
    tool_func(host="testhost", user="testuser")
    mock_run_ssh_command.assert_called_once()
    actual_cmd = mock_run_ssh_command.call_args[0][2]
    assert actual_cmd == expected_cmd


# ============================================================
# Simple tools — verify SSH args are forwarded correctly
# ============================================================

def test_tool_forwards_all_ssh_args(mock_run_ssh_command):
    mcp_ssh.get_uptime(
        host="myhost",
        user="myuser",
        port=2222,
        password="secret",
        key_path="/tmp/key",
        timeout=30,
        accept_new_hostkey=True,
    )
    args, kwargs = mock_run_ssh_command.call_args
    assert args[0] == "myhost"
    assert args[1] == "myuser"
    assert args[3] == 2222
    assert args[4] == "secret"
    assert args[5] == "/tmp/key"
    assert args[6] == 30
    assert args[7] is True


def test_tool_uses_default_args(mock_run_ssh_command):
    mcp_ssh.get_uptime(host="h", user="u")
    args, kwargs = mock_run_ssh_command.call_args
    assert args[3] == 22        # port
    assert args[4] is None      # password
    assert args[5] is None      # key_path
    assert args[7] is False     # accept_new_hostkey


# ============================================================
# get_disk_usage — command building (happy path)
# ============================================================

def test_disk_usage_command_building(mock_run_ssh_command):
    mcp_ssh.get_disk_usage(host="h", user="u", abs_path="/data")
    cmd = mock_run_ssh_command.call_args[0][2]
    assert cmd.startswith("find /data ")
    assert "-mindepth 1 -maxdepth 1" in cmd
    assert "-exec du -sh" in cmd
    assert "sort -rh" in cmd
    assert "head -n 20" in cmd


# ============================================================
# get_systemd_status — command building (happy path)
# ============================================================

def test_systemd_status_command_building(mock_run_ssh_command):
    mcp_ssh.get_systemd_status(daemon="nginx", host="h", user="u")
    cmd = mock_run_ssh_command.call_args[0][2]
    assert "systemctl status" in cmd
    assert "nginx" in cmd


# ============================================================
# get_service_logs_from_journalctl — command building (happy path)
# ============================================================

def test_journalctl_command_building(mock_run_ssh_command):
    mcp_ssh.get_service_logs_from_journalctl(service="sshd", host="h", user="u", lines=100)
    cmd = mock_run_ssh_command.call_args[0][2]
    assert "journalctl -xeu" in cmd
    assert "sshd" in cmd
    assert "-n 100" in cmd
    assert "--no-pager" in cmd


def test_journalctl_default_lines(mock_run_ssh_command):
    mcp_ssh.get_service_logs_from_journalctl(service="sshd", host="h", user="u")
    cmd = mock_run_ssh_command.call_args[0][2]
    assert "-n 200" in cmd
