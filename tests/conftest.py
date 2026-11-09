import os
import sys
import pytest

# Ensure project root is in sys.path so pytest can run without PYTHONPATH=.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import src.backend.puzzle_state as puzzle_state_mod

@pytest.fixture(autouse=True)
def isolate_game_state(monkeypatch, tmp_path):
    """
    Autouse fixture to isolate test game state to a temporary directory.
    Guarantees that real game_state.json files in the project root are never modified or deleted by tests.
    """
    test_state_file = str(tmp_path / "game_state.json")
    monkeypatch.setenv("GAME_STATE_FILE", test_state_file)
    monkeypatch.setattr(puzzle_state_mod, "GAME_STATE_FILE", test_state_file)
    monkeypatch.setattr("tests.test_edge_cases.GAME_STATE_FILE", test_state_file, raising=False)
    monkeypatch.setattr("tests.test_server.GAME_STATE_FILE", test_state_file, raising=False)
    monkeypatch.setattr("tests.test_mcp_server.GAME_STATE_FILE", test_state_file, raising=False)
    yield test_state_file
