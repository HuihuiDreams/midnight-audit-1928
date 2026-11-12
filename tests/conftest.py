import os
import shutil
import sys
import tempfile
import pytest

# Ensure project root is in sys.path so pytest can run without PYTHONPATH=.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Point the state file at a throwaway directory before anything imports src.backend.puzzle_state,
# so even a name bound at import time (from ... import GAME_STATE_FILE) can never reach the real save.
_SESSION_STATE_DIR = tempfile.mkdtemp(prefix="midnight_audit_tests_")
os.environ["GAME_STATE_FILE"] = os.path.join(_SESSION_STATE_DIR, "game_state.json")

import src.backend.puzzle_state as puzzle_state_mod
import src.backend.server as server_mod
import src.backend.mcp_server as mcp_mod

def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(_SESSION_STATE_DIR, ignore_errors=True)

@pytest.fixture(autouse=True)
def isolate_game_state(monkeypatch, tmp_path):
    """
    Autouse fixture: the single isolation entry point for every test.
    Gives each test its own temporary game_state.json and a fresh engine in the server and MCP modules,
    so real game_state.json files in the project root are never read, modified or deleted by tests.
    """
    test_state_file = str(tmp_path / "game_state.json")
    monkeypatch.setenv("GAME_STATE_FILE", test_state_file)
    monkeypatch.setattr(puzzle_state_mod, "GAME_STATE_FILE", test_state_file)
    server_mod.engine = puzzle_state_mod.PuzzleEngine()
    mcp_mod.engine = puzzle_state_mod.PuzzleEngine()
    yield test_state_file

@pytest.fixture
def break_disk(monkeypatch):
    """
    Returns a callable that makes every state write fail (as a locked or read-only state file would).
    The callable returns the real os.replace so a test can restore it.
    """
    real_replace = os.replace

    def refuse(src, dst):
        raise PermissionError(13, "Permission denied")

    def apply():
        monkeypatch.setattr(os, "replace", refuse)
        return real_replace

    return apply
