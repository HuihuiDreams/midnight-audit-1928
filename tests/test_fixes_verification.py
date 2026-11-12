import os
import sys
import subprocess
import pytest
from fastapi.testclient import TestClient
from src.backend.puzzle_state import PuzzleEngine, PhaseEnum
from src.backend.server import app
from src.backend.mcp_server import call_tool

client = TestClient(app)

def test_issue1_no_early_banishment_across_all_phases():
    """Verify that ritual banishment is strictly rejected in Phases 1, 2, and 3."""
    engine = PuzzleEngine()
    
    # Phase 1: Rejection
    assert engine.current_phase == PhaseEnum.THE_AUDIT_DISCREPANCY
    res1 = engine.judge_ritual("SEAL THE DEEP VAULT")
    assert res1["banished"] is False
    assert engine.archive_sealed is False

    # HTTP /api/banish in Phase 1
    http_res = client.post("/api/banish", json={"phrase": "SEAL THE DEEP VAULT"})
    assert http_res.status_code == 200
    assert http_res.json()["banished"] is False

    # HTTP /api/event banish in Phase 1
    event_res = client.post("/api/event", json={"event_type": "banish"})
    assert event_res.status_code == 200
    assert event_res.json()["banished"] is False

    # Phase 2: Rejection
    engine.handle_cell_change("H7", "7.00")
    assert engine.current_phase == PhaseEnum.THE_UNSEEN_INTRUDER
    res2 = engine.judge_ritual("SEAL THE DEEP VAULT")
    assert res2["banished"] is False

    # Phase 3: Rejection
    engine.handle_reagent_spray()
    assert engine.current_phase == PhaseEnum.HIJACKED_CIPHER
    res3 = engine.judge_ritual("SEAL THE DEEP VAULT")
    assert res3["banished"] is False

    # Phase 4: Acceptance
    engine.handle_cell_change("B18", "first_attempt_triggers_hijack")
    engine.handle_cell_change("B18", "SEAL THE DEEP VAULT")
    assert engine.current_phase == PhaseEnum.MIDNIGHT_SETTLEMENT
    res4 = engine.judge_ritual("SEAL THE DEEP VAULT")
    assert res4["banished"] is True
    assert engine.archive_sealed is True

def test_issue1_vba_banish_gating():
    """Verify that VBA code enforces gLocalPhase >= 4 gating for banishment."""
    cls_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "Sheet1_Archive.cls")
    with open(cls_path, "r", encoding="utf-8") as f:
        cls_content = f.read()
    assert "If gLocalPhase >= 4 Then" in cls_content
    assert "TriggerBanishMacro" in cls_content

    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas_content = f.read()
    assert "If gLocalPhase < 4 Then Exit Sub" in bas_content
    # Ensure Or eventType = "banish" bypass was removed
    assert 'Or eventType = "banish"' not in bas_content

def test_issue2_exact_banish_phrase_matching():
    """Verify that only the exact spec phrase 'SEAL THE DEEP VAULT' is accepted in Phase 4."""
    engine = PuzzleEngine()
    engine.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT

    # Broad substring/improper matches must be rejected
    rejected_phrases = [
        "SEAL",
        "UNSEALED",
        "DON'T SEAL",
        "PLEASE SEAL NOW",
        "BANISH",
        "BANISH WILBUR",
        "MEMENTO MORI",
        "PH'NGLUI MGLW'NAFH",
        "THE DEEP VAULT",
        "SEAL THE VAULT",
        "",
        "   ",
        "123"
    ]
    for p in rejected_phrases:
        res = engine.judge_ritual(p)
        assert res["banished"] is False, f"Phrase '{p}' should have been rejected"

    # Exact match (with case and whitespace normalization) must succeed
    for phrase in ["SEAL THE DEEP VAULT", "seal the deep vault", "   SEAL   THE   DEEP   VAULT   "]:
        engine.archive_sealed = False
        assert engine.judge_ritual(phrase)["banished"] is True

    # Once sealed, subsequent ritual attempts must be rejected
    sealed_res = engine.judge_ritual("SEAL THE DEEP VAULT")
    assert sealed_res["banished"] is False
    assert sealed_res["accepted"] is False
    assert "archive is sealed" in sealed_res["message"].lower()

