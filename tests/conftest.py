import os
import sys
import pytest

# Ensure project root is in sys.path so pytest can run without PYTHONPATH=.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.backend.puzzle_state import GAME_STATE_FILE

def _remove_game_state_file():
    if os.path.exists(GAME_STATE_FILE):
        try:
            os.remove(GAME_STATE_FILE)
        except OSError:
            pass

@pytest.fixture(autouse=True)
def clean_game_state():
    """Autouse fixture to clean up game_state.json before and after every test."""
    _remove_game_state_file()
    try:
        yield
    finally:
        _remove_game_state_file()

@pytest.fixture(autouse=True, scope="session")
def clean_game_state_session():
    """Ensure game_state.json is cleaned up before and after the entire test session."""
    _remove_game_state_file()
    try:
        yield
    finally:
        _remove_game_state_file()

def pytest_sessionfinish(session, exitstatus):
    """Guaranteed hook invoked at the end of the test session."""
    _remove_game_state_file()

