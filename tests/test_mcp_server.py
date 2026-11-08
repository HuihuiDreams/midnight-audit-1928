import pytest
import json
from src.backend.mcp_server import handle_json_rpc, list_tools, call_tool
from src.backend.puzzle_state import PuzzleEngine

@pytest.fixture(autouse=True)
def reset_mcp_engine():
    import os
    from src.backend.puzzle_state import PuzzleEngine, GAME_STATE_FILE
    import src.backend.mcp_server as mcp
    if os.path.exists(GAME_STATE_FILE):
        try:
            os.remove(GAME_STATE_FILE)
        except Exception:
            pass
    mcp.engine = PuzzleEngine()

def test_list_tools():
    tools = list_tools()
    tool_names = [t["name"] for t in tools]
    assert "inspect_ledger" in tool_names
    assert "haunt_spreadsheet" in tool_names
    assert "judge_ritual" in tool_names

def test_call_inspect_ledger():
    res = call_tool("inspect_ledger", {})
    assert "content" in res
    text = res["content"][0]["text"]
    assert "Current Phase: 1" in text
    assert "Wilbur Whateley" in text

def test_call_inspect_ledger_include_anomalies():
    res = call_tool("inspect_ledger", {"include_anomalies": True})
    assert "content" in res
    text = res["content"][0]["text"]
    assert "[SUPERNATURAL ANOMALY DOSSIER]" in text
    assert "Wilbur V. Whateley" in text
    assert "W34:X35" in text
    assert "SEAL THE DEEP VAULT" in text

def test_call_inspect_ledger_target_range():
    res = call_tool("inspect_ledger", {"target_range": "H7"})
    text = res["content"][0]["text"]
    assert "H7" in text

def test_cross_process_shared_state_sync():
    # Simulate server changing state to Phase 2
    from src.backend.puzzle_state import PuzzleEngine
    srv_engine = PuzzleEngine()
    srv_engine.handle_cell_change("H7", "7.00")
    assert srv_engine.phase_number == 2

    # MCP tool inspect_ledger should observe Phase 2 through game_state.json
    res = call_tool("inspect_ledger", {})
    text = res["content"][0]["text"]
    assert "Current Phase: 2" in text
    assert "Row 13 Awakened: True" in text

def test_call_haunt_spreadsheet():
    res = call_tool("haunt_spreadsheet", {"haunt_type": "cell_text", "target_cell": "B18", "message": "YOUR SOUL IS OVERDUE"})
    text = res["content"][0]["text"]
    assert "Queued" in text

def test_call_judge_ritual():
    res_fail = call_tool("judge_ritual", {"phrase": "PLEASE GO AWAY"})
    assert "MISMATCHED DEBIT" in res_fail["content"][0]["text"]

    res_success = call_tool("judge_ritual", {"phrase": "SEAL THE DEEP VAULT"})
    assert "ARCHIVE SEALED" in res_success["content"][0]["text"]

def test_json_rpc_initialize():
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    resp = handle_json_rpc(req)
    assert resp["id"] == 1
    assert "serverInfo" in resp["result"]
    assert resp["result"]["serverInfo"]["name"] == "midnight-audit-mcp"

def test_json_rpc_tools_list():
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    resp = handle_json_rpc(req)
    assert resp["id"] == 2
    assert "tools" in resp["result"]
    assert len(resp["result"]["tools"]) == 3

def test_json_rpc_tools_call():
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "judge_ritual",
            "arguments": {
                "phrase": "SEAL THE DEEP VAULT"
            }
        }
    }
    resp = handle_json_rpc(req)
    assert resp["id"] == 3
    assert "content" in resp["result"]
    assert "ARCHIVE SEALED" in resp["result"]["content"][0]["text"]