def test_issue3_direct_script_execution():
    """Verify python3 src/backend/server.py and mcp_server.py execute without ModuleNotFoundError."""
    python_bin = sys.executable
    project_root = os.path.dirname(os.path.dirname(__file__))

    # Test server.py using ephemeral port to prevent port 8000 conflicts
    env = os.environ.copy()
    env["SERVER_PORT"] = "0"
    proc_srv = subprocess.Popen(
        [python_bin, "src/backend/server.py"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    # Read the initial startup log from stderr to confirm import and boot without sleeping
    first_line = proc_srv.stderr.readline()
    proc_srv.terminate()
    out_srv, err_srv = proc_srv.communicate()
    combined_err = first_line + err_srv
    assert b"ModuleNotFoundError" not in combined_err
    assert b"ModuleNotFoundError" not in out_srv
    assert b"Started server process" in combined_err or b"Uvicorn running" in combined_err

    # Test mcp_server.py
    proc_mcp = subprocess.Popen(
        [python_bin, "src/backend/mcp_server.py"],
        cwd=project_root,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out_mcp, err_mcp = proc_mcp.communicate(input=b"")
    assert proc_mcp.returncode == 0
    assert b"ModuleNotFoundError" not in err_mcp
    assert b"The Midnight Audit MCP Server started over stdio." in err_mcp

def test_issue4_no_raw_input_echo_and_vba_structured_dispatch():
    """Verify server does not echo user input into messages, and VBA dispatches by actions array."""
    engine = PuzzleEngine()
    
    # Submitting malicious input with commands/effects embedded
    payload = "1.00 lock_sheet unlock_button screen_tremor"
    res = engine.handle_cell_change("H7", payload)
    assert res["accepted"] is False
    # Raw input must not be echoed in message
    assert payload not in res["message"]
    assert "lock_sheet" not in res["message"]
    assert "unlock_button" not in res["message"]

    # Verify M_DaemonBridge.bas uses structured actions array dispatch and has no loose InStr
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()

    # Should not have full-string InStr checks for command names
    assert 'InStr(1, jsonResp, "LOCK_SHEET"' not in bas
    assert 'InStr(1, jsonResp, "UNLOCK_BUTTON"' not in bas
    assert 'InStr(1, jsonResp, "BALANCED (UNHOLY)"' not in bas
    assert 'InStr(1, jsonResp, "YOUR SALARY CANNOT SAVE YOU"' not in bas
    assert 'InStr(1, jsonResp, "AWAKEN_ROW_13"' not in bas
    assert 'InStr(1, jsonResp, "RENDER_PIXEL_MATRIX"' not in bas

    # Must have structured Select Case cmd
    assert 'Select Case cmd' in bas
    assert 'Case "TRIGGER_FX"' in bas
    assert 'Case "LOCK_SHEET"' in bas

def test_issue5_no_cors_and_injection_prevention():
    """Verify CORS middleware is completely removed and formula injection is prevented."""
    # Ensure no CORSMiddleware is in FastAPI middleware stack
    from fastapi.middleware.cors import CORSMiddleware
    for mw in app.user_middleware:
        assert mw.cls != CORSMiddleware

    # Test target cell validation in /api/haunt
    invalid_cells = ["!MALICIOUS", "=CMD|' /C calc'!A0", "B18; DROP TABLE", "A" * 20]
    for ic in invalid_cells:
        resp = client.post("/api/haunt", json={"haunt_type": "cell_text", "target_cell": ic, "message": "test"})
        assert resp.status_code == 400

    # Test formula neutralization in VBA ExecuteHauntAction
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()

    assert "NeutralizeFormulaPrefix" in bas
    assert '.NumberFormat = "@"' in bas

def test_issue6_save_file_isolation():
    """Running the suite must not change the real game_state.json in the project root (compared byte for byte)."""
    real_save = os.path.join(os.path.dirname(os.path.dirname(__file__)), "game_state.json")

    def snapshot():
        if not os.path.exists(real_save):
            return None
        with open(real_save, "rb") as f:
            return f.read()

    before = snapshot()

    engine = PuzzleEngine()
    engine.handle_cell_change("H7", "7.00")
    engine.save_state()

    assert snapshot() == before

def test_deepened_issue1_phase4_offline_gating_and_sealed_flag():
    """Verify that VBA HandleOfflineEvent strictly requires banish event and Not gArchiveSealed."""
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()

    # Must require banish event/button AND Not gArchiveSealed
    assert "If gLocalPhase = 4 And Not gArchiveSealed And (eventType = \"banish\" Or buttonName = \"SEAL_ARCHIVE\") Then" in bas
    assert "gArchiveSealed = True" in bas
    assert "If gArchiveSealed Then Exit Sub" in bas

    cls_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "Sheet1_Archive.cls")
    with open(cls_path, "r", encoding="utf-8") as f:
        cls = f.read()
    assert "If gLocalPhase >= 4 Then" in cls
    assert "If Not gArchiveSealed Then" in cls

    # judge_ritual must return accepted and current_phase
    engine = PuzzleEngine()
    engine.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT
    success = engine.judge_ritual("SEAL THE DEEP VAULT")
    assert success["accepted"] is True
    assert success["current_phase"] == 4
    assert success["banished"] is True

    fail = engine.judge_ritual("WRONG PHRASE")
    assert fail["accepted"] is False
    assert fail["current_phase"] == 4
    assert fail["banished"] is False

def test_deepened_issue4_vba_actions_boundary_parsing_and_no_var_collision():
    """Verify VBA has FindMatchingBracket and no variable named inStr colliding with VBA keyword."""
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()

    # FindMatchingBracket must exist
    assert "Function FindMatchingBracket" in bas
    assert "arrEnd = FindMatchingBracket(jsonResp, posArrStart)" in bas

    # inStr should not be declared as a variable
    assert "Dim inStr As Boolean" not in bas
    assert "isInsideString" in bas

def test_deepened_issue5_cell_validation_and_mcp():
    """Verify invalid cell coordinates are rejected by engine, server, and MCP."""
    engine = PuzzleEngine()
    with pytest.raises(ValueError, match="Invalid target cell coordinate"):
        engine.queue_haunt("cell_text", target_cell="=CMD|' /C calc'!A0", message="pwn")

    # MCP tool call with invalid cell
    mcp_res = call_tool("haunt_spreadsheet", {"haunt_type": "cell_text", "target_cell": "INVALID!CELL", "message": "test"})
    assert mcp_res.get("isError") is True
    assert "Invalid target cell coordinate" in mcp_res["content"][0]["text"]

    # Server /api/event cell coordinate validation
    res = client.post("/api/event", json={"event_type": "cell_change", "cell": "MALICIOUS;DROP", "value": "123"})
    assert res.status_code == 400
    assert "Invalid cell coordinate" in res.json()["detail"]

    # VBA IsValidCellAddress must be defined and referenced
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()
    assert "Function IsValidCellAddress" in bas
    assert "isTargetValid = IsValidCellAddress(targetAddress)" in bas
    # VBA mirrors the Python bounds: XFD / 1048576 / 900 cells, and cell_text never takes a range
    assert "MAX_SHEET_ROW As Long = 1048576" in bas
    assert "MAX_SHEET_COLUMN As Long = 16384" in bas
    assert "MAX_RANGE_AREA As Long = 900" in bas
    assert "65536" not in bas
    assert 'If InStr(targetAddress, ":") > 0 Then isTargetValid = False' in bas
    assert "isInkTargetValid = IsValidCellAddress(inkTarget)" in bas

def test_i4_sync_state_and_non_200_no_fallthrough():
    """Verify I4: SyncDaemonState queries /api/status, and Windows HTTP non-200 does not fall through to offline mode."""
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()

    # SyncDaemonState must be defined and query /status
    assert "Public Sub SyncDaemonState()" in bas
    assert 'DAEMON_URL & "/status"' in bas
    assert "gLocalPhase = pVal" in bas
    assert "gArchiveSealed = True" in bas

    # Windows non-200 check: http.Status > 0 exits without falling through
    assert "ElseIf http.Status > 0 Then" in bas
    assert "Exit Sub" in bas

    # ThisWorkbook.cls Workbook_Open must call SyncDaemonState
    wb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "ThisWorkbook.cls")
    with open(wb_path, "r", encoding="utf-8") as f:
        wb = f.read()
    assert "SyncDaemonState" in wb

def test_i5_mac_safe_transport():
    """Verify I5: Mac curl transport writes JSON to temp file and uses --data-binary @ to prevent shell injection."""
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()

    assert 'tmpFile = "/tmp/ma_payload_' in bas
    assert "Print #fNum, jsonPayload;" in bas
    assert "--data-binary @" in bas
    assert "Kill tmpFile" in bas

def test_i7_concurrency_file_locking_and_reentrancy(tmp_path):
    """Verify I7: file_lock handles re-entrancy and concurrent multi-threaded state access safely."""
    from src.backend.puzzle_state import file_lock, PuzzleEngine
    import threading

    state_file = str(tmp_path / "concurrent_game_state.json")
    engine = PuzzleEngine()
    engine.save_state(state_file)

    # 1. Test re-entrancy within the same thread
    with file_lock(state_file):
        with file_lock(state_file):
            engine.load_state(state_file)
            engine.save_state(state_file)

    # 2. Test multi-threaded concurrent access
    errors = []
    def worker(worker_id):
        try:
            for i in range(10):
                with file_lock(state_file):
                    local_engine = PuzzleEngine()
                    local_engine.load_state(state_file)
                    local_engine.pending_effects.append({
                        "type": "cell_text",
                        "target_cell": "B18",
                        "message": f"worker_{worker_id}_{i}"
                    })
                    local_engine.save_state(state_file)
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Concurrent workers encountered errors: {errors}"
    final_engine = PuzzleEngine()
    final_engine.load_state(state_file)
    assert len(final_engine.pending_effects) == 50

def test_i8_mcp_json_rpc_compliance():
    """Verify I8: notifications return None, ping is supported, -32700 for decode error, params=None is handled."""
    from src.backend.mcp_server import handle_json_rpc

    # 1. Notifications without 'id' return None
    notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    assert handle_json_rpc(notification) is None

    # 2. Ping method
    ping_req = {
        "jsonrpc": "2.0",
        "id": 42,
        "method": "ping"
    }
    ping_resp = handle_json_rpc(ping_req)
    assert ping_resp == {"jsonrpc": "2.0", "id": 42, "result": {}}

    # 3. params = None safe handling
    req_null_params = {
        "jsonrpc": "2.0",
        "id": 99,
        "method": "tools/list",
        "params": None
    }
    resp = handle_json_rpc(req_null_params)
    assert resp["id"] == 99
    assert "tools" in resp["result"]

    # 4. Unknown method with id returns -32601
    bad_method = {
        "jsonrpc": "2.0",
        "id": 100,
        "method": "non_existent_method"
    }
    bad_resp = handle_json_rpc(bad_method)
    assert bad_resp["error"]["code"] == -32601

def test_s1_save_state_error_logging_and_cleanup(tmp_path, monkeypatch, capsys):
    """Verify S1: save_state logs errors to sys.stderr and raises StateSaveError instead of reporting success."""
    from src.backend.puzzle_state import StateSaveError

    engine = PuzzleEngine()
    # Direct save to an uncreatable path (e.g. file used as directory)
    fake_dir_file = tmp_path / "not_a_dir"
    fake_dir_file.write_text("blocked")
    target_path = str(fake_dir_file / "invalid_sub" / "game_state.json")

    with pytest.raises(StateSaveError):
        engine.save_state(target_path)
    captured = capsys.readouterr()
    assert "Error saving game state" in captured.err

def test_s2_inspect_ledger_range_matching():
    """Verify S2: inspect_ledger accurately parses cell/range coordinates and does not confuse A17/H70 with row 7."""
    # A17 must NOT match row 7
    res_a17 = call_tool("inspect_ledger", {"target_range": "A17"})
    text_a17 = res_a17["content"][0]["text"]
    assert "Row 7:" not in text_a17
    assert "Target range A17 appears standard" in text_a17

    # H70 must NOT match row 7
    res_h70 = call_tool("inspect_ledger", {"target_range": "H70"})
    text_h70 = res_h70["content"][0]["text"]
    assert "Row 7:" not in text_h70
    assert "Target range H70 appears standard" in text_h70

    # A13:I17 covers 13 through 17 -> matches row 13, does NOT match row 7
    res_range = call_tool("inspect_ledger", {"target_range": "A13:I17"})
    text_range = res_range["content"][0]["text"]
    assert "Row 13:" in text_range
    assert "Row 7:" not in text_range

    # H7 matches row 7
    res_h7 = call_tool("inspect_ledger", {"target_range": "H7"})
    assert "Row 7:" in res_h7["content"][0]["text"]

    # B18 matches row 18
    res_b18 = call_tool("inspect_ledger", {"target_range": "B18"})
    assert "Row 18:" in res_b18["content"][0]["text"]
    assert "B18 Override Code Cell" in res_b18["content"][0]["text"]

def test_s3_vba_blood_scab_color_restoration():
    """Verify S3: SpreadBloodScab saves original colors in array and restores each cell's exact color."""
    fx_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_HorrorFX.bas")
    with open(fx_path, "r", encoding="utf-8") as f:
        fx = f.read()

    assert "ReDim origColors(1 To numR, 1 To numC)" in fx
    assert "origColors(i, j) = fullRange.Cells(i, j).Interior.Color" in fx
    assert "fullRange.Cells(i, j).Interior.Color = origColors(i, j)" in fx
    # Old hardcoded COLOR_BONE_PAPER wipeout must be gone
    assert "fullRange).Interior.Color = COLOR_BONE_PAPER" not in fx
    assert "Resize(maxSpread * 2 + 1, maxSpread * 2 + 1).Interior.Color = COLOR_BONE_PAPER" not in fx

def test_s4_pixel_radar_and_blinking_eye_alignment():
    """Verify S4: get_pixel_radar pupil center (r=14..15, c=12..13) exactly aligns with W34:X35."""
    engine = PuzzleEngine()
    radar = engine.get_pixel_radar()
    grid = radar["grid"]

    # Pupil at W34:X35 corresponds to r=14,15 and c=12,13 in 0-based grid
    from src.backend.puzzle_state import PALETTE
    assert grid[14][12] == PALETTE["DRIED_BLOOD"]
    assert grid[14][13] == PALETTE["DRIED_BLOOD"]
    assert grid[15][12] == PALETTE["DRIED_BLOOD"]
    assert grid[15][13] == PALETTE["DRIED_BLOOD"]
    assert radar["blinking_cells"] == ["W34", "X34", "W35", "X35"]

    # The VBA renders the same matrix (see test_vba_face_pixels_equal_python_radar_cell_for_cell)
    from src.backend.puzzle_state import ENTITY_FACE_MATRIX, ENTITY_FACE_LEGEND
    for r in (14, 15):
        for c in (12, 13):
            assert ENTITY_FACE_LEGEND[ENTITY_FACE_MATRIX[r][c]] == "DRIED_BLOOD"

def test_s5_platform_sleep_midnight_wrap_around():
    """Verify S5: PlatformSleep handles midnight wrap-around when Timer resets to 0."""
    boot_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_Bootstrap.bas")
    with open(boot_path, "r", encoding="utf-8") as f:
        boot = f.read()

    assert "86400# - startT" in boot
    assert "elapsed >= durationSec" in boot

def test_s6_silent_emergency_reset_on_close():
    """Verify S6: EmergencyReset accepts optional silent parameter, and Workbook_BeforeClose passes True."""
    boot_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_Bootstrap.bas")
    with open(boot_path, "r", encoding="utf-8") as f:
        boot = f.read()
    assert "Public Sub EmergencyReset(Optional ByVal silent As Boolean = False)" in boot
    assert "If Not silent Then" in boot

    wb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "ThisWorkbook.cls")
    with open(wb_path, "r", encoding="utf-8") as f:
        wb = f.read()
    assert "EmergencyReset True" in wb

