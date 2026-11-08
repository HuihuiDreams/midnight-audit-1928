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

    res = client.post("/api/banish", json={"phrase": "SEAL THE DEEP VAULT"})
    assert res.status_code == 200
    data = res.json()
    assert data["banished"] is True
    assert "ARCHIVE SEALED" in data["stamp"]

    # Test banish event without phrase in Phase 4
    res_event = client.post("/api/event", json={"event_type": "banish"})
    assert res_event.status_code == 200
    assert res_event.json()["banished"] is True
