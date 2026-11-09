# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.1]

### Security

- **Security Headers & Cross-Origin Protection**: Added `SecurityHeadersAndOriginMiddleware` configuring `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy: default-src 'none'`, and `Referrer-Policy: no-referrer`, while rejecting untrusted external browser `Origin` headers to mitigate CSRF and DNS rebinding attacks.
- **Input Validation & DoS Protection**: Enforced strict validation and length bounds across API request models (`EventRequest`, `HauntRequest`, `BanishRequest`), capped `pending_effects` queue to prevent unbounded disk/memory growth, and limited ritual phrase normalization buffers.
- **Strict Haunt Type Enforcement**: Gated `queue_haunt` and `/api/haunt` to strictly accept only recognized haunt types (`cell_text`, `flicker_lamp`, `thunder_invert`, `ink_spread`, `whisper`, `screen_tremor`), returning 400 Bad Request on unrecognized payloads.
- **Lockfile Permission Hardening**: Restricted file permissions on `game_state.json.lock` from `0o666` to `0o600` (owner read/write only).
- **VBA Transport Symlink Mitigation**: Added pre-execution file unlinking (`Kill tmpFile`) before temporary file creation on macOS to prevent symlink-following attacks.
- **Excel Injection & Coordinate Validation**: Hardened VBA action handlers (`SET_VALUE`, `HIJACK_TYPE`, `SPREAD_BLOOD_SCAB`) to validate cell coordinates via `IsValidCellAddress` and neutralize formula injection prefixes (`=`, `+`, `-`, `@`) even when preceded by whitespace.

## [1.2.0]

### Added

- Halloween atmospheric setting (October 31, 1928 / All Hallows' Eve) across ledger subtitles, status bars, and banishment stamps.
- Ambient horror whisper system (`TriggerAmbientWhisper`) in Excel status bar cycling atmospheric textual cues at timed intervals.
- Torchlight absorption visual effect (`FlashAbyssAbsorption`) when the user selects Row 13 ("He Sleeps Beneath the Floorboards").
- Automated cleanup handlers for `Application.OnTime` timers in `Workbook_BeforeClose` and `EmergencyReset`.

### Changed

- Updated archive sealing timestamp and banish stamp across specifications, backend, VBA, and template generator to `OCTOBER 31, 1928 - 00:01 AM`.

### Fixed

- Prevented Excel from ghost-reopening after workbook closure caused by lingering background `Application.OnTime` timer schedules (`StopEyeBlink` and `CancelAmbientWhisper`).

## [1.1.2]

### Changed

- Unified color palette configuration source in `scripts/build_ledger.py` with `.kiro/steering/aesthetic_autopsy.md`.

### Fixed

- Prevented infinite retriggering of victory audio/visual sequences once the archive has been sealed (`archive_sealed is True`).
- Gated Phase 4 banishment requests to reject empty or blank submission strings.
- Resolved server port conflicts during automated test execution via configurable `SERVER_PORT` environment variable and ephemeral test ports.
- Normalized whitespace handling in VBA offline ritual verification to align with backend regex parsing.
- Aligned VBA `RenderPixelFace` coordinates 1:1 with backend 30x30 pixel radar layout, including entity mouth rendering (`Z41:AE42`).
- Removed obsolete `GAME_STATE_FILE` monkeypatching logic from pytest fixtures.

## [1.1.1]

### Added

- Inter-process file locking (`file_lock`) supporting Unix `fcntl`, Windows `msvcrt`, and lockfile fallbacks to ensure safe concurrent state access between Python Daemon and MCP Agent.
- Multi-format coordinate and range parser (`parse_range_rows`) supporting coordinates (`H7`), row numbers (`7`, `Row 7`), and cell ranges (`A6:I12`).
- Comprehensive regression and concurrency test suite in `tests/test_fixes_verification.py`.

### Changed

- Clarified document class module wiring (`Sheet1_Archive.cls` and `ThisWorkbook.cls`) in `README.md`.

### Fixed

- Crash in MCP tool `inspect_ledger` when handling range or row format variations.
- Race conditions and state desynchronization between daemon processes and MCP tool handlers.
- Improved HTTP error resilience, request timeouts, and PtrSafe cross-platform API declarations in VBA bridge modules.

## [1.1.0]

### Added

- State persistence mechanism saving and loading puzzle progression via `game_state.json` with atomic temporary file writes.
- Serialization methods (`to_dict` and `from_dict`) on `PuzzleEngine`.
- Supernatural Anomaly Dossier output in MCP `inspect_ledger` tool when `include_anomalies=True` is provided.
- Pure-VBA JSON parser and command dispatcher in `M_DaemonBridge.bas` to handle complex nested server responses and batched haunting actions (`TRIGGER_HAUNT`, `TRIGGER_FX`, `AWAKEN_ROW_13`, etc.).
- Pytest teardown hooks in `tests/conftest.py` ensuring clean test state isolation.
- Edge case test coverage for state serialization and JSON parsing.

### Changed

- Initialized `PuzzleEngine` with `load_existing=True` in server and MCP entrypoints to preserve game state across restarts.

## [1.0.0]

### Added

- Core 4-phase puzzle engine (`PuzzleEngine`) implementing:
  - Phase 1: Audit Discrepancy & overdue fine calculation ($7.00 for Wilbur Whateley in row 7) with Row 13 awakening.
  - Phase 2: Unseen Intruder detection with reagent spray and 30x30 pixel radar manifestation.
  - Phase 3: ROT-3 cipher decryption (`VHDO WKH GHHS YDXOW` -> `SEAL THE DEEP VAULT`) and typewriter hijacking horror sequence.
  - Phase 4: Midnight Settlement banishing ritual with thunder strobe and archive sealing stamp.
- FastAPI local daemon bridge providing REST API endpoints (`/api/status`, `/api/event`, `/api/pixel_radar`, `/api/haunt`, `/api/banish`, `/api/reset`).
- Model Context Protocol (MCP) server providing tools (`inspect_ledger`, `haunt_spreadsheet`, `judge_ritual_phrase`, `get_puzzle_state`) for Kiro IDE agent integration.
- Excel VBA 1990s client suite:
  - `M_Bootstrap.bas`: Macro-free workbook initialization, UI lock down, and emergency reset hotkey (`Ctrl + Shift + R`).
  - `M_DaemonBridge.bas`: HTTP bridge for communication with the local Python daemon.
  - `M_HorrorFX.bas`: Sensory horror engine (screen tremors, eye blinking, pixel face rendering, thunder inversion, and blood-scab spreading).
  - `Sheet1_Archive.cls` and `ThisWorkbook.cls`: Worksheet event hooks for input interception and complete offline puzzle fallback mode.
- Ledger template generator (`scripts/build_ledger.py`) using openpyxl to generate `Midnight_Audit_1928_Template.xlsx` with custom 1928 Morbid Archive styling.
- Kiro specifications and steering guidelines under `.kiro/` (architecture, aesthetic autopsy, cosmic persona, MCP contract, puzzle engine spec).
- Initial test suite for puzzle state transitions, server endpoints, and MCP tool interactions.
