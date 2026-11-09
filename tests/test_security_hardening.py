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
    """Verify cross-origin browser requests with external Origin are rejected with 403."""
    # Untrusted external origin
    resp = client.post(
        "/api/reset",
        headers={"Origin": "https://evil-attacker-site.com"}
    )
    assert resp.status_code == 403
    assert "Cross-origin requests from untrusted origins are forbidden" in resp.json()["detail"]

    # Trusted local origins are accepted
    for allowed_origin in ["http://localhost:3000", "http://127.0.0.1:8000"]:
        resp = client.get(
            "/api/status",
            headers={"Origin": allowed_origin}
        )
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
    """Verify VBA code includes pre-unlinking, cell address validation, and formula escaping."""
    bas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba", "M_DaemonBridge.bas")
    with open(bas_path, "r", encoding="utf-8") as f:
        bas = f.read()

    # Pre-unlink before Open tmpFile on Mac
    assert 'Kill tmpFile\n        On Error GoTo FallbackHandler\n        Dim fNum As Integer' in bas

    # Cell address validation in SET_VALUE and HIJACK_TYPE
    assert "If IsValidCellAddress(svCell) Then" in bas
    assert "If Not IsValidCellAddress(hjCell) Then hjCell = \"B18\"" in bas
    assert "If Not IsValidCellAddress(fxCell) Then" in bas

    # Formula neutralization in SET_VALUE and HIJACK_TYPE
    assert "fCharSv = Left$(Trim$(svVal), 1)" in bas
    assert "fCharHj = Left$(Trim$(hjText), 1)" in bas