def test_s7_toggle_eye_blink_gating():
    """Verify S7: ToggleEyeBlink checks phase 2/3 and archive_sealed, and reschedules with 2s interval."""
    fx_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_HorrorFX.bas")
    with open(fx_path, "r", encoding="utf-8") as f:
        fx = f.read()
    assert "If gArchiveSealed Or (gLocalPhase <> 2 And gLocalPhase <> 3) Then" in fx
    assert 'TimeValue("00:00:02")' in fx

def test_s8_archive_sealed_prevents_retrigger():
    """Verify S8: once sealed, handle_cell_change rejects inputs and VBA exits early."""
    engine = PuzzleEngine()
    engine.archive_sealed = True

    # Cell change in B18 or H7 must be rejected when archive is sealed
    res = engine.handle_cell_change("B18", "SEAL THE DEEP VAULT")
    assert res["accepted"] is False
    assert "The archive is sealed" in res["message"]

    res_h7 = engine.handle_cell_change("H7", "7.00")
    assert res_h7["accepted"] is False
    assert "The archive is sealed" in res_h7["message"]

    # VBA checks
    cls_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "Sheet1_Archive.cls")
    with open(cls_path, "r", encoding="utf-8") as f:
        cls = f.read()
    assert "If gArchiveSealed Then Exit Sub" in cls

    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()
    assert "If gArchiveSealed Then Exit Sub" in bas

