import json
import os

from src.backend.mcp_server import handle_json_rpc
from src.backend.server import app

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASE_VERSION = "1.3.0"


def _load_json(*parts):
    with open(os.path.join(PROJECT_ROOT, *parts), encoding="utf-8") as f:
        return json.load(f)


def test_mcp_server_reports_release_version():
    resp = handle_json_rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["result"]["serverInfo"]["version"] == RELEASE_VERSION


def test_daemon_reports_release_version():
    assert app.version == RELEASE_VERSION


def test_changelog_has_release_section():
    with open(os.path.join(PROJECT_ROOT, "CHANGELOG.md"), encoding="utf-8") as f:
        text = f.read()
    assert f"## [{RELEASE_VERSION}] - 2026-11-12" in text


def test_kiro_mcp_settings():
    server = _load_json(".kiro", "settings", "mcp.json")["mcpServers"]["midnight-audit-mcp"]
    assert server["command"] == "uv"
    assert server["args"] == [
        "run",
        "--with-requirements",
        "requirements.txt",
        "python",
        "-m",
        "src.backend.mcp_server",
    ]
    assert server["disabled"] is False
    assert set(server["autoApprove"]) == {"inspect_ledger", "haunt_spreadsheet", "judge_ritual"}


def test_kiro_verification_hook():
    hook = _load_json(".kiro", "hooks", "verify-backend-and-ledger.json")["hooks"][0]
    assert hook["trigger"] == "PostFileSave"
    assert hook["action"]["command"] == (
        "uv run --with-requirements requirements.txt python -m pytest -q "
        "&& uv run --with-requirements requirements.txt python scripts/build_ledger.py"
    )


def test_kiro_spec_folder_complete():
    spec_dir = os.path.join(PROJECT_ROOT, ".kiro", "specs")
    for name in ("requirements.md", "design.md", "tasks.md"):
        assert os.path.isfile(os.path.join(spec_dir, "midnight-audit", name))
    for legacy in ("mcp_contract.md", "puzzle_engine_spec.md"):
        assert os.path.isfile(os.path.join(spec_dir, legacy))
