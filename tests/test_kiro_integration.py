import json
import os

from src.backend.mcp_server import handle_json_rpc
from src.backend.server import app

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASE_VERSION = "1.3.1"


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
        "uv run --with-requirements requirements-dev.txt python -m pytest -q "
        "&& uv run --with-requirements requirements.txt python scripts/build_ledger.py"
    )


def _requirement_names(filename):
    with open(os.path.join(PROJECT_ROOT, filename), encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return lines


def test_runtime_requirements_exclude_test_tooling():
    runtime = " ".join(_requirement_names("requirements.txt"))
    for needed in ("fastapi", "uvicorn", "openpyxl", "pydantic"):
        assert needed in runtime
    for dev_only in ("pytest", "httpx"):
        assert dev_only not in runtime


def test_dev_requirements_extend_runtime_requirements():
    dev = _requirement_names("requirements-dev.txt")
    assert "-r requirements.txt" in dev
    assert any(line.startswith("pytest") for line in dev)
    assert any(line.startswith("httpx") for line in dev)


def test_kiro_spec_folder_complete():
    spec_dir = os.path.join(PROJECT_ROOT, ".kiro", "specs")
    for name in ("requirements.md", "design.md", "tasks.md"):
        assert os.path.isfile(os.path.join(spec_dir, "midnight-audit", name))
    for legacy in ("mcp_contract.md", "puzzle_engine_spec.md"):
        assert os.path.isfile(os.path.join(spec_dir, legacy))
