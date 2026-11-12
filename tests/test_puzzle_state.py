import os
import pytest
from src.backend.puzzle_state import PuzzleEngine, PhaseEnum, PALETTE, StateSaveError

def _engine_at_phase(phase):
    engine = PuzzleEngine()
    if phase >= 2:
        engine.handle_cell_change("H7", "7.00")
    if phase >= 3:
        engine.handle_reagent_spray()
    if phase >= 4:
        engine.handle_cell_change("B18", "S")
        engine.handle_cell_change("B18", "SEAL THE DEEP VAULT")
    return engine

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
    assert any(a.get("effect") == "SPREAD_BLOOD_SCAB" for a in res["actions"])

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

def test_state_persistence(tmp_path):
    state_file = str(tmp_path / "test_game_state.json")
    engine1 = PuzzleEngine()
    engine1.handle_cell_change("H7", "7.00")
    engine1.save_state(state_file)

    engine2 = PuzzleEngine()
    loaded = engine2.load_state(state_file)
    assert loaded is True
    assert engine2.phase_number == 2
    assert engine2.row13_awakened is True

def test_save_state_failure_raises_and_leaves_no_temp_files(tmp_path, capsys, break_disk):
    target = tmp_path / "failing_game_state.json"
    break_disk()

    with pytest.raises(StateSaveError):
        PuzzleEngine().save_state(str(target))

    assert "Error saving game state" in capsys.readouterr().err
    assert not target.exists()
    assert [p.name for p in tmp_path.iterdir() if p.suffix != ".lock"] == []

def test_phase_1_save_failure_rolls_back_memory(break_disk):
    engine = PuzzleEngine()
    break_disk()

    with pytest.raises(StateSaveError):
        engine.handle_cell_change("H7", "7.00")

    assert engine.phase_number == 1
    assert engine.row13_awakened is False
    assert engine.ledger_data[7]["fee"] is None
    assert engine.ledger_data[7]["status"] == "FLAGGED"

def test_reagent_spray_save_failure_rolls_back_memory(break_disk):
    engine = _engine_at_phase(2)
    break_disk()

    with pytest.raises(StateSaveError):
        engine.handle_reagent_spray()

    assert engine.phase_number == 2
    assert engine.intruder_revealed is False

def test_hijack_save_failure_rolls_back_so_next_entry_still_hijacks(monkeypatch, break_disk):
    engine = _engine_at_phase(3)
    real_replace = break_disk()

    with pytest.raises(StateSaveError):
        engine.handle_cell_change("B18", "S")
    assert engine.hijack_triggered is False

    monkeypatch.setattr(os, "replace", real_replace)
    assert engine.handle_cell_change("B18", "S")["hijacked"] is True

def test_override_code_save_failure_keeps_phase_3(break_disk):
    engine = _engine_at_phase(3)
    engine.handle_cell_change("B18", "S")
    break_disk()

    with pytest.raises(StateSaveError):
        engine.handle_cell_change("B18", "SEAL THE DEEP VAULT")

    assert engine.phase_number == 3

def test_ritual_save_failure_does_not_seal_archive(break_disk):
    engine = _engine_at_phase(4)
    break_disk()

    with pytest.raises(StateSaveError):
        engine.judge_ritual("SEAL THE DEEP VAULT")

    assert engine.archive_sealed is False
    assert engine.phase_number == 4

def test_haunt_queue_save_failure_rolls_back(break_disk):
    engine = PuzzleEngine()
    break_disk()

    with pytest.raises(StateSaveError):
        engine.queue_haunt("whisper", None, "lost")

    assert engine.pending_effects == []

def test_pop_pending_effects_save_failure_keeps_effects_queued(break_disk):
    engine = PuzzleEngine()
    engine.queue_haunt("whisper", None, "still queued")
    break_disk()

    with pytest.raises(StateSaveError):
        engine.pop_pending_effects()

    assert len(engine.pending_effects) == 1

def test_rejected_inputs_do_not_need_the_disk(break_disk):
    phase_1 = PuzzleEngine()
    phase_3 = _engine_at_phase(3)
    phase_3.handle_cell_change("B18", "S")
    phase_4 = _engine_at_phase(4)
    break_disk()

    assert phase_1.handle_cell_change("H7", "1.00")["accepted"] is False
    assert phase_1.handle_cell_change("H7", "not a number")["accepted"] is False
    assert phase_3.handle_cell_change("B18", "WRONG CODE")["accepted"] is False
    assert phase_4.judge_ritual("HELLO GHOST")["banished"] is False

def test_missing_state_file_resets_engine_to_new_game():
    engine = _engine_at_phase(3)
    from src.backend.puzzle_state import GAME_STATE_FILE
    assert os.path.exists(GAME_STATE_FILE)
    os.remove(GAME_STATE_FILE)

    assert engine.load_state() is False

    assert engine.phase_number == 1
    assert engine.row13_awakened is False
    assert engine.intruder_revealed is False
    assert engine.ledger_data[7]["fee"] is None
    assert engine.ledger_data[7]["status"] == "FLAGGED"

