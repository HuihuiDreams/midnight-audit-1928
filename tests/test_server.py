import os
import pytest
from fastapi.testclient import TestClient
from src.backend.server import app, engine

@pytest.fixture(autouse=True)
def reset_engine():
    from src.backend.puzzle_state import PuzzleEngine, GAME_STATE_FILE
    import src.backend.server as srv
    if os.path.exists(GAME_STATE_FILE):
        try:
            os.remove(GAME_STATE_FILE)
        except Exception:
            pass
    srv.engine = PuzzleEngine()

client = TestClient(app)

def _break_disk(monkeypatch):
    """Make every state write fail (as a locked or read-only state file would); returns the real os.replace."""
    real_replace = os.replace

    def refuse(src, dst):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(os, "replace", refuse)
    return real_replace

def _advance_to_phase_4():
    client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "7.00"})
    client.post("/api/event", json={"event_type": "reagent_spray"})
    client.post("/api/event", json={"event_type": "cell_change", "cell": "B18", "value": "S"})
    client.post("/api/event", json={"event_type": "cell_change", "cell": "B18", "value": "SEAL THE DEEP VAULT"})

def test_health_and_status():
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["phase"] == 1
    assert data["row13_awakened"] is False

def test_event_cell_change_phase1_flow():
    # Submit incorrect fee
    res = client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "1.00"})
    assert res.status_code == 200
    data = res.json()
    assert data["accepted"] is False
    assert any(a["effect"] == "SPREAD_BLOOD_SCAB" for a in data["actions"])

    # Submit correct fee
    res = client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "$7.00"})
    assert res.status_code == 200
    data = res.json()
    assert data["accepted"] is True
    assert data["current_phase"] == 2
    assert any(a["command"] == "AWAKEN_ROW_13" for a in data["actions"])

def test_pixel_radar_endpoint():
    res = client.get("/api/pixel_radar")
    assert res.status_code == 200
    data = res.json()
    assert data["rows"] == 30
    assert data["cols"] == 30
    assert "blinking_cells" in data

def test_event_spray_reagent():
    # Move to phase 2 first
    client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "7.00"})
    
    res = client.post("/api/event", json={"event_type": "reagent_spray"})
    assert res.status_code == 200
    data = res.json()
    assert data["accepted"] is True
    assert data["current_phase"] == 3

def test_haunt_and_pending_effects():
    haunt_types = ["cell_text", "flicker_lamp", "thunder_invert", "ink_spread", "whisper", "screen_tremor"]
    
    for idx, ht in enumerate(haunt_types):
        res = client.post("/api/haunt", json={
            "haunt_type": ht,
            "target_cell": f"B{18 + idx}",
            "message": f"HAUNT MSG FOR {ht}"
        })
        assert res.status_code == 200
        assert res.json()["queued"] is True

    # Check status includes all 6 pending effects
    status_res = client.get("/api/status")
    assert len(status_res.json()["pending_effects"]) == 6

    # Next event should pop all pending effects into actions as TRIGGER_HAUNT
    event_res = client.post("/api/event", json={"event_type": "unknown_probe"})
    assert event_res.status_code == 200
    actions = event_res.json().get("actions", [])
    haunt_actions = [a for a in actions if a.get("command") == "TRIGGER_HAUNT"]
    assert len(haunt_actions) == 6
    received_types = [a["haunt_type"] for a in haunt_actions]
    assert received_types == haunt_types
    for a in haunt_actions:
        assert a["cell"].startswith("B")
        assert a["message"].startswith("HAUNT MSG FOR")

    # Pending effects queue should now be empty
    status_after = client.get("/api/status")
    assert len(status_after.json()["pending_effects"]) == 0


def test_banish_endpoint():
    # Advance to Phase 4
    client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "7.00"})
    client.post("/api/event", json={"event_type": "reagent_spray"})
    client.post("/api/event", json={"event_type": "cell_change", "cell": "B18", "value": "S"}) # hijack
    client.post("/api/event", json={"event_type": "cell_change", "cell": "B18", "value": "SEAL THE DEEP VAULT"})

    # Test banish event without phrase in Phase 4 - must be rejected
    res_event_empty = client.post("/api/event", json={"event_type": "banish"})
    assert res_event_empty.status_code == 200
    assert res_event_empty.json()["banished"] is False

    res = client.post("/api/banish", json={"phrase": "SEAL THE DEEP VAULT"})
    assert res.status_code == 200
    data = res.json()
    assert data["banished"] is True
    assert "ARCHIVE SEALED" in data["stamp"]

    # Post-seal repeat banish must also be rejected
    res_after = client.post("/api/banish", json={"phrase": "SEAL THE DEEP VAULT"})
    assert res_after.status_code == 200
    assert res_after.json()["banished"] is False

