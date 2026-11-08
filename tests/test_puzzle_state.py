import pytest
from src.backend.puzzle_state import PuzzleEngine, PhaseEnum, PALETTE

def test_initial_puzzle_state():
    engine = PuzzleEngine()
    state = engine.get_state()
    assert state["phase"] == 1
    assert state["phase_name"] == PhaseEnum.THE_AUDIT_DISCREPANCY.value
    assert state["row13_awakened"] is False
    assert state["intruder_revealed"] is False
    assert state["archive_sealed"] is False
    assert len(state["pending_effects"]) == 0

def test_phase_1_verification_invalid():
    engine = PuzzleEngine()
    # Invalid fee (expected 7.00 for 140 days * 0.05)
    res = engine.handle_cell_change("H7", "5.00")
    assert res["accepted"] is False
    assert engine.current_phase == PhaseEnum.THE_AUDIT_DISCREPANCY
    assert engine.row13_awakened is False

    # Non-numeric input
    res = engine.handle_cell_change("H7", "invalid_text")
    assert res["accepted"] is False

def test_phase_1_verification_success():
    engine = PuzzleEngine()
    # Accept $7.00, 7.00, 7, " 7.00 "
    res = engine.handle_cell_change("H7", "$7.00")
    assert res["accepted"] is True
    assert engine.current_phase == PhaseEnum.THE_UNSEEN_INTRUDER
    assert engine.row13_awakened is True
    
    actions = res["actions"]
    assert any(a["command"] == "AWAKEN_ROW_13" for a in actions)
    assert any(a["command"] == "TRIGGER_FX" and a["effect"] == "THUD_BEEP" for a in actions)
    assert any(a["command"] == "SET_VALUE" and a["cell"] == "I7" and "BALANCED" in a["value"] for a in actions)

def test_phase_2_pixel_radar_generation():
    engine = PuzzleEngine()
    # Trigger Phase 1 first
    engine.handle_cell_change("H7", "7.00")
    assert engine.current_phase == PhaseEnum.THE_UNSEEN_INTRUDER

    radar = engine.get_pixel_radar()
    assert radar["rows"] == 30
    assert radar["cols"] == 30
    assert radar["start_cell"] == "K20"
    assert len(radar["grid"]) == 30
    assert len(radar["grid"][0]) == 30
    
    # Check that colors in grid belong to PALETTE
    valid_colors = set(PALETTE.values())
    for row in radar["grid"]:
        for cell_color in row:
            assert cell_color in valid_colors

    assert len(radar["blinking_cells"]) > 0
    assert "W34" in radar["blinking_cells"]

    # Triggering spray developer advances to Phase 3
    res = engine.handle_reagent_spray()
    assert res["accepted"] is True
    assert engine.current_phase == PhaseEnum.HIJACKED_CIPHER
    assert engine.intruder_revealed is True

def test_phase_3_hijack_and_cipher():
    engine = PuzzleEngine()
    engine.handle_cell_change("H7", "7.00")
    engine.handle_reagent_spray()
    assert engine.current_phase == PhaseEnum.HIJACKED_CIPHER

    # First typing into B18 triggers ghost hijack
    hijack_res = engine.handle_cell_change("B18", "S")
    assert hijack_res["hijacked"] is True
    assert "YOUR SALARY CANNOT SAVE YOU" in hijack_res["ghost_text"]

    # Wrong code
    wrong_res = engine.handle_cell_change("B18", "WRONG CIPHER CODE")
    assert wrong_res["accepted"] is False
    assert engine.current_phase == PhaseEnum.HIJACKED_CIPHER

    # Correct code "SEAL THE DEEP VAULT" (case-insensitive, trimmed)
    correct_res = engine.handle_cell_change("B18", "  seal the deep vault  ")
    assert correct_res["accepted"] is True
    assert engine.current_phase == PhaseEnum.MIDNIGHT_SETTLEMENT
    assert any(a["command"] == "UNLOCK_BUTTON" for a in correct_res["actions"])

def test_phase_4_banishment():
    engine = PuzzleEngine()
    engine.handle_cell_change("H7", "7.00")
    engine.handle_reagent_spray()
    # First input triggers hijack
    engine.handle_cell_change("B18", "S")
    # Second input enters override code
    engine.handle_cell_change("B18", "SEAL THE DEEP VAULT")
    assert engine.current_phase == PhaseEnum.MIDNIGHT_SETTLEMENT

    # Invalid banishment
    fail_res = engine.judge_ritual("HELLO GHOST")
    assert fail_res["banished"] is False

    # Valid banishment
    success_res = engine.judge_ritual("SEAL THE DEEP VAULT")
    assert success_res["banished"] is True
    assert engine.archive_sealed is True
    assert "ARCHIVE SEALED" in success_res["stamp"]
    assert any(a["effect"] == "THUNDER_STROBE" for a in success_res["actions"])
    assert any(a["effect"] == "SCREEN_TREMOR" for a in success_res["actions"])

def test_haunt_queue():
    engine = PuzzleEngine()
    engine.queue_haunt("flicker_lamp", "A1", "Flicker test")
    assert len(engine.pending_effects) == 1
    state = engine.get_state()
    assert len(state["pending_effects"]) == 1
    popped = engine.pop_pending_effects()
    assert len(popped) == 1
    assert len(engine.pending_effects) == 0