@pytest.mark.parametrize("empty_value", ["", "   ", None])
def test_empty_entry_is_ignored_without_penalty(empty_value):
    phase_1 = PuzzleEngine()
    res = phase_1.handle_cell_change("H7", empty_value)
    assert res["accepted"] is False
    assert "actions" not in res
    assert phase_1.phase_number == 1

    phase_3 = _engine_at_phase(3)
    res = phase_3.handle_cell_change("B18", empty_value)
    assert res["accepted"] is False
    assert "actions" not in res
    assert phase_3.hijack_triggered is False

def test_wrong_fee_attempts_are_counted():
    engine = PuzzleEngine()
    assert engine.get_state()["attempts"] == {"H7": 0, "B18": 0}

    engine.handle_cell_change("H7", "5.00")
    engine.handle_cell_change("H7", "not a number")
    engine.handle_cell_change("H7", "")          # cleared cell is not an attempt
    assert engine.attempts["H7"] == 2

    engine.handle_cell_change("H7", "7.00")      # the correct fee is not a failed attempt
    assert engine.attempts["H7"] == 2

def test_wrong_cipher_attempts_are_counted_but_the_hijack_is_not():
    engine = _engine_at_phase(3)

    engine.handle_cell_change("B18", "S")        # first entry is hijacked, not judged
    assert engine.attempts["B18"] == 0

    engine.handle_cell_change("B18", "WRONG")
    engine.handle_cell_change("B18", "STILL WRONG")
    assert engine.attempts["B18"] == 2

    engine.handle_cell_change("B18", "SEAL THE DEEP VAULT")
    assert engine.attempts["B18"] == 2

def test_attempts_persist_across_load_and_reset_with_a_new_game(tmp_path):
    state_file = str(tmp_path / "attempts_state.json")
    engine = PuzzleEngine()
    engine.handle_cell_change("H7", "1.00")
    engine.save_state(state_file)

    reloaded = PuzzleEngine()
    reloaded.load_state(state_file)
    assert reloaded.attempts["H7"] == 1

    assert PuzzleEngine().attempts == {"H7": 0, "B18": 0}

def test_attempt_counting_never_turns_feedback_into_an_error(break_disk):
    engine = PuzzleEngine()
    break_disk()

    res = engine.handle_cell_change("H7", "1.00")

    assert res["accepted"] is False
    assert "actions" in res

def test_entity_face_matrix_is_30x30_and_uses_only_legend_characters():
    from src.backend.puzzle_state import ENTITY_FACE_MATRIX, ENTITY_FACE_LEGEND

    assert len(ENTITY_FACE_MATRIX) == 30
    assert {len(row) for row in ENTITY_FACE_MATRIX} == {30}
    assert set("".join(ENTITY_FACE_MATRIX)) <= set(ENTITY_FACE_LEGEND)
    assert set(ENTITY_FACE_LEGEND.values()) <= set(PALETTE)

def test_pixel_radar_grid_is_built_from_the_face_matrix():
    from src.backend.puzzle_state import ENTITY_FACE_MATRIX, ENTITY_FACE_LEGEND

    grid = PuzzleEngine().get_pixel_radar()["grid"]

    for r, row in enumerate(ENTITY_FACE_MATRIX):
        for c, ch in enumerate(row):
            assert grid[r][c] == PALETTE[ENTITY_FACE_LEGEND[ch]]

@pytest.mark.parametrize("haunt_type,target", [
    ("cell_text", "A1:AN50"),      # 2,000 cells would be overwritten by one message
    ("cell_text", "K20:K21"),      # cell_text writes one cell, never a range
    ("ink_spread", "A1:AN50"),     # range larger than 900 cells
    ("ink_spread", "A1:XFD1048576"),
    ("cell_text", "ZZZ1"),         # column beyond XFD
    ("cell_text", "XFE1"),
    ("cell_text", "A1048577"),     # row beyond the sheet
    ("cell_text", "A0"),
    ("cell_text", "A01"),
    ("cell_text", "A1:B2:C3"),
])
def test_queue_haunt_rejects_targets_outside_the_sheet_or_too_large(haunt_type, target):
    engine = PuzzleEngine()

    with pytest.raises(ValueError):
        engine.queue_haunt(haunt_type, target, "x")

    assert engine.pending_effects == []

@pytest.mark.parametrize("haunt_type,target", [
    ("cell_text", "A1"),
    ("cell_text", "xfd1048576"),   # last cell of the sheet; also lower case
    ("cell_text", "A100000"),      # rows above 99,999 are real rows
    ("ink_spread", "K20:AN49"),    # the 30x30 radar, exactly 900 cells
    ("ink_spread", "W34:X35"),
    ("whisper", "B18"),
])
def test_queue_haunt_accepts_designed_targets(haunt_type, target):
    engine = PuzzleEngine()

    engine.queue_haunt(haunt_type, target, "x")

    assert engine.pending_effects[0]["target_cell"] == target.upper()

