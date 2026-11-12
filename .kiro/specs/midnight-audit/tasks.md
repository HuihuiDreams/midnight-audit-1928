# Implementation Plan — The Midnight Audit (1928)

> Traces to [`requirements.md`](requirements.md) and [`design.md`](design.md).

## Core Engine & Bridges

- [x] 1. Implement `PuzzleEngine` 4-phase state machine in `src/backend/puzzle_state.py`
  - Phase 1 fee check on `H7`, Row 13 awakening, censored rows 14–16 reveal
  - Phase 2 reagent spray and 30×30 radar matrix with eye cells `W34:X35`
  - Phase 3 hijack text and ROT-3 phrase check on `B18`
  - Phase 4 banishment, Cold Ash stamp, no victory replay once sealed
  - _Requirements: 1, 2, 3, 4_
- [x] 2. Persist state to `game_state.json` with `file_lock` (fcntl / msvcrt, re-entrant, `0o600`) and atomic `os.replace` writes
  - _Requirements: 7.3, 7.5_
- [x] 3. Build FastAPI Daemon `src/backend/server.py` (`/api/status`, `/api/event`, `/api/pixel_radar`, `/api/haunt`, `/api/banish`, `/api/reset`) with origin check and security headers
  - _Requirements: 4.1, 7.9_
- [x] 4. Build MCP stdio server `src/backend/mcp_server.py` with `inspect_ledger`, `haunt_spreadsheet`, `judge_ritual`
  - _Requirements: 7.1–7.8_

## Excel Client

- [x] 5. Write VBA modules `M_Bootstrap.bas`, `M_DaemonBridge.bas`, `M_HorrorFX.bas`, `Sheet1_Archive.cls`, `ThisWorkbook.cls`
  - PtrSafe conditional compilation, macOS fallbacks, `Ctrl+Shift+R` EmergencyReset, timer cleanup
  - _Requirements: 6_
- [x] 6. Implement `HandleOfflineEvent` mirroring all four phase rules without the Daemon
  - _Requirements: 6.1_
- [x] 7. Generate `Midnight_Audit_1928_Template.xlsx` via `scripts/build_ledger.py` inside `A1:AN50`
  - Row 13 Abyss at 220 pt, 30×30 radar at `K20:AN49`, Row 50 plaques flush on both wings
  - Diegetic documents only: ledger, Ward's note `K4:AN12`, protocol card `K13:AN16`, cipher strip `B21:H28`, Armitage memorandum `B30:H48`
  - _Requirements: 5_

## Kiro-Native Integration (v1.3.0)

- [x] 8. Register `midnight-audit-mcp` in `.kiro/settings/mcp.json` (`uv run --with-requirements requirements.txt python -m src.backend.mcp_server`, `disabled: false`, `autoApprove` for all three tools)
  - _Requirements: 7_
- [x] 9. Add canonical spec folder `.kiro/specs/midnight-audit/` (requirements, design, tasks), keeping `mcp_contract.md` and `puzzle_engine_spec.md`
- [x] 10. Add verification hook `.kiro/hooks/verify-backend-and-ledger.json` (PostFileSave on `src/backend/*.py` and `scripts/build_ledger.py` → pytest, then template rebuild)
- [x] 11. Confirm `.gitignore` does not exclude `.kiro/specs`, `.kiro/steering`, `.kiro/hooks`, or `.kiro/settings/mcp.json`

## Release 1.3.0 Verification

- [x] 12. Bump `serverInfo.version` (`mcp_server.py`) and FastAPI `version` (`server.py`) to `1.3.0`
  - Verify: `tests/test_kiro_integration.py` version assertions pass
- [x] 13. Cut `CHANGELOG.md` `[Unreleased]` to `## [1.3.0] - 2026-11-12`
- [x] 14. Regenerate the template: `.venv/bin/python scripts/build_ledger.py`
  - Verify: `Midnight_Audit_1928_Template.xlsx` rewritten without errors
- [x] 15. Run the full suite: `.venv/bin/pytest`
  - Verify: 100% pass, zero failures
- [ ] 16. Manual smoke test in Excel (Windows and macOS): import VBA modules, play Phase 1 → 4 with the Daemon running, then again offline
  - Verify: archive sealed stamp appears in both modes; `Ctrl+Shift+R` restores the UI