def test_s9_python_port_of_the_extract_json_field_algorithm():
    """
    S9: exercises a Python PORT of the ExtractJsonField algorithm against real daemon JSON.
    It does not run the VBA code, so it cannot catch a divergence between the port and M_DaemonBridge.bas.
    Tests that read .bas files are source checks (lint), not behavior tests; VBA behavior needs Excel.
    """
    import json

    sample_response = json.dumps({
        "current_phase": 3,
        "phase": 3,
        "archive_sealed": False,
        "message": "Escape test: \"quotes\" and newline \n inside value",
        "actions": [
            {
                "command": "TRIGGER_FX",
                "effect": "THUD_BEEP"
            }
        ]
    })

    # Python simulation of VBA ExtractJsonField algorithm
    def py_extract_json_field(json_str: str, target_key: str) -> str:
        target_key = target_key.lower().strip()
        i = 0
        while i < len(json_str):
            c = json_str[i]
            if c == '"':
                str_start = i + 1
                str_end = -1
                j = str_start
                esc = False
                while j < len(json_str):
                    sc = json_str[j]
                    if esc:
                        esc = False
                    elif sc == '\\':
                        esc = True
                    elif sc == '"':
                        str_end = j
                        break
                    j += 1
                if str_end > str_start:
                    cand_key = json_str[str_start:str_end]
                    # Find colon
                    colon_pos = -1
                    for k in range(str_end + 1, len(json_str)):
                        chk = json_str[k]
                        if chk == ':':
                            colon_pos = k
                            break
                        elif chk not in (' ', '\t', '\r', '\n'):
                            break
                    if colon_pos > 0 and cand_key.lower() == target_key:
                        val_start = -1
                        for k in range(colon_pos + 1, len(json_str)):
                            vc = json_str[k]
                            if vc not in (' ', '\t', '\r', '\n'):
                                val_start = k
                                break
                        if val_start < 0:
                            return ""
                        first_vc = json_str[val_start]
                        if first_vc == '"':
                            val_chars = []
                            esc_val = False
                            for k in range(val_start + 1, len(json_str)):
                                ch = json_str[k]
                                if esc_val:
                                    if ch == 'n': val_chars.append('\n')
                                    elif ch == 'r': val_chars.append('\r')
                                    elif ch == 't': val_chars.append('\t')
                                    else: val_chars.append(ch)
                                    esc_val = False
                                elif ch == '\\':
                                    esc_val = True
                                elif ch == '"':
                                    break
                                else:
                                    val_chars.append(ch)
                            return "".join(val_chars)
                        else:
                            val_chars = []
                            for k in range(val_start, len(json_str)):
                                ch = json_str[k]
                                if ch in (',', '}', ']', '\r', '\n', ' '):
                                    break
                                val_chars.append(ch)
                            return "".join(val_chars).strip()
                    i = str_end + 1
                    continue
            i += 1
        return ""

    assert py_extract_json_field(sample_response, "current_phase") == "3"
    assert py_extract_json_field(sample_response, "phase") == "3"
    assert py_extract_json_field(sample_response, "archive_sealed") == "false"
    assert "Escape test: \"quotes\" and newline \n inside value" == py_extract_json_field(sample_response, "message")

