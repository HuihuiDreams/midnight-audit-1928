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

## Post-Audit Hardening

- [x] 17. `save_state` raises `StateSaveError`; mutating calls roll back; daemon answers `500`, MCP answers `isError`
- [x] 18. Count rejected entries (`attempts`), expose them in `/api/status` and `inspect_ledger`; add `GET /api/pending`
- [x] 19. Share one 30×30 entity face between Python and VBA (`ENTITY_FACE_MATRIX` → `scripts/sync_vba_radar.py`)
- [x] 20. Split `requirements.txt` (runtime) from `requirements-dev.txt` (tests)
- [ ] 21. In Excel: confirm haunt polling (queue a haunt with the MCP tool while idle, expect it within ~3 s), `Ctrl+Shift+R` stops it, sealing protects the sheet and `Ctrl+Shift+R` lifts it
- [ ] 22. In Excel for Mac: confirm the `MacScript` + `/tmp` transport reaches the daemon; if `/tmp` writes are denied, switch the temp file to `Environ("TMPDIR")`
- [x] 23. Bump `serverInfo.version` and FastAPI `version` to `1.3.1`; cut `CHANGELOG.md` `[Unreleased]` to `## [1.3.1] - 2026-11-12`

## Dread Upgrade (Video Demo)

- [x] 24. Midnight clock (`StartMidnightClock` / `MidnightClockTick` / `StopMidnightClock`) with late interest on rejected entries (`ChargeLateInterest`) and live time in `G1`, status bar and whispers
  - _Requirements: 8.1, 8.2, 8.8_
- [x] 25. Widening Row 13 abyss (`GrowAbyssTo`, `CloseAbyss`) and the midnight foreclosure ending (`ForecloseLedger`)
  - _Requirements: 8.3, 8.4, 8.5_
- [x] 26. Camera moves (`CameraMove`, `CameraDollyToAbyss`, radar lean-in inside `RenderPixelFace`)
  - _Requirements: 8.6_
- [x] 27. Entity gaze (`TrackEntityGaze`; `ToggleEyeBlink` follows the pupil)
  - _Requirements: 8.7_
- [ ] 28. In Excel (record on whichever of Windows / macOS runs smoothest): play to the seal and confirm the clock ticks, wrong entries cost a minute, Row 13 widens and closes on seal, both camera moves return or settle correctly, and the pupil follows selections; then let the clock run out and confirm the foreclosure stamp and that reopening restarts the clock
  - Tune `CLOCK_TICK_INTERVAL`, `CAMERA_FRAMES` and the zoom offsets in `M_HorrorFX.bas` if the recording looks too fast or too slow
  - Balance: the 260 s budget includes the camera and reveal animations, and each wrong entry costs 20 s; check that a first-time player can still solve the ROT-3 strip in time
  - Phase 3 view (scroll row 14) puts the `G1` clock off screen, leaving only the status bar; check whether the pressure still reads on video, and if not, consider showing the time in the `E18:I18` HUD as well

## Backlog (recorded, not scheduled)

Ideas from the gameplay and visual review, kept for later. All stay inside Excel + VBA, the 10-color palette and the `A1:AN50` canvas.
- [ ] B1. **Limited reagent search (Phase 2 gameplay)**: five doses; double-clicking a radar cell (`BeforeDoubleClick`) develops a 5x5 patch, and the player has to find the eye before the doses run out. The density of `#REF!` glyphs nearby hints at the distance, and an empty patch costs a minute. Heavier alternative: an 8x8 nonogram whose row and column totals must balance like ledger columns, drawing the entity when solved.
- [ ] B2. **Forged seal button (Phase 3 gameplay)**: after the correct phrase, light both `[ SEAL ARCHIVE ]` and a forged `[ UNSEAL ARCHIVE ]`; only Armitage's memorandum (`B30:H48`) tells which is real. `Worksheet_Change` fires only on Enter, so a per-keystroke hijack is not possible.
- [ ] B3. **Your name in the ledger**: on foreclosure, append `ARK-0014 | <Application.UserName> | DUE 1928-10-31 | OVERDUE: FOREVER` (local only, never sent to the daemon). Add "the entity remembers you" on reopen via `game_state.json`.
- [ ] B4. **Kerosene lamp radius**: two defined names hold the selected row and column; a conditional format `=MAX(ABS(ROW()-CurRow),ABS(COLUMN()-CurCol))>3` blacks out everything outside the lamp, with the radius shrinking in Phase 3.
- [ ] B5. **Numbers that change their face**: swap `NumberFormat` (e.g. `"OWED";"OWED"`) so every amount reads `OWED` without changing a value.
- [ ] B6. **Kiro hook as horror director**: watch `game_state.json`, have the agent run `inspect_ledger` and decide whether to haunt. First verify that a file written by the daemon (not by the IDE) triggers a Kiro file hook.
- [ ] B7. **Per-run puzzle answers**: the agent (or VBA `Rnd` offline) picks overdue days, fee rate, ROT shift and phrase, with all clues kept consistent.
- [ ] B8. **Typewriter replies**: a confession cell on Ward's note; the agent answers in the Wilbur persona, typed out letter by letter (~40 ms per letter), with canned replies offline.
- [ ] B9. **Agent-painted sigil**: an MCP `paint_radar` tool lets the agent draw a new 30x30 sigil per run, validated against the palette.
- Rejected: formula trace arrows (`ShowDependents`) as tentacles, because their color is fixed blue/red outside the palette; `Application.Speech` whispers, because they are missing on Mac and break the silence rule.
- Open question: the seal stamp still reads `00:01 AM` while the clock's deadline is midnight. Decide whether the stamp should show the actual sealing time (this touches `judge_ritual`'s `stamp`, `mcp_contract.md` and the tests that pin it).