def test_corrupt_state_file_is_not_half_loaded(tmp_path):
    path = tmp_path / "game_state.json"
    path.write_text('{"current_phase": "THE_UNSEEN_INTRUDER", "attempts": {"H7": "x"}}', encoding="utf-8")
    engine = PuzzleEngine()

    assert engine.load_state() is False

    assert engine.current_phase == PhaseEnum.THE_AUDIT_DISCREPANCY
    assert engine.attempts == {"H7": 0, "B18": 0}

def test_corrupt_state_file_is_kept_as_a_copy_before_it_is_overwritten(tmp_path):
    path = tmp_path / "game_state.json"
    corrupt = '{"current_phase": "THE_UNSEEN_INTRUDER", "attempts": {"H7": "x"}}'
    path.write_text(corrupt, encoding="utf-8")
    engine = PuzzleEngine()

    engine.queue_haunt("whisper", None, "after the corruption")

    assert (tmp_path / "game_state.json.corrupt").read_text(encoding="utf-8") == corrupt
    assert "after the corruption" in path.read_text(encoding="utf-8")

def test_non_object_state_file_is_rejected_without_changing_the_engine(tmp_path):
    (tmp_path / "game_state.json").write_text('["not", "an", "object"]', encoding="utf-8")
    engine = PuzzleEngine()

    assert engine.load_state() is False
    assert engine.current_phase == PhaseEnum.THE_AUDIT_DISCREPANCY

def test_polling_an_empty_queue_does_not_write_the_state_file(tmp_path):
    engine = PuzzleEngine()
    engine.save_state()
    path = tmp_path / "game_state.json"
    before = path.stat().st_mtime_ns
    inode = path.stat().st_ino

    assert engine.pop_pending_effects() == []

    assert path.stat().st_mtime_ns == before
    assert path.stat().st_ino == inode

def test_pop_pending_effects_still_drains_and_saves_a_non_empty_queue():
    engine = PuzzleEngine()
    engine.queue_haunt("whisper", None, "one")

    assert [e["message"] for e in engine.pop_pending_effects()] == ["one"]
    assert PuzzleEngine(load_existing=True).pending_effects == []

@pytest.mark.parametrize("pending", ["abc", [{}], [None], [1, "x"], [{"type": "nope"}], [{"type": ["cell_text"]}], {"type": "whisper"}])
def test_bad_pending_entries_are_dropped_without_discarding_the_rest_of_the_save(tmp_path, pending):
    import json
    good = {"type": "whisper", "target_cell": None, "message": "kept"}
    (tmp_path / "game_state.json").write_text(json.dumps({
        "current_phase": "HIJACKED_CIPHER",
        "pending_effects": [good] + pending if isinstance(pending, list) else pending,
    }), encoding="utf-8")
    engine = PuzzleEngine()

    assert engine.load_state() is True

    assert engine.phase_number == 3
    assert engine.pending_effects == ([good] if isinstance(pending, list) else [])

def test_pending_entry_missing_optional_fields_is_completed_and_a_built_action_is_kept(tmp_path):
    import json
    (tmp_path / "game_state.json").write_text(json.dumps({
        "pending_effects": [{"type": "whisper"}, {"command": "LOCK_SHEET"}],
    }), encoding="utf-8")
    engine = PuzzleEngine()

    engine.load_state()

    assert engine.pending_effects == [
        {"type": "whisper", "target_cell": None, "message": None},
        {"command": "LOCK_SHEET"},
    ]

@pytest.mark.parametrize("content", ["[]", "{}", "null", '"text"'])
def test_empty_or_non_object_state_file_is_rejected(tmp_path, content):
    (tmp_path / "game_state.json").write_text(content, encoding="utf-8")
    engine = PuzzleEngine()

    assert engine.load_state() is False
    assert engine.current_phase == PhaseEnum.THE_AUDIT_DISCREPANCY

def test_persistently_corrupt_save_is_copied_once_not_on_every_load(tmp_path):
    path = tmp_path / "game_state.json"
    path.write_text("{broken", encoding="utf-8")
    backup = tmp_path / "game_state.json.corrupt"
    engine = PuzzleEngine()

    engine.load_state()
    first = backup.stat().st_mtime_ns
    engine.load_state()

    assert backup.stat().st_mtime_ns == first
    path.write_text("{broken differently", encoding="utf-8")
    engine.load_state()
    assert backup.read_text(encoding="utf-8") == "{broken differently"

@pytest.mark.parametrize("val", [7, 7.0, "7", "7.0", "7.00", "$7", "$7.00", "  7.00  "])
def test_h7_accepts_plain_numbers_without_currency_symbol(val):
    engine = PuzzleEngine()
    res = engine.handle_cell_change("H7", val)
    assert res["accepted"] is True
    assert engine.current_phase == PhaseEnum.THE_UNSEEN_INTRUDER