def test_spread_blood_scab_boundary_clamping():
    """Verify SpreadBloodScab clamps maxSpread to 0 at sheet boundaries without throwing error 1004."""
    fx_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_HorrorFX.bas")
    with open(fx_path, "r", encoding="utf-8") as f:
        fx = f.read()

    # Must clamp to 0, not 1
    assert "If maxSpread < 0 Then maxSpread = 0" in fx
    assert "If maxSpread < 1 Then maxSpread = 1" not in fx
    assert "If maxSpread >= 1 Then" in fx

    # Algorithmic simulation of VBA cell boundary clamping
    def calc_spread_bounds(base_row: int, base_col: int):
        max_spread = 2
        if base_row - max_spread < 1:
            max_spread = base_row - 1
        if base_col - max_spread < 1:
            max_spread = base_col - 1
        if max_spread < 0:
            max_spread = 0
        min_r = base_row - max_spread
        min_c = base_col - max_spread
        max_r = base_row + max_spread
        max_c = base_col + max_spread
        return max_spread, min_r, min_c, max_r, max_c

    # Row 1, Col 1 (A1)
    sp, r1, c1, r2, c2 = calc_spread_bounds(1, 1)
    assert sp == 0 and r1 == 1 and c1 == 1 and r2 == 1 and c2 == 1

    # Col 1 (A5)
    sp, r1, c1, r2, c2 = calc_spread_bounds(5, 1)
    assert sp == 0 and r1 == 5 and c1 == 1 and r2 == 5 and c2 == 1

    # B18 (row 18, col 2)
    sp, r1, c1, r2, c2 = calc_spread_bounds(18, 2)
    assert sp == 1 and r1 == 17 and c1 == 1 and r2 == 19 and c2 == 3

    # H7 (row 7, col 8)
    sp, r1, c1, r2, c2 = calc_spread_bounds(7, 8)
    assert sp == 2 and r1 == 5 and c1 == 6 and r2 == 9 and c2 == 10

def test_i5_mac_transport_hardening_and_tab_escaping():
    """Verify Mac transport cleans up tmpFile on error, escapes vbTab, and never falls back on non-empty response."""
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()

    # vbTab escaped
    assert 'Replace(safeVal, vbTab, "\\t")' in bas

    # Kill tmpFile in FallbackHandler
    assert "FallbackHandler:" in bas
    assert "Kill tmpFile" in bas

    # Non-empty response never falls through
    assert "ElseIf Len(respText) > 0 Then" in bas

def test_i4_sync_state_sealed_false_reset():
    """Verify SyncDaemonState resets gArchiveSealed to False when server returns archive_sealed: false."""
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()

    assert 'ElseIf sealedStr = "false" Then' in bas
    assert "gArchiveSealed = False" in bas

def test_macro_phase_gating_and_sealed_guards():
    """Verify TriggerReagentMacro checks phase 2 and sealed state, and Worksheet events check sealed state early."""
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()

    assert "If gLocalPhase <> 2 Or gArchiveSealed Then Exit Sub" in bas

    cls_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "Sheet1_Archive.cls")
    with open(cls_path, "r", encoding="utf-8") as f:
        cls = f.read()

    # Both Change and SelectionChange should have early Exit Sub when gArchiveSealed
    assert cls.count("If gArchiveSealed Then Exit Sub") >= 2

def test_i8_mcp_non_dict_and_error_id_preservation():
    """Verify handle_json_rpc returns -32600 for non-dict requests, and preserves id on errors."""
    from src.backend.mcp_server import handle_json_rpc

    # Non-dict requests return -32600 Invalid Request
    for non_dict in [123, "not_a_json_rpc", [1, 2, 3], True]:
        resp = handle_json_rpc(non_dict)
        assert resp is not None
        assert resp["error"]["code"] == -32600
        assert "Invalid Request" in resp["error"]["message"]

    # Tool call failure preserves request id
    tool_err_req = {
        "jsonrpc": "2.0",
        "id": "req-xyz-999",
        "method": "tools/call",
        "params": {
            "name": "haunt_spreadsheet",
            "arguments": {"haunt_type": "cell_text", "target_cell": "INVALID"}
        }
    }
    tool_resp = handle_json_rpc(tool_err_req)
    assert tool_resp["id"] == "req-xyz-999"
    assert tool_resp["result"]["isError"] is True

def test_s2_inspect_ledger_row_references():
    """Verify parse_range_rows extracts row numbers from '7', 'ROW 7', 'Row 13', and ranges."""
    from src.backend.mcp_server import parse_range_rows, call_tool

    assert parse_range_rows("7") == {7}
    assert parse_range_rows("ROW 7") == {7}
    assert parse_range_rows("row 13") == {13}
    assert parse_range_rows("B18") == {18}
    assert parse_range_rows("A13:I17") == {13, 14, 15, 16, 17}

    # inspect_ledger with 'ROW 7'
    res_r7 = call_tool("inspect_ledger", {"target_range": "ROW 7"})
    assert "Row 7:" in res_r7["content"][0]["text"]

def test_issue1_no_repeated_victory_after_archive_sealed():
    """Verify that once archive is sealed, judge_ritual cannot be replayed to trigger victory."""
    engine = PuzzleEngine()
    engine.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT
    
    # First ritual seals archive
    res1 = engine.judge_ritual("SEAL THE DEEP VAULT")
    assert res1["banished"] is True
    assert res1["accepted"] is True
    assert engine.archive_sealed is True
    assert any(a["effect"] == "THUNDER_STROBE" for a in res1.get("actions", []))

    # Second ritual must be blocked and not re-trigger victory
    res2 = engine.judge_ritual("SEAL THE DEEP VAULT")
    assert res2["banished"] is False
    assert res2["accepted"] is False
    assert "sealed" in res2["message"].lower()
    assert len(res2.get("actions", [])) == 0

    # Also cell changes must be blocked
    res_cell = engine.handle_cell_change("B18", "SEAL THE DEEP VAULT")
    assert res_cell["accepted"] is False
    assert "sealed" in res_cell["message"].lower()

