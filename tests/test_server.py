import pytest
from starlette.testclient import TestClient
from src.backend.server import app, engine

@pytest.fixture(autouse=True)
def reset_engine():
    # Reset engine before each test
    from src.backend.puzzle_state import PuzzleEngine
    import src.backend.server as srv
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
    # Queue a haunt
    res = client.post("/api/haunt", json={"haunt_type": "whisper", "target_cell": "B18", "message": "TEST WHISPER"})
    assert res.status_code == 200
    assert res.json()["queued"] is True

    # Check status includes pending effect
    status_res = client.get("/api/status")
    assert len(status_res.json()["pending_effects"]) == 1

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