def test_event_save_failure_returns_500_and_leaves_phase_unchanged(monkeypatch):
    _break_disk(monkeypatch)

    res = client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "7.00"})

    assert res.status_code == 500
    assert "could not be saved" in res.json()["detail"]
    assert res.headers.get("x-content-type-options") == "nosniff"
    status = client.get("/api/status").json()
    assert status["phase"] == 1
    assert status["row13_awakened"] is False

def test_wrong_answer_still_gets_feedback_when_disk_is_broken(monkeypatch):
    _break_disk(monkeypatch)

    res = client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "1.00"})

    assert res.status_code == 200
    assert res.json()["accepted"] is False

def test_haunt_save_failure_returns_500_and_queues_nothing(monkeypatch):
    real_replace = _break_disk(monkeypatch)

    res = client.post("/api/haunt", json={"haunt_type": "whisper", "message": "lost"})

    assert res.status_code == 500
    monkeypatch.setattr(os, "replace", real_replace)
    assert client.get("/api/status").json()["pending_effects"] == []

def test_banish_save_failure_returns_500_and_does_not_seal(monkeypatch):
    _advance_to_phase_4()
    real_replace = _break_disk(monkeypatch)

    res = client.post("/api/banish", json={"phrase": "SEAL THE DEEP VAULT"})

    assert res.status_code == 500
    monkeypatch.setattr(os, "replace", real_replace)
    status = client.get("/api/status").json()
    assert status["archive_sealed"] is False
    assert status["phase"] == 4

def test_reset_save_failure_keeps_current_game(monkeypatch):
    client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "7.00"})
    _break_disk(monkeypatch)

    res = client.post("/api/reset")

    assert res.status_code == 500
    assert client.get("/api/status").json()["phase"] == 2

def test_event_succeeds_when_only_haunt_delivery_cannot_be_saved(monkeypatch):
    client.post("/api/haunt", json={"haunt_type": "whisper", "message": "queued"})
    real_replace = os.replace
    calls = {"count": 0}

    def fail_after_first_write(src, dst):
        calls["count"] += 1
        if calls["count"] > 1:
            raise PermissionError(13, "Permission denied")
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", fail_after_first_write)

    res = client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "7.00"})

    assert res.status_code == 200
    data = res.json()
    assert data["accepted"] is True
    assert not any(a.get("command") == "TRIGGER_HAUNT" for a in data["actions"])
    monkeypatch.setattr(os, "replace", real_replace)
    assert len(client.get("/api/status").json()["pending_effects"]) == 1

def test_deleting_state_file_resets_running_daemon():
    import src.backend.puzzle_state as ps
    client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "7.00"})
    assert client.get("/api/status").json()["phase"] == 2

    os.remove(ps.GAME_STATE_FILE)

    status = client.get("/api/status").json()
    assert status["phase"] == 1
    assert status["row13_awakened"] is False

def test_clearing_fee_cell_gets_no_penalty_effects():
    res = client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": ""})

    assert res.status_code == 200
    data = res.json()
    assert data["accepted"] is False
    assert "actions" not in data

def test_status_exposes_failed_attempts():
    client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "1.00"})
    client.post("/api/event", json={"event_type": "cell_change", "cell": "H7", "value": "2.00"})

    assert client.get("/api/status").json()["attempts"] == {"H7": 2, "B18": 0}

def test_pending_endpoint_delivers_queued_haunts_without_a_player_event():
    client.post("/api/haunt", json={"haunt_type": "cell_text", "target_cell": "A13", "message": "DID ARMITAGE AUTHORIZE THIS?"})
    client.post("/api/haunt", json={"haunt_type": "whisper", "message": "...the floorboards remember..."})

    res = client.get("/api/pending")

    assert res.status_code == 200
    actions = res.json()["actions"]
    assert actions == [
        {"command": "TRIGGER_HAUNT", "haunt_type": "cell_text", "cell": "A13", "message": "DID ARMITAGE AUTHORIZE THIS?"},
        {"command": "TRIGGER_HAUNT", "haunt_type": "whisper", "cell": None, "message": "...the floorboards remember..."},
    ]
    assert client.get("/api/pending").json() == {"actions": []}
    assert client.get("/api/status").json()["pending_effects"] == []

def test_pending_endpoint_keeps_haunts_queued_when_the_pop_cannot_be_saved(monkeypatch):
    client.post("/api/haunt", json={"haunt_type": "whisper", "message": "still here"})
    real_replace = _break_disk(monkeypatch)

    res = client.get("/api/pending")

    assert res.status_code == 500
    monkeypatch.setattr(os, "replace", real_replace)
    assert len(client.get("/api/status").json()["pending_effects"]) == 1
    assert len(client.get("/api/pending").json()["actions"]) == 1