def test_issue2_empty_banish_event_rejected():
    """Verify that empty / omitted phrase in /api/event banish is strictly rejected in Phase 4."""
    # Reset engine to phase 4
    engine = PuzzleEngine()
    engine.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT
    engine.save_state()

    # Empty phrase via /api/event
    res_empty = client.post("/api/event", json={"event_type": "banish", "value": ""})
    assert res_empty.status_code == 200
    assert res_empty.json()["banished"] is False

    # Missing value field
    res_none = client.post("/api/event", json={"event_type": "banish"})
    assert res_none.status_code == 200
    assert res_none.json()["banished"] is False

    # Exact phrase works
    res_exact = client.post("/api/event", json={"event_type": "banish", "value": "SEAL THE DEEP VAULT"})
    assert res_exact.status_code == 200
    assert res_exact.json()["banished"] is True

def test_issue4_offline_vba_whitespace_normalization():
    """Verify VBA offline engine normalizes multiple spaces, tabs, and newlines in override code."""
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()

    assert 'cleanCode = Replace(Replace(Replace(cellVal, vbTab, " "), vbCr, " "), vbLf, " ")' in bas
    assert 'cleanCode = Trim(UCase(cleanCode))' in bas
    assert 'Do While InStr(cleanCode, "  ") > 0' in bas
    assert 'cleanCode = Replace(cleanCode, "  ", " ")' in bas

    # Algorithmic simulation verifying behavioral parity between VBA string loop and Python regex
    def vba_clean_code(cell_val: str) -> str:
        s = cell_val.replace("\t", " ").replace("\r", " ").replace("\n", " ")
        s = s.strip().upper()
        while "  " in s:
            s = s.replace("  ", " ")
        return s

    test_inputs = [
        "SEAL THE DEEP VAULT",
        "  SEAL   THE   DEEP   VAULT  ",
        "SEAL\tTHE\r\nDEEP  VAULT",
        "seal   the\t\tdeep\n\nvault",
        "   ",
        "",
        "SEAL  THE DEEP",
    ]
    for inp in test_inputs:
        import re
        py_norm = re.sub(r"\s+", " ", str(inp).strip().upper())
        vba_norm = vba_clean_code(inp)
        assert py_norm == vba_norm, f"Mismatch for input {inp!r}: py='{py_norm}', vba='{vba_norm}'"
        assert (py_norm == "SEAL THE DEEP VAULT") == (vba_norm == "SEAL THE DEEP VAULT")

def test_issue5_build_ledger_single_palette_source():
    """Verify build_ledger imports PALETTE directly from puzzle_state and uses COLOR_PHOSPHOR_GREEN."""
    from scripts.build_ledger import build_ledger_workbook, COLOR_PHOSPHOR_GREEN, COLOR_COLD_ASH
    from src.backend.puzzle_state import PALETTE

    assert COLOR_PHOSPHOR_GREEN == PALETTE["PHOSPHOR_GREEN"].lstrip("#")
    assert COLOR_COLD_ASH == PALETTE["COLD_ASH"].lstrip("#")

    ledger_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "build_ledger.py")
    with open(ledger_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "from src.backend.puzzle_state import PALETTE" in content
    assert '"3B533E"' not in content

def test_issue6_no_dead_configs():
    """Verify PALETTE has no unused ABYSS_BLACK and conftest has no dead GAME_STATE_FILE patch for server."""
    from src.backend.puzzle_state import PALETTE
    import src.backend.server as server_mod

    assert "ABYSS_BLACK" not in PALETTE
    assert not hasattr(server_mod, "GAME_STATE_FILE")

    conftest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "conftest.py")
    with open(conftest_path, "r", encoding="utf-8") as f:
        conftest = f.read()
    assert "src.backend.server.GAME_STATE_FILE" not in conftest
    assert "src.backend.mcp_server.GAME_STATE_FILE" not in conftest

def test_issue7_mouth_rendering_and_spec_drift():
    """Verify the shared face matrix renders the mouth, and the spec documents the 2s blink interval."""
    from src.backend.puzzle_state import ENTITY_FACE_MATRIX, ENTITY_FACE_LEGEND

    # 0-based mouth range (r=20..22, c=10..19)
    for r in range(20, 23):
        for c in range(10, 20):
            assert ENTITY_FACE_LEGEND[ENTITY_FACE_MATRIX[r][c]] == "DRIED_BLOOD"

    spec_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".kiro", "specs", "puzzle_engine_spec.md")
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = f.read()

    assert "every 2 seconds" in spec
    assert "every 1.5 seconds" not in spec

def test_halloween_horror_enhancements():
    """Verify Halloween horror enhancements: timeline, statusbar whispers, and abyss absorption."""
    # 1. Backend stamp
    engine = PuzzleEngine()
    engine.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT
    res = engine.judge_ritual("SEAL THE DEEP VAULT")
    assert res["stamp"] == "[ ARCHIVE SEALED - OCTOBER 31, 1928 - 00:01 AM ]"

    # 2. VBA Bootstrap
    vba_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba")
    with open(os.path.join(vba_dir, "M_Bootstrap.bas"), "r", encoding="utf-8") as f:
        bootstrap = f.read()
    assert "OCTOBER 31, 1928 - 11:47 PM | ALL HALLOWS' EVE" in bootstrap

    # 3. VBA Horror FX
    with open(os.path.join(vba_dir, "M_HorrorFX.bas"), "r", encoding="utf-8") as f:
        horror_fx = f.read()
    assert "Public Sub FlashAbyssAbsorption(ByVal ws As Worksheet)" in horror_fx
    assert "Public Sub TriggerAmbientWhisper()" in horror_fx
    assert "Public Sub ResetStatusBar()" in horror_fx
    assert "Public Sub CancelAmbientWhisper()" in horror_fx
    assert "OCTOBER 31, 1928 - 00:01 AM | ARCHIVE SEALED" in horror_fx

    # 4. VBA Sheet1 Hooks
    with open(os.path.join(vba_dir, "Sheet1_Archive.cls"), "r", encoding="utf-8") as f:
        sheet = f.read()
    assert "FlashAbyssAbsorption Me" in sheet
    assert "TriggerAmbientWhisper" in sheet

    # 5. Workbook BeforeClose cancellation
    wb_path = os.path.join(vba_dir, "ThisWorkbook.cls")
    with open(wb_path, "r", encoding="utf-8") as f:
        wb = f.read()
    assert "CancelAmbientWhisper" in wb


