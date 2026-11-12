import json
from src.backend.mcp_server import handle_json_rpc, list_tools, call_tool
from src.backend.puzzle_state import PuzzleEngine

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

    import src.backend.mcp_server as mcp
    from src.backend.puzzle_state import PhaseEnum
    mcp.engine.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT
    mcp.engine.save_state()

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
    import src.backend.mcp_server as mcp
    from src.backend.puzzle_state import PhaseEnum
    mcp.engine.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT
    mcp.engine.save_state()

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

def _tools_call(request_id, name, arguments):
    return handle_json_rpc({
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments}
    })

def test_haunt_save_failure_is_a_tool_error_not_a_protocol_error(break_disk):
    break_disk()

    resp = _tools_call(10, "haunt_spreadsheet", {"haunt_type": "whisper", "message": "lost"})

    assert resp["id"] == 10
    assert "error" not in resp
    assert resp["result"]["isError"] is True
    assert "could not be saved" in resp["result"]["content"][0]["text"]

def test_ritual_save_failure_does_not_report_victory(break_disk):
    import src.backend.mcp_server as mcp
    from src.backend.puzzle_state import PhaseEnum
    mcp.engine.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT
    mcp.engine.save_state()
    break_disk()

    resp = _tools_call(11, "judge_ritual", {"phrase": "SEAL THE DEEP VAULT"})

    assert resp["result"]["isError"] is True
    assert "RITUAL SUCCESSFUL" not in resp["result"]["content"][0]["text"]
    assert mcp.engine.archive_sealed is False

def test_non_string_target_range_is_a_tool_error():
    resp = _tools_call(20, "inspect_ledger", {"target_range": 7})

    assert resp["id"] == 20
    assert "error" not in resp
    assert resp["result"]["isError"] is True
    assert "target_range" in resp["result"]["content"][0]["text"]

def test_non_object_arguments_are_a_tool_error():
    resp = _tools_call(21, "inspect_ledger", ["H7"])

    assert "error" not in resp
    assert resp["result"]["isError"] is True

def test_non_object_params_are_invalid_params():
    resp = handle_json_rpc({"jsonrpc": "2.0", "id": 22, "method": "tools/call", "params": [1]})

    assert resp["id"] == 22
    assert resp["error"]["code"] == -32602

def test_non_string_haunt_target_cell_is_a_tool_error():
    resp = _tools_call(23, "haunt_spreadsheet", {"haunt_type": "cell_text", "target_cell": 5})

    assert "error" not in resp
    assert resp["result"]["isError"] is True

def test_row_18_inspection_describes_the_control_bar_for_any_column():
    text = call_tool("inspect_ledger", {"target_range": "K18"})["content"][0]["text"]

    assert "Row 18:" in text
    assert "B18" in text and "K18:AN18" in text

def test_inspect_ledger_reports_failed_attempts():
    from src.backend.puzzle_state import PuzzleEngine
    player = PuzzleEngine()
    player.handle_cell_change("H7", "1.00")
    player.handle_cell_change("H7", "2.00")

    text = call_tool("inspect_ledger", {})["content"][0]["text"]

    assert "Failed Attempts: H7=2, B18=0" in text

def test_stdio_server_survives_non_ascii_input_under_an_ascii_locale(tmp_path):
    import os
    import subprocess
    import sys
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frames = [
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "haunt_spreadsheet",
            "arguments": {"haunt_type": "whisper", "message": "你好，审计员"}}},
        {"jsonrpc": "2.0", "id": 2, "method": "ping"},
    ]
    stdin = "".join(json.dumps(f, ensure_ascii=False) + "\n" for f in frames).encode("utf-8")
    env = dict(os.environ, PYTHONIOENCODING="ascii", GAME_STATE_FILE=str(tmp_path / "game_state.json"))

    proc = subprocess.run([sys.executable, "-m", "src.backend.mcp_server"], input=stdin,
                          cwd=project_root, env=env, capture_output=True, timeout=30)

    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")
    replies = [json.loads(line) for line in proc.stdout.decode("utf-8").splitlines()]
    assert [r["id"] for r in replies] == [1, 2]
    assert "你好，审计员" in replies[0]["result"]["content"][0]["text"]

def test_mcp_ritual_success_queues_the_concluding_actions_for_the_workbook():
    import src.backend.mcp_server as mcp
    from src.backend.puzzle_state import PhaseEnum
    mcp.engine.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT
    mcp.engine.save_state()

    resp = _tools_call(30, "judge_ritual", {"phrase": "SEAL THE DEEP VAULT"})

    assert "RITUAL SUCCESSFUL" in resp["result"]["content"][0]["text"]
    queued = PuzzleEngine(load_existing=True).pending_effects
    assert [a.get("effect") or a["command"] for a in queued] == ["THUNDER_STROBE", "SCREEN_TREMOR", "LOCK_SHEET"]

def test_mcp_ritual_rejection_queues_nothing():
    import src.backend.mcp_server as mcp
    from src.backend.puzzle_state import PhaseEnum
    mcp.engine.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT
    mcp.engine.save_state()

    _tools_call(31, "judge_ritual", {"phrase": "WRONG PHRASE"})

    assert PuzzleEngine(load_existing=True).pending_effects == []

def test_mcp_ritual_save_failure_seals_nothing_and_queues_nothing(break_disk):
    import src.backend.mcp_server as mcp
    from src.backend.puzzle_state import PhaseEnum
    mcp.engine.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT
    mcp.engine.save_state()
    break_disk()

    _tools_call(32, "judge_ritual", {"phrase": "SEAL THE DEEP VAULT"})

    assert mcp.engine.archive_sealed is False
    assert mcp.engine.pending_effects == []
