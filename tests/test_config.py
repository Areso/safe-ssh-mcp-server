"""Tests for load_config()."""
import mcp_ssh


class TestLoadConfig:

    def test_full_config(self, tmp_path, monkeypatch):
        config = tmp_path / "mcp_config.ini"
        config.write_text("[server]\ntransport=sse\nhost=0.0.0.0\nport=9000\n")
        monkeypatch.setattr(mcp_ssh, "__file__", str(tmp_path / "mcp_ssh.py"))

        result = mcp_ssh.load_config()
        assert result["transport"] == "sse"
        assert result["host"] == "0.0.0.0"
        assert result["port"] == "9000"

    def test_partial_config_keeps_defaults(self, tmp_path, monkeypatch):
        config = tmp_path / "mcp_config.ini"
        config.write_text("[server]\ntransport=sse\n")
        monkeypatch.setattr(mcp_ssh, "__file__", str(tmp_path / "mcp_ssh.py"))

        result = mcp_ssh.load_config()
        assert result["transport"] == "sse"
        assert result["host"] == "127.0.0.1"
        assert result["port"] == "8000"

    def test_missing_config_returns_defaults(self, tmp_path, monkeypatch):
        monkeypatch.setattr(mcp_ssh, "__file__", str(tmp_path / "mcp_ssh.py"))

        result = mcp_ssh.load_config()
        assert result == {"transport": "stdio", "host": "127.0.0.1", "port": "8000"}

    def test_empty_config_no_server_section(self, tmp_path, monkeypatch):
        config = tmp_path / "mcp_config.ini"
        config.write_text("[other]\nfoo=bar\n")
        monkeypatch.setattr(mcp_ssh, "__file__", str(tmp_path / "mcp_ssh.py"))

        result = mcp_ssh.load_config()
        assert result == {"transport": "stdio", "host": "127.0.0.1", "port": "8000"}

    def test_extra_keys_included(self, tmp_path, monkeypatch):
        config = tmp_path / "mcp_config.ini"
        config.write_text("[server]\ntransport=stdio\ncustom_key=hello\n")
        monkeypatch.setattr(mcp_ssh, "__file__", str(tmp_path / "mcp_ssh.py"))

        result = mcp_ssh.load_config()
        assert result["custom_key"] == "hello"