def test_agent_guidelines_and_changelog_integrity():
    """Verify the Kiro steering agent guidelines exist with required rules, no conversation IDs, and are tracked in CHANGELOG.md."""
    repo_root = os.path.dirname(os.path.dirname(__file__))
    agents_path = os.path.join(repo_root, ".kiro", "steering", "agent_guidelines.md")
    assert os.path.isfile(agents_path), "agent_guidelines.md must exist in .kiro/steering"
    # The root AGENTS.md was migrated into steering; keeping both would load the rules twice.
    assert not os.path.exists(os.path.join(repo_root, "AGENTS.md"))

    with open(agents_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Must be platform-agnostic: no ephemeral conversation IDs or Antigravity URL schemes
    assert "conversation://" not in content
    assert "a146e671" not in content

    # Must contain holistic UI design and boundary constraints
    assert "UI 整体设计" in content or "Holistic UI Design" in content
    assert "A1:AN50" in content

    # Must contain lore adherence and ban narrative drift
    assert "不能偏离最初的故事设定" in content or "Strict Grounding in the Original Lore" in content

    # Must contain Karpathy Guidelines
    assert "Karpathy" in content
    assert "Think Before Coding" in content
    assert "Simplicity First" in content
    assert "Surgical Changes" in content
    assert "Goal-Driven Execution" in content

    # Must contain TDD and CHANGELOG protocols
    assert "Test-Driven Development" in content or "测试驱动开发" in content
    assert "CHANGELOG" in content

    # Layout ranges must match the build script and aesthetic_autopsy.md
    for stale in ("K4:U16", "W4:AN16", "B20:H26", "B28:H49"):
        assert stale not in content
    for current in ("K4:AN12", "K13:AN16", "B21:H28", "B30:H48"):
        assert current in content

    # Verify CHANGELOG.md tracks the steering file
    changelog_path = os.path.join(repo_root, "CHANGELOG.md")
    with open(changelog_path, "r", encoding="utf-8") as f:
        changelog = f.read()
    assert "agent_guidelines.md" in changelog



# ---------------------------------------------------------------------------
# VBA source-level checks. VBA cannot run under pytest, so these only pin the
# source text; the behavior still has to be confirmed in Excel (tasks.md #16).
# ---------------------------------------------------------------------------

def _vba_source(name):
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _vba_proc(source, header):
    start = source.index(header)
    return source[start:source.index("End Sub", start)]

def test_vba_lamp_flicker_restores_original_header_colors():
    fx = _vba_source("M_HorrorFX.bas")
    lamp = _vba_proc(fx, "Public Sub FlashKeroseneLamp()")

    assert "origColors(i, j) = c.Cells(i, j).Interior.Color" in lamp
    assert "c.Cells(i, j).Interior.Color = origColors(i, j)" in lamp
    assert "COLOR_BONE_PAPER" not in lamp
    assert 'Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")' in lamp

def test_vba_thunder_invert_targets_the_game_sheet():
    thunder = _vba_proc(_vba_source("M_HorrorFX.bas"), "Public Sub ThunderInvert()")

    assert 'Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")' in thunder

def test_vba_start_eye_blink_cancels_pending_timer_first():
    start = _vba_proc(_vba_source("M_HorrorFX.bas"), "Public Sub StartEyeBlink(ByVal ws As Worksheet)")

    assert start.index("StopEyeBlink") < start.index("ToggleEyeBlink")

def test_vba_does_not_use_reserved_word_step_as_variable():
    import re
    fx = _vba_source("M_HorrorFX.bas")

    assert not re.search(r"\bDim\s+step\b", fx, re.IGNORECASE)
    assert not re.search(r"\bNext\s+step\b", fx, re.IGNORECASE)

def test_vba_cleared_input_cells_are_not_sent_as_attempts():
    cls = _vba_source("Sheet1_Archive.cls")

    for cell in ("H7", "B18"):
        start = cls.index(f'Intersect(Target, Me.Range("{cell}"))')
        block = cls[start:cls.index(f'PostEvent "cell_change", "{cell}"')]
        guard = f'If Len(Trim$(CStr(Me.Range("{cell}").Value))) = 0 Then Exit Sub'
        assert block.index(guard) < block.index("Application.EnableEvents = False")

def test_vba_tells_player_when_daemon_refuses_an_entry():
    bas = _vba_source("M_DaemonBridge.bas")

    assert "Private Sub ReportDaemonRefusal()" in bas
    assert bas.count("ReportDaemonRefusal\n") == 2   # Windows and macOS non-200 branches
    assert "Application.StatusBar = " in _vba_proc(bas, "Private Sub ReportDaemonRefusal()")

def test_offline_mode_reveals_censored_rows_by_color_only_like_online_mode():
    bas = _vba_source("M_DaemonBridge.bas")
    offline_phase_1 = _vba_proc(bas, "Public Sub HandleOfflineEvent(")

    # Online AWAKEN_ROW_13 / UNLOCK_CENSORED_ROWS only recolor A14:I16; I14 already carries the coordinate.
    assert 'ws.Range("B14")' not in offline_phase_1
    assert "COORDINATE DISCLOSED" not in bas

def test_mac_temp_file_name_is_seeded_randomly():
    bas = _vba_source("M_DaemonBridge.bas")

    assert bas.index("Randomize") < bas.index('tmpFile = "/tmp/ma_payload_')

def test_vba_haunt_polling_lifecycle():
    bas = _vba_source("M_DaemonBridge.bas")

    start = _vba_proc(bas, "Public Sub StartHauntPolling()")
    assert start.index("StopHauntPolling") < start.index("Application.OnTime")   # never two chains
    assert "If gArchiveSealed Then Exit Sub" in start
    assert '"PollPendingHaunts"' in start

    stop = _vba_proc(bas, "Public Sub StopHauntPolling()")
    assert 'Application.OnTime mNextPollTime, "PollPendingHaunts", , False' in stop

def test_vba_poll_fetches_pending_haunts_with_events_disabled_and_reschedules():
    bas = _vba_source("M_DaemonBridge.bas")
    poll = _vba_proc(bas, "Public Sub PollPendingHaunts()")

    assert "If gArchiveSealed Then Exit Sub" in poll
    assert '"/pending"' in _vba_proc(bas, "Private Function FetchPendingHaunts() As String")
    # A haunt that writes into H7/B18 must not be mistaken for a player attempt
    assert poll.index("Application.EnableEvents = False") < poll.index("ProcessDaemonResponse")
    assert poll.index("ProcessDaemonResponse") < poll.index("Application.EnableEvents = eventsWereOn")
    assert poll.rindex("StartHauntPolling") > poll.index("ProcessDaemonResponse")
    assert "HandleOfflineEvent" not in poll   # a silent daemon must never fall back to the offline engine

def test_vba_polling_starts_on_open_and_is_cleaned_up_everywhere():
    opened = _vba_proc(_vba_source("ThisWorkbook.cls"), "Private Sub Workbook_Open")
    # A seal queued while the workbook was closed must be drained before SyncDaemonState marks the archive sealed
    assert opened.index("PollPendingHaunts") < opened.index("SyncDaemonState") < opened.index("StartHauntPolling")
    assert "StopHauntPolling" in _vba_proc(_vba_source("ThisWorkbook.cls"), "Private Sub Workbook_BeforeClose")
    assert "StopHauntPolling" in _vba_proc(_vba_source("M_Bootstrap.bas"), "Public Sub EmergencyReset(")

    bas = _vba_source("M_DaemonBridge.bas")
    lock_sheet = bas[bas.index('Case "LOCK_SHEET"'):bas.index('Case "TRIGGER_HAUNT"')]
    assert "StopHauntPolling" in lock_sheet
    offline_seal = bas[bas.index("' Phase 4: Banishment Execution"):]
    assert "StopHauntPolling" in offline_seal

def test_vba_entity_face_is_generated_from_the_python_matrix():
    from scripts.sync_vba_radar import render_block, BEGIN_MARKER, END_MARKER
    fx = _vba_source("M_HorrorFX.bas")

    block = fx[fx.index(BEGIN_MARKER):fx.index(END_MARKER) + len(END_MARKER)]

    assert block == render_block(), "M_HorrorFX.bas is out of date: run `python scripts/sync_vba_radar.py`"

def test_vba_render_pixel_face_has_no_hand_written_geometry():
    render = _vba_proc(_vba_source("M_HorrorFX.bas"), "Public Sub RenderPixelFace(ByVal ws As Worksheet)")

    assert "EntityFaceRow(r)" in render
    assert "EntityFaceColor(" in render
    assert "distSq" not in render

def test_vba_face_pixels_equal_python_radar_cell_for_cell():
    import re
    from src.backend.puzzle_state import PALETTE
    fx = _vba_source("M_HorrorFX.bas")

    rows = {int(n): text for n, text in re.findall(r'Case (\d+): EntityFaceRow = "([^"]*)"', fx)}
    colors = dict(re.findall(r'Case "(.)": EntityFaceColor = COLOR_(\w+)', fx))
    py_grid = PuzzleEngine().get_pixel_radar()["grid"]

    assert sorted(rows) == list(range(1, 31))
    for r in range(30):
        assert len(rows[r + 1]) == 30
        for c in range(30):
            assert PALETTE[colors[rows[r + 1][c]]] == py_grid[r][c], f"pixel mismatch at r={r}, c={c}"

def test_vba_sealing_protects_the_sheet_after_stamping_in_both_modes():
    bas = _vba_source("M_DaemonBridge.bas")
    online = bas[bas.index('Case "LOCK_SHEET"'):bas.index('Case "TRIGGER_HAUNT"')]
    offline = bas[bas.index("' Phase 4: Banishment Execution"):]

    for seal_path in (online, offline):
        assert seal_path.index('ws.Range("B12").Value') < seal_path.index("ws.Protect") < seal_path.index("MsgBox")

def test_vba_emergency_reset_lifts_sheet_protection():
    reset = _vba_proc(_vba_source("M_Bootstrap.bas"), "Public Sub EmergencyReset(")

    assert 'ThisWorkbook.Sheets("Audit_Ledger_1928").Unprotect' in reset

def test_test_isolation_has_a_single_entry_point():
    """No test module may bind the real save path at import time; conftest is the only isolation point."""
    import re
    tests_dir = os.path.dirname(__file__)
    for name in sorted(os.listdir(tests_dir)):
        if not name.startswith("test_") or not name.endswith(".py"):
            continue
        with open(os.path.join(tests_dir, name), "r", encoding="utf-8") as f:
            source = f.read()
        assert not re.search(r"^from src\.backend\.puzzle_state import .*GAME_STATE_FILE", source, re.M), name

    with open(os.path.join(tests_dir, "conftest.py"), "r", encoding="utf-8") as f:
        conftest = f.read()
    assert conftest.index('os.environ["GAME_STATE_FILE"]') < conftest.index("import src.backend.puzzle_state")
    assert "tests.test_" not in conftest

def test_vba_pending_poll_sends_the_client_header_on_both_transports():
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas"), "r", encoding="utf-8") as f:
        bas = f.read()
    fetch = bas[bas.index("Private Function FetchPendingHaunts()"):bas.index("End Function", bas.index("Private Function FetchPendingHaunts()"))]

    assert 'http.setRequestHeader "X-Audit-Client", "1"' in fetch
    assert '-H ""X-Audit-Client: 1""' in fetch

def test_vba_screen_tremor_never_moves_a_foreign_window():
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_HorrorFX.bas"), "r", encoding="utf-8") as f:
        fx = f.read()
    tremor = fx[fx.index("Public Sub ScreenTremor()"):fx.index("End Sub", fx.index("Public Sub ScreenTremor()"))]

    assert "hWnd = Application.Hwnd" in tremor
    assert "hWnd = GetForegroundWindow()\n" not in tremor  # the foreground window is only compared, never shaken
    assert "And hWnd = GetForegroundWindow() Then" in tremor
    code = "\n".join(line for line in tremor.splitlines() if not line.strip().startswith("'"))
    assert "SmallScroll" not in code
    assert "ActiveWindow" not in code
