import os
import pytest
from fastapi.testclient import TestClient
from src.backend.puzzle_state import PuzzleEngine, VALID_HAUNT_TYPES, file_lock
from src.backend.server import app

client = TestClient(app)

def test_security_headers_present():
    """Verify standard security headers are added to HTTP responses."""
    resp = client.get("/api/status")
    assert resp.status_code == 200
    assert resp.headers.get("x-content-type-options") == "nosniff"
    assert resp.headers.get("x-frame-options") == "DENY"
    assert resp.headers.get("content-security-policy") == "default-src 'none'"
    assert resp.headers.get("referrer-policy") == "no-referrer"

def test_origin_header_cross_origin_protection():
    """Verify cross-origin browser requests with external Origin (including substring lookalikes) are rejected with 403."""
    # Untrusted external origins, including lookalikes
    untrusted_origins = [
        "https://evil-attacker-site.com",
        "http://localhost.evil.com",
        "http://127.0.0.1.attacker.net",
        "http://evil-localhost.com:8000"
    ]
    for evil in untrusted_origins:
        resp = client.post(
            "/api/reset",
            headers={"Origin": evil}
        )
        assert resp.status_code == 403
        assert "Cross-origin requests from untrusted origins are forbidden" in resp.json()["detail"]

    # Trusted local origins are accepted
    for allowed_origin in ["http://localhost:3000", "http://127.0.0.1:8000", "http://[::1]:8000"]:
        resp = client.get(
            "/api/status",
            headers={"Origin": allowed_origin}
        )
        assert resp.status_code == 200

def test_event_request_value_size_bounding():
    """Verify EventRequest.value rejects oversized strings and payloads."""
    # Oversized string > 2000 chars rejected with 422 Unprocessable Entity
    resp = client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "A" * 2001})
    assert resp.status_code == 422

    # Normal values accepted
    resp = client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "7.00"})
    assert resp.status_code == 200

def test_haunt_type_validation_and_queue_bounding(tmp_path):
    """Verify queue_haunt validates haunt types and caps pending queue size."""
    state_file = str(tmp_path / "security_game_state.json")
    engine = PuzzleEngine()
    engine.save_state(state_file)

    # Valid haunt types
    for ht in VALID_HAUNT_TYPES:
        engine.queue_haunt(ht, "B18", "Valid Haunt")
    assert len(engine.pending_effects) == len(VALID_HAUNT_TYPES)

    # Invalid haunt types must raise ValueError
    with pytest.raises(ValueError, match="Invalid haunt type"):
        engine.queue_haunt("malicious_unrecognized_haunt", "B18", "Bad Haunt")

    # /api/haunt endpoint returns 400 for invalid haunt type
    resp = client.post("/api/haunt", json={"haunt_type": "exploit_rce", "target_cell": "B18"})
    assert resp.status_code == 400

    # Queue bounding: queue 60 effects and verify capped at 50
    for i in range(60):
        engine.queue_haunt("whisper", None, f"Spam {i}")
    assert len(engine.pending_effects) <= 50

def test_lockfile_permissions(tmp_path):
    """Verify lock file is created with restricted owner permissions (0o600)."""
    target = str(tmp_path / "test_state.json")
    with file_lock(target):
        lock_file = target + ".lock"
        assert os.path.exists(lock_file)
        mode = os.stat(lock_file).st_mode & 0o777
        assert mode == 0o600

def test_vba_bridge_security_hardening():
    """Verify VBA code includes pre-unlinking, unique tmpFile, cell address validation, and formula neutralization helper."""
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()

    # Unique random temporary filename on Mac to mitigate sticky /tmp symlink attacks
    assert 'tmpFile = "/tmp/ma_payload_' in bas
    assert 'Kill tmpFile\n        On Error GoTo FallbackHandler\n        Dim fNum As Integer' in bas

    # Cell address validation in SET_VALUE and HIJACK_TYPE
    assert "If IsValidCellAddress(svCell) Then" in bas
    assert "If Not IsValidCellAddress(hjCell) Then hjCell = \"B18\"" in bas
    assert "If Not IsValidCellAddress(fxCell) Then" in bas

    # Centralized formula neutralization helper function used in SET_VALUE, HIJACK_TYPE, ExecuteHauntAction
    assert "Public Function NeutralizeFormulaPrefix(ByVal s As String) As String" in bas
    assert "svVal = NeutralizeFormulaPrefix(svVal)" in bas
    assert "hjText = NeutralizeFormulaPrefix(hjText)" in bas
    assert "msgToWrite = NeutralizeFormulaPrefix(msgToWrite)" in bas
