import os
from src.backend.puzzle_state import PuzzleEngine, PhaseEnum
from src.backend.mcp_server import call_tool, handle_json_rpc
from fastapi.testclient import TestClient
from src.backend.server import app

client = TestClient(app)

def test_engine_edge_cases():
    engine = PuzzleEngine()

    # Empty inputs and non-matching cells
    assert engine.handle_cell_change("", "")["accepted"] is False
    assert engine.handle_cell_change("ZZ999", "100")["accepted"] is False
    assert engine.handle_cell_change("H7", "")["accepted"] is False
    assert engine.handle_cell_change("H7", "-7.00")["accepted"] is False
    assert engine.handle_cell_change("H7", "0")["accepted"] is False
    assert engine.handle_cell_change("H7", None)["accepted"] is False
    assert engine.handle_cell_change("H7", "NaN")["accepted"] is False
    assert engine.handle_cell_change("H7", "Inf")["accepted"] is False

    # Calling reagent spray out of phase
    assert engine.handle_reagent_spray()["accepted"] is False

    # Calling ritual judgement with empty or strange string
    assert engine.judge_ritual("")["banished"] is False
    assert engine.judge_ritual("   ")["banished"] is False
    assert engine.judge_ritual("123456789!@#$%^&*()")["banished"] is False

    # Case-insensitivity on coordinates and values
    res = engine.handle_cell_change("h7", "  $7.00  ")
    assert res["accepted"] is True
    assert engine.current_phase == PhaseEnum.THE_UNSEEN_INTRUDER

    # Phase 2 reagent spray
    assert engine.handle_reagent_spray()["accepted"] is True
    assert engine.current_phase == PhaseEnum.HIJACKED_CIPHER

    # Second spray should now be rejected (already in Phase 3)
    assert engine.handle_reagent_spray()["accepted"] is False

    # Cell change in Phase 3 with non-B18 cell
    assert engine.handle_cell_change("A1", "TEST")["accepted"] is False

def test_mcp_edge_cases():
    # Unknown tool
    err_res = call_tool("non_existent_tool", {})
    assert err_res.get("isError") is True

    # Empty target range
    res = call_tool("inspect_ledger", {"target_range": ""})
    assert "Active Ledger Records:" in res["content"][0]["text"]

    # Unknown JSON-RPC method
    rpc_err = handle_json_rpc({"jsonrpc": "2.0", "id": 99, "method": "unknown/method"})
    assert "error" in rpc_err
    assert rpc_err["error"]["code"] == -32601

def test_server_error_paths():
    # cell_change missing cell
    res = client.post("/api/event", json={"event_type": "cell_change"})
    assert res.status_code == 400

    # Unknown event type
    res = client.post("/api/event", json={"event_type": "unknown_cosmic_event"})
    assert res.status_code == 200
    assert res.json()["accepted"] is False

    # Reset endpoint
    res = client.post("/api/reset")
    assert res.status_code == 200
    assert res.json()["phase"] == 1

def test_mcp_all_haunt_types():
    haunt_types = ["cell_text", "flicker_lamp", "thunder_invert", "ink_spread", "whisper", "screen_tremor"]
    for ht in haunt_types:
        res = call_tool("haunt_spreadsheet", {"haunt_type": ht, "target_cell": "B18", "message": f"Eldritch {ht}"})
        assert "content" in res
        assert ht in res["content"][0]["text"]

def test_vba_bootstrap_ui_stripping_and_restoration():
    vba_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_Bootstrap.bas")
    with open(vba_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # InitializeArchiveUI must hide tabs and scrollbars
    assert "ActiveWindow.DisplayWorkbookTabs = False" in content
    assert "ActiveWindow.DisplayHorizontalScrollBar = False" in content
    assert "ActiveWindow.DisplayVerticalScrollBar = False" in content

    # EmergencyReset must restore tabs and scrollbars
    assert "ActiveWindow.DisplayWorkbookTabs = True" in content
    assert "ActiveWindow.DisplayHorizontalScrollBar = True" in content
    assert "ActiveWindow.DisplayVerticalScrollBar = True" in content

def test_vba_daemon_bridge_haunt_handling():
    vba_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(vba_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Must extract JSON fields, match braces, and handle all 6 haunt types
    assert "ExtractJsonField" in content
    assert "ExecuteHauntAction" in content
    assert "FindMatchingBrace" in content
    assert "TRIGGER_HAUNT" in content

    haunt_types = ["cell_text", "flicker_lamp", "thunder_invert", "ink_spread", "whisper", "screen_tremor"]
    for ht in haunt_types:
        assert f'Case "{ht}"' in content or f'"{ht}"' in content

def test_server_complex_haunt_payloads():
    # Test queueing haunt messages containing braces, colons, quotes and special characters
    complex_haunt = {
        "haunt_type": "cell_text",
        "target_cell": "B18",
        "message": "ANOMALY {LEVEL: 9}: \"SEAL THE DEEP VAULT\" IMMEDIATELY!"
    }
    res = client.post("/api/haunt", json=complex_haunt)
    assert res.status_code == 200

    # Pop via event dispatch
    event_res = client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "1.00"})
    assert event_res.status_code == 200
    data = event_res.json()
    assert data["accepted"] is False
    actions = data.get("actions", [])
    
    # Must contain both standard FX (SPREAD_BLOOD_SCAB) and TRIGGER_HAUNT
    assert any(a.get("effect") == "SPREAD_BLOOD_SCAB" for a in actions)
    haunt_acts = [a for a in actions if a.get("command") == "TRIGGER_HAUNT"]
    assert len(haunt_acts) == 1
    assert haunt_acts[0]["haunt_type"] == "cell_text"
    assert haunt_acts[0]["cell"] == "B18"
    assert "ANOMALY {LEVEL: 9}" in haunt_acts[0]["message"]

def test_spec_consistency():
    spec_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".kiro", "specs", "puzzle_engine_spec.md")
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "LocalPuzzleState.bas" not in content
    assert "HandleOfflineEvent" in content
    assert "M_HorrorFX.bas" in content


