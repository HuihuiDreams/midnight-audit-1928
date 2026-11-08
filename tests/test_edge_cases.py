import pytest
from src.backend.puzzle_state import PuzzleEngine, PhaseEnum
from src.backend.mcp_server import call_tool, handle_json_rpc
from starlette.testclient import TestClient
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
