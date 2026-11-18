# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Midnight Clock & Late Interest (`M_HorrorFX.bas`, `M_DaemonBridge.bas`, `ThisWorkbook.cls`, `M_Bootstrap.bas`)**: The night now runs out. `StartMidnightClock` (on open) starts at `11:47 PM`, and `MidnightClockTick` advances one in-game minute every 20 s until the midnight stroke 13 minutes later (4 min 20 s untouched). Every rejected fee or cipher calls `ChargeLateInterest` (one more minute, noted on the status bar), in both daemon and offline mode. The live time appears in the `G1` masthead, at the front of every phase status line, and in the ambient whispers, which no longer carry fixed `11:49`–`11:55 PM` stamps. The clock is cancelled on seal, `EmergencyReset` and close. Ward's note (`K4:AN12`) gains the line *"Each wrong entry costs a minute. Seal it before midnight."*
- **Widening Abyss (`M_HorrorFX.bas`)**: Row 13 grows 14 pt per elapsed minute (220 to 402 pt) and closes back to 220 pt when the archive is sealed. In the last 3 minutes the `G1:I1` stamp bleeds and the abyss flashes on every tick.
- **Midnight Foreclosure Ending (`M_HorrorFX.bas`, `M_DaemonBridge.bas`)**: If midnight strikes before the seal, `ForecloseLedger` freezes the ledger, writes `MIDNIGHT. THE AUDITOR IS NOW THE AUDITED.` into Row 13, stamps `[ FORECLOSED - OCTOBER 31, 1928 - 12:00 MIDNIGHT ]` / `NIGHT AUDITOR MISSING SINCE 12:00 MIDNIGHT` across `B10:H12`, updates `E18` and the status bar, and protects the sheet. The workbook is marked saved, so closing does not offer to keep the ruined ledger. Reopening restarts the clock.
- **Camera Moves (`M_HorrorFX.bas`)**: `CameraMove` eases this workbook's own window (zoom and scroll). Clearing Phase 1 dollies into Row 13 and back. The reagent reveal leans over the radar, then settles on a Phase 3 view that holds `B18`, the cipher strip and the eye.
- **Entity Gaze (`M_HorrorFX.bas`, `Sheet1_Archive.cls`)**: After the reveal, `TrackEntityGaze` moves the 2x2 pupil inside the iris `V33:Y36` toward every selected cell, and the blink follows the pupil.
- **Tests (`tests/test_midnight_dread.py`)**: Source checks for the clock lifecycle, late interest, abyss bounds, foreclosure, camera window scope and gaze geometry. The geometry check compares against `ENTITY_FACE_MATRIX`.
- **`LICENSE`**: The MIT license the README already declared (copyright holder: the git author `huihuidreams`, 2026).
- **Non-modal in-sheet onboarding & live Phase HUD (`src/vba/`, `scripts/build_ledger.py`)**:
  - Added `RefreshPhaseGuidance`, `CurrentPhaseStatusText`, `ShowLockedControlHint`, `ShowWrongEntryGuidance`, `ShowPhaseBlockedHint`, and `StripPlaceholderPrefix` in `src/vba/M_DaemonBridge.bas` (wired through `ThisWorkbook.cls`, `Sheet1_Archive.cls`, and `M_HorrorFX.bas`'s `ResetStatusBar`). The VBA modules stay pure ASCII (the HUD candle is built with `ChrW` in `WaxSealLabel`) because the VBE imports them with the ANSI code page; lit buttons use `#D3CEB9` text instead of pure white.
  - Opening the workbook now auto-scrolls to top-left and focuses `H7`, displays dynamic `1/4`–`4/4` mission guidance in `E18:I18` (`CUSTODIAL WAX SEAL`) and `Application.StatusBar`, and explains locked buttons/out-of-phase clicks instead of failing silently.

### Changed

- **Template affordances, anti-spoiler clues, and label-based references (`scripts/build_ledger.py`, `Midnight_Audit_1928_Template.xlsx`)**:
  - Added `H7` (`[ TYPE FEE ]`) and `B18` (`[ LOCKED ]` -> `[ TYPE PHRASE ]`) placeholders plus visually distinct dormant (`#181614`/`#8A8D8F`), lit (`#3B533E` for `[ SPRAY REAGENT ]`, `#8A1C14` for `[ SEAL ARCHIVE ]`, both with `#D3CEB9` text), and spent button styles on `K18:AN18` and `C18:D18`.
  - Replaced raw cell coordinates (`H7`/`B18`/`K20:AN49`) and `$7.00` answer spoilers across `K4:AN12`, `K13:AN16`, `I14` (`ANOMALY: BASEMENT RADAR ->`), and `B30:H48` with concise 1928 archival action clues; embedded `"SEAL PHRASE (ROT-3):  VHDO WKH GHHS YDXOW"` and `PLAIN (READ TOP)` / `CIPHER (FIND BELOW)` decoding rows directly in `B21:H28`.
  - Synchronized `.kiro/specs/midnight-audit/requirements.md`, `.kiro/specs/puzzle_engine_spec.md`, `.kiro/steering/aesthetic_autopsy.md`, `tests/test_build_ledger.py`, and `tests/test_fixes_verification.py`.

  - Removed the `Ctrl+Shift+R` / Excel-toolbar line from the `K13` Special Collections protocol card: a 1928 archive document must not mention Excel. The hint remains in the status bar.
- **Pre-formatted Fee Column (`scripts/build_ledger.py`, `M_DaemonBridge.bas`, `README.md`, `README_CN.md`)**: Cell `H7` now carries the `$#,##0.00` currency number format directly in the template and is enforced by VBA upon Phase 1 awakening, so users can enter plain numbers (`7` or `7.00`) without manually typing the currency symbol `$`.
- **Zero-Warning Dev Dependencies (`requirements-dev.txt`)**: Added `httpx2>=2.16.0` to eliminate Starlette's `StarletteDeprecationWarning` under Python 3.14.
- **Agent Ritual Reaches the Workbook (`mcp_server.py`, `server.py`, `puzzle_state.py`, `M_DaemonBridge.bas`)**: A successful `judge_ritual` (MCP) or `POST /api/banish` sealed only the backend, so the open workbook was never stamped or protected and rejected every entry until reopened. `judge_ritual(..., deliver_to_workbook=True)` now queues `THUNDER_STROBE`, `SCREEN_TREMOR` and `LOCK_SHEET` in the same save as the seal; `/api/pending` passes queued actions that carry a `command` through unchanged, and `PollPendingHaunts` runs any queued command, not only `TRIGGER_HAUNT`. The workbook's own seal (`/api/event`) is unchanged and does not lock twice.
- **Haunt Target Validation (`puzzle_state.py`, `M_DaemonBridge.bas`)**: `validate_haunt_target` (Python) and `IsValidCellAddress` (VBA) now share the same bounds: columns up to `XFD`, rows up to 1,048,576 (was 99,999 in Python and 65,536 in VBA), no leading zeros, and ranges of at most 900 cells. `cell_text` accepts a single cell only, so one message can no longer overwrite `A1:AN50`. An out-of-bounds address now falls back to the status bar instead of vanishing under `On Error Resume Next`.
- **`LOCK_SHEET` Carries No Dead Fields (`puzzle_state.py`, `mcp_contract.md`)**: Removed `color` and `stamp_range`; the workbook always stamps `B10:H12` in cold ash.
- **Screen Tremor Only Moves Excel (`M_HorrorFX.bas`)**: Windows shakes `Application.Hwnd` and only while Excel is the foreground window (it used to shake whatever window was in front). macOS no longer scrolls `ActiveWindow`; it flickers the ledger with `FlashKeroseneLamp`.
- **Tests Have One Isolation Point (`tests/conftest.py`)**: `GAME_STATE_FILE` is pointed at a temporary directory before the backend is imported, every test gets a fresh temporary save and fresh server and MCP engines, and the three copies of `_break_disk` are now the `break_disk` fixture. The `tests.test_*` patches that never took effect are gone.

### Fixed

- **Tests Deleted the Real Save (`tests/test_edge_cases.py`)**: Its autouse fixture removed the `GAME_STATE_FILE` bound at import time, which was the real `game_state.json`; the save hook runs the suite on every backend save. The fixture is gone and a test now guards against module-level bindings.
- **MCP Stdio Died on Non-ASCII Input (`mcp_server.py`)**: Under a non-UTF-8 locale (`PYTHONIOENCODING=ascii`, Windows code pages) a Chinese message raised `UnicodeDecodeError`, and the error handler then raised `UnboundLocalError` on `req`, ending the process. stdin and stdout are now UTF-8 and `req` is reset on every loop.
- **Corrupt Save Was Half Loaded (`puzzle_state.py`)**: `from_dict` assigned fields as it parsed, so a bad `attempts` value left the phase changed while `load_state()` returned `False`, and the next save wrote that mix back. It now parses first and assigns after, rejects a non-object file, and keeps a copy of an unreadable save as `game_state.json.corrupt` before the next save replaces it.
- **Empty Poll Wrote the Disk Every 3 Seconds (`puzzle_state.py`)**: `pop_pending_effects` saved even when nothing was queued. It now returns early. `GET /api/pending` also no longer loads the state twice.
- **Agent Seal Made While the Workbook Was Closed (`ThisWorkbook.cls`)**: On reopen, `SyncDaemonState` set `gArchiveSealed` before any poll ran, so the queued `LOCK_SHEET` was never executed and the sheet stayed unsealed and unprotected. `Workbook_Open` now polls once before the sync.
- **Bad Queue Entry Lost the Queue and Failed Events (`puzzle_state.py`)**: `pending_effects` was loaded unchecked, so `[{}]` made `GET /api/pending` and `/api/event` answer `500` (`KeyError`) after the queue had already been cleared and the phase saved. Loading now keeps only haunts with a known type and built actions with a `command`, and drops the rest without declaring the save corrupt.
- **Empty or Non-Object Save (`puzzle_state.py`)**: `[]` and `{}` loaded as success; they are now rejected like any other non-object file.
- **`game_state.json.corrupt` Was Rewritten Every Poll (`puzzle_state.py`)**: The copy is skipped when the same bytes are already kept.
- **Isolation Test Used the Real Save as a Sentinel (`tests/test_fixes_verification.py`)**: `test_issue6_save_file_isolation` failed whenever a real `game_state.json` existed and could leave a fake save behind. It now compares the real save's bytes before and after, and creates nothing.

### Security

- **`GET /api/pending` Needs `X-Audit-Client: 1` (`server.py`, `M_DaemonBridge.bas`)**: The endpoint drains the haunt queue, and a request without an `Origin` header (an `<img>` tag, another process) passed the origin check. Without the header it now answers `403` and leaves the queue alone; the VBA poller sends it on both the MSXML and the macOS `curl` transport.

## [1.3.1] - 2026-11-12

### Added

- **Haunt Polling (`GET /api/pending`, `M_DaemonBridge.bas`)**: Haunts queued with `haunt_spreadsheet` used to wait for the player's next edit or click. `GET /api/pending` now pops them as `TRIGGER_HAUNT` actions, and the workbook polls it every 3 seconds (`StartHauntPolling` / `StopHauntPolling` / `PollPendingHaunts`, started in `Workbook_Open`). Polling runs with `EnableEvents` off so a haunt written into `H7` or `B18` is never mistaken for a player attempt, ignores a silent or refusing daemon, and is cancelled by `Ctrl+Shift+R`, workbook close, and the archive seal.
- **Failed Attempt Counters (`attempts`)**: The engine counts rejected entries per input cell (`H7` wrong or non-numeric fee, `B18` wrong override code after the first-entry hijack; cleared cells and correct answers are not counted). `/api/status` returns them and `inspect_ledger` prints `Failed Attempts: H7=<n>, B18=<n>`, so the Agent can tell when the player is stuck. Saving the counter is best effort and never turns player feedback into an error.
- **Single Entity Face Definition (`ENTITY_FACE_MATRIX`, `scripts/sync_vba_radar.py`)**: The 30×30 face revealed by `[ SPRAY REAGENT ]` is now one ASCII matrix plus legend in `puzzle_state.py`. `get_pixel_radar` builds its grid from it (identical to the previous formula output in all 900 cells), and the script regenerates the marked block in `M_HorrorFX.bas` that `RenderPixelFace` paints offline. Tests fail if the VBA copy drifts. The reveal intentionally paints over the pre-spray candle-and-pumpkin sanctum.
- **`requirements-dev.txt`**: Test tooling (`pytest`, `httpx`) moved out of the runtime requirements; it includes `requirements.txt`.
- **Kiro MCP Server Registration (`.kiro/settings/mcp.json`)**: Registers `midnight-audit-mcp` to run `uv run --with-requirements requirements.txt python -m src.backend.mcp_server` from the workspace root, enabled, with `autoApprove` for `inspect_ledger`, `haunt_spreadsheet`, and `judge_ritual`.
- **Canonical Kiro Spec Folder (`.kiro/specs/midnight-audit/`)**: `requirements.md` (EARS requirements for the 4-phase loop, `A1:AN50` Morbid Archive UI, cross-platform VBA offline fallback, and MCP haunting bridge), `design.md` (3-tier architecture, file-locked `game_state.json` persistence, 30x30 radar coordinates), and `tasks.md` (implementation and release checklist). The existing `mcp_contract.md` and `puzzle_engine_spec.md` are unchanged.
- **Kiro Verification Hook (`.kiro/hooks/verify-backend-and-ledger.json`)**: When a file in `src/backend/*.py` or `scripts/build_ledger.py` is saved, runs `uv run --with-requirements requirements.txt python -m pytest -q` and, if the suite passes, regenerates `Midnight_Audit_1928_Template.xlsx`.
- **Kiro Integration Tests (`tests/test_kiro_integration.py`)**: Checks release version strings, the changelog release header, MCP settings, the verification hook, and the spec folder layout.
- **Bilingual VBA Setup, Playthrough, and uv Guide (`README.md`)**: Added detailed English and Chinese (`中文快速上手与 Excel 宏（VBA）导入指南`) instructions covering `.bas` module importing, `.cls` document class copy-pasting (skipping lines 1–9 class headers), `.xlsm` saving, 4-phase playthrough steps, `Ctrl + Shift + R` emergency reset, `uv` installation, and Kiro MCP verification.

### Changed

- **Runtime vs Dev Requirements**: `requirements.txt` now lists only `fastapi`, `uvicorn`, `openpyxl`, and `pydantic`, so the MCP server and daemon start lighter. The verification hook and README run `pytest` through `requirements-dev.txt`.
- **Ledger Dates Count to the Game Night (`scripts/build_ledger.py`)**: The overdue days were really counted to October 13, so Wilbur's 140 days did not reach the October 31 setting. Every visible record (`ARK-001`..`ARK-040`) keeps its overdue days and paid fees and moves its checkout and due dates 18 days later, which keeps each loan length; Wilbur's due date is now `1928-06-13` and his checkout `1928-05-03` (41-day loan). The $7.00 answer, the ledger records in `puzzle_state.py`, and Rule 1's ">100 days" test (only Wilbur qualifies) are unchanged. The three expunged rows keep their dates and recount their days: `ARK-066` 273 → 292, `ARK-067` 345 → 353, `ARK-068` 86320 → 86361. New tests check that every row's due date plus overdue days equals October 31, 1928, that fees are $0.05 per day, and that the sheet matches the engine's records.
- **Sealed Archive Is Protected (`M_DaemonBridge.bas`, `M_Bootstrap.bas`)**: The Phase 4 seal now calls `ws.Protect` (no password) in both daemon and offline modes, so the stamped archive cannot be edited. `EmergencyReset` (`Ctrl+Shift+R`, also run silently on close) lifts it.
- **Offline Phase 1 Matches the Daemon (`M_DaemonBridge.bas`)**: The offline path no longer overwrites `B14` with `COORDINATE DISCLOSED...`; it recolors `A14:I16` only, as the daemon path does, and the pre-printed `I14` shows the coordinate.
- **macOS Temp File Name (`M_DaemonBridge.bas`)**: `Randomize` is called before building the `/tmp/ma_payload_*.json` name; `Rnd` without it repeated the same sequence on every launch.
- **Release Version `1.3.1`**: Bumped MCP `serverInfo.version` (`src/backend/mcp_server.py`) and FastAPI daemon `version` (`src/backend/server.py`) from `1.3.0` to `1.3.1`.
- **Agent Guidelines Moved to Kiro Steering (`.kiro/steering/agent_guidelines.md`)**: Converted the root `AGENTS.md` into an always-included Kiro steering rule and removed `AGENTS.md`, so Kiro no longer loads the same guidelines twice. Relative links now resolve from `.kiro/steering/`, the architecture section points to `architecture.md` instead of repeating its diagram, delegation now refers to `invoke_sub_agent`, and the verification hook is mentioned in the TDD section. `README.md` and `README_CN.md` link to the new path.

### Fixed

- **Failed State Saves No Longer Report Success (`src/backend/puzzle_state.py`, `server.py`, `mcp_server.py`)**: `save_state` used to log a write error to stderr and return normally, so `/api/event` answered `200 accepted` for an advance that was never persisted and the next request reloaded the old phase. It now raises `StateSaveError` (after logging and removing the temp file). `handle_cell_change`, `handle_reagent_spray`, `judge_ritual`, `queue_haunt`, and `pop_pending_effects` restore the in-memory engine to its pre-call state when the save fails. The daemon answers `500` with `"Game state could not be saved; the entry was not applied."` (security headers still applied), `/api/reset` keeps the current game if the fresh state cannot be written, and MCP tools return `isError: true` instead of a JSON-RPC protocol error. Haunt delivery on `/api/event` stays best effort: if only the queue cannot be saved, the event result is still returned and the haunts remain queued. Rejected inputs (wrong fee, wrong cipher, wrong ritual phrase) no longer write the state file, so they keep working when the disk is read-only.
- **Deleting `game_state.json` Now Restarts the Game (`src/backend/puzzle_state.py`)**: `load_state` kept the in-memory phase when the file was missing, so a running daemon or MCP server ignored the deletion until restarted. A missing file now resets the engine to a new game.
- **Cleared Cells Are Not Wrong Answers (`puzzle_state.py`, `Sheet1_Archive.cls`)**: Pressing Delete in `H7` or `B18` used to send an empty value that was judged invalid (blood scab, thud) and, in Phase 3, consumed the typing hijack. `Worksheet_Change` no longer posts empty values, and `handle_cell_change` ignores them with no penalty effects.
- **Lamp Flicker No Longer Erases the Masthead (`M_HorrorFX.bas`)**: `FlashKeroseneLamp` repainted `A1:I5` bone paper without restoring, leaving the bone-on-carbon masthead `A2:I2` unreadable. It now saves and restores each cell's color, and `FlashKeroseneLamp` and `ThunderInvert` target the `Audit_Ledger_1928` sheet instead of `ActiveSheet`.
- **Eye Blink Timer Is Started Once (`M_HorrorFX.bas`)**: In daemon mode `RenderPixelFace` and the `START_EYE_BLINK` action both started the blink, leaving an orphaned `OnTime` chain that `StopEyeBlink` could not cancel (double blink rate, possible workbook reopen after close). `StartEyeBlink` now cancels the pending timer first.
- **Renamed `step` Variable in `ScreenTremor` (`M_HorrorFX.bas`)**: `Step` is a VBA keyword; the loop variable is now `shakeStep`.
- **Player Is Told When the Daemon Refuses an Entry (`M_DaemonBridge.bas`)**: A non-200 reply (for example the new `500` on save failure) used to be a silent no-op. The status bar now reads `THE LEDGER REFUSES THE ENTRY - NOTHING WAS RECORDED. TRY AGAIN.`; the client still does not fall back to offline mode.
- **MCP Argument Validation (`mcp_server.py`, `puzzle_state.py`)**: Non-object `arguments`, a non-string `target_range`, or a non-string haunt `target_cell` now return a tool error (`isError`) instead of `-32603`; a non-object `params` returns `-32602`. `inspect_ledger` no longer labels every row-18 target `Cell B18`; it describes the row-18 control bar.
- Removed the unused `PhaseEnum` import from `server.py`, and `test_build_ledger_generates_file` now writes to `tmp_path` instead of a working-directory-relative path.
- Corrected stale cell ranges in the agent guidelines to match `scripts/build_ledger.py` and `aesthetic_autopsy.md`: handover note `K4:AN12` (was `K4:U16`), night protocol card `K13:AN16` (was `W4:AN16`), cipher strip `B21:H28` (was `B20:H26`), Armitage memorandum `B30:H48` plus plaque `B50:H50` (was `B28:H49`).
- Corrected the conditional-compilation order in the agent guidelines to `#If Mac ... #ElseIf VBA7 ... #Else`, matching `architecture.md`.
- Standardized MCP and verification-hook execution on cross-platform `uv`, which resolves project dependencies without OS-specific `.venv` paths.
- Constrained the generated template to the canonical `A1:AN50` canvas and stabilized its workbook core metadata across equivalent builds.

## [1.3.0] - 2026-11-12

### Added

- **Yellow Handover Note Full 30-Column Layout & Handwritten Typography (`K4:AN12`, `Bradley Hand`)**:
  - Expanded Ward's sticky note across all 30 columns (`K4:AN12`, spanning Rows 4..12 at ~221pt height), eliminating artificial column AN/Row 12 drop-shadow gaps that cramped the text.
  - Tailored line lengths (<50 chars) and switched font to `Bradley Hand` (bold, 9.5pt), providing an authentic organic ink-pen handwriting aesthetic (replacing plain/flat sans fonts) and ensuring 100% of the header, Rules 1-3, and Ward's bottom warning (`🩸 WARNING: Never alter or inspect Row 13. — Former Auditor Ward (Missing since Oct 30, 11:59 PM)`) are fully visible without truncation.
- **Special Collections Night Protocol & Reagent Card (`K13:AN16`, `American Typewriter`)**:
  - Added a full 30-column wide diegetic document card spanning Rows 13..16 (~277pt height) in authentic typewriter font, naturally absorbing the 220pt Row 13 Abyss height.
  - Features Dr. Armitage's archive directive #1928-X, detailing Wilbur Whateley's delinquent Necronomicon custody lock ($7.00 penalty in H7), Ibn-Ghazi reagent atomizer spray instructions for radar grid `K20:AN49`, and midnight vault sealing rules.
- **Charred Cipher Key Strip Full Box Display (`B21:H28`)**:
  - Expanded the charred ROT-3 cipher strip from `B21:H25` (60pt) to `B21:H28` (8 rows × 12pt = 96pt), giving all 6 lines of `Courier New` monospace cipher text and the bottom box border `╚════════════════════════════════════════════════════════════════════════════╝` comfortable breathing room with zero clipping.
  - Shifted the charred ash dither to Row 29 and re-anchored Dr. Henry Armitage's Archival Memorandum to `B30:H48` (19 rows = 228pt), preserving symmetrical alignment with Row 50 plaques (`B50:H50` and `K50:AN50`).
- **Dr. Henry Armitage's Restricted Archival Memorandum (`B30:H48`) & Plaque (`B50:H50`)**:
  - Added a 19-row (`B30:H48`) typed archival memorandum in authentic 9pt `American Typewriter` monospace font, recording late-night incident logs (floorboard groaning beneath Row 13, former auditor Ward's disappearance, non-Euclidean beam warping) and 4-step shift instructions.
  - Anchored with double-red borders, a Row 49 charred ash dither, and an official restricted directive plaque at `B50:H50` (`📜 ARCHIVAL FOLIO #1928-31B | DR. H. ARMITAGE RESTRICTED DIRECTIVE | VAULT SEAL REQUIRED`).
- **Emergency Override Label Clean Wrapping (`A18`) & Column A Width**:
  - Widened Column A (width 21) and updated `A18` to `"EMERGENCY OVERRIDE\nCODE (PHASE 3):"` in `Copperplate` bold (8.5pt), completely eliminating text truncation against cell `B18`.
- **Radar Bottom Plaque Geometry & Text Display (`K50:AN50`)**:
  - Refined the footer plaque under the 30x30 micro-pixel canvas to `"🕯️ ANNEX SUB-VAULT 13 SANCTUM | EPICENTER W34:X35"` (49 characters) at 8pt `Copperplate` bold centered, completely eliminating text truncation across the 390pt cell width while maintaining strict symmetry with the left-wing directive plaque (`B50:H50`).
- **Holistic Layout Convergence & Boundary Enforcement (`A1:AN50`)**:
  - Grounded the layout strictly in 1928 Miskatonic University lore and enforced the global `A1:AN50` canvas boundary, embedding the 30x30 16-bit candlelit sanctum pixel art directly within `K20:AN49` and removing non-canon exterior blocks (`Rows 51..80` and `Columns AO..BC`).
- **1928 Archival Plaque & Table Header Typography (`Copperplate`)**:
  - Upgraded table column headers (`A5:I5`) and classification banner (`A1`) to `Copperplate` bold (9.5pt), reinforcing the vintage 1928 bank/library ledger aesthetic.
- **Tactile 3D Action Button Bevels & Seamless Composite Borders**:
  - Upgraded `[ SEAL ARCHIVE ]` (`C18:D18`) and `[ SPRAY REAGENT ]` (`K18:AN18`) with bone paper highlights (top/left) and carbon shadows (bottom/right), removing internal green dividing lines for seamless mechanical button feedback, and cleaned internal borders on the Custodial Wax Seal box (`E18:I18`).
- **Charred Ash Ordered Dithering (`Row 29` & `Row 49`)**:
  - Added dithered crumbling ash borders across columns B..H at Row 29 (directly beneath the Charred Cipher Key Strip) and Row 49 (beneath Dr. Armitage's Archival Memorandum), creating authentic deteriorating burnt paper edges.
- **Universal Agent Working Guidelines (`AGENTS.md`)**: Established standardized repository development and collaboration guidelines for all AI agents and human contributors:
  - Architectural retrospective and design principles: strict adherence to the original Miskatonic University 1928 story lore and rejection of narrative drift (e.g., coroner autopsy reports or unrelated clip-art).
  - Holistic UI design principles: strict `A1:AN50` canvas boundary alignment, zero irregular protruding blocks, natural absorption of the 220pt Row 13 Abyss, and dedicated 30x30 1:1 micro-pixel canvas (`K20:AN49`).
  - Strict compliance with Karpathy Guidelines (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution).
  - Test-Driven Development (TDD) protocol requiring test synchronization and 100% pytest pass rate.
  - Mandatory changelog and specification synchronization procedures.

### Changed

- **Release Version `1.3.0`**: Bumped MCP `serverInfo.version` (`src/backend/mcp_server.py`) and FastAPI daemon `version` (`src/backend/server.py`) from `1.2.1` to `1.3.0`.
- **Annex Basement Radar De-Cluttering & Silhouette Clarity (`K20:AN49`)**:
  - Removed text error noise (`#ROT!`, `#REF!`, `[VOID]`, etc.) from the entity face and skull interior cells so the pixel-art geometry is crisp and unobstructed. Retained glitch tokens exclusively on perimeter scanning margins, while rendering solid dried-blood ram horns and revealing the central Cosmic Eye / Abyss Core at `W34:X35`.
- **Corrupted Radar Ghostly Watermark & Concentric Dither (`K20:AN49`)**:
  - Rendered a faint, ghostly 30x30 horned demonic skull and cosmic eye silhouette beneath the glitch tokens in the pre-spray state using organic blood and decaying paper fills, matching the revealed occult anatomy.
- **Compact Ledger Column Widths & Viewport Fit (`A1:AN50`)**:
  - Tightened ledger columns A..I to 156 total units and set `zoomScale = 85` so the entire sheet, including the 30x30 radar and right-wing dossier wing, fits 100% inside the visible display without right-edge clipping.
- **Spray Reagent Full-Width Action Bar**:
  - Expanded `[ SPRAY REAGENT ]` button (`K18:AN18`) and radar header (`K19:AN19`) to match the 30x30 radar grid geometry, updating click interception across `K18:AN18` in `Sheet1_Archive.cls`.
- **Text Overflow in Censored Cell `I14`**:
  - Added `wrap_text=True` and `shrink_to_fit=True` to prevent text from leaking across column J into the yellow handover note.
- **A18 Label Background & Text Truncation**:
  - Styled A18 with Decaying Paper fill (`#C5BFA8`) and Hospital Green thin border; widened Column A to 21 and enabled 2-line word wrapping at 28pt height to eliminate text truncation behind cell B18.
- **Letterhead Banner Paper Fill**:
  - Added Bone Paper (`#D3CEB9`) background fill and hairline borders to title banners `A2:I2` and `A3:I3`, eliminating raw unstyled white patches.
- **Row 18 Control Bar Completion**:
  - Set `D18` button background fill and styled trailing cells `E18:I18` with Bone Paper fill and thin borders, closing off the bottom table perimeter.
- **Phase 4 Cold Ash Stamp Text Collisions**:
  - Cleared range `B10:H12` (`.Value = Empty`) before applying Cold Ash banishment stamp in `M_DaemonBridge.bas`, preventing visual collisions with existing borrower entries.

### Removed

- **Non-Canon Relic Galleries & External Canvas Extensions (`Rows 51..80`, `Columns AO..BC`)**:
  - Scrapped the experimental 16-bit relic gallery (Option B) below the radar and extraneous column margins to strictly enforce the unified `A1:AN50` canvas boundary and 1:1 square micro-grid geometry.
- **Detached Altar Triptych & Halloween Pumpkin Clip-Art (`W4:AN12`, `AJ4:AN12`)**:
  - Removed detached pixel-art sprites (including standalone Halloween pumpkin lamps and separate candle/skull icons) that overcrowded the top-right wing; replaced with authentic 1928 university archival documents (the 30-column Yellow Handover Note `K4:AN12` and Special Collections Protocol Card `K13:AN16`).
- **External Police Autopsy Dossier (`B28:H48`)**:
  - Removed the non-diegetic coroner autopsy log, returning focus to the core 1928 Miskatonic University Library lore with Dr. Henry Armitage's restricted archival memorandum (`B30:H48`).

## [1.2.1]

### Security

- **Security Headers & Cross-Origin Protection**: Added `SecurityHeadersAndOriginMiddleware` configuring `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy: default-src 'none'`, and `Referrer-Policy: no-referrer`, while strictly validating `Origin` hostnames (`localhost`, `127.0.0.1`, `::1`) via `urlparse` to prevent substring bypasses (`localhost.evil.com`).
- **Input Validation & DoS Protection**: Enforced strict validation and length bounds across API request models (`EventRequest`, `HauntRequest`, `BanishRequest`, including size bounds validator on `EventRequest.value`), capped `pending_effects` queue to prevent unbounded disk/memory growth, and limited ritual phrase normalization buffers.
- **Strict Haunt Type Enforcement**: Gated `queue_haunt` and `/api/haunt` to strictly accept only recognized haunt types (`cell_text`, `flicker_lamp`, `thunder_invert`, `ink_spread`, `whisper`, `screen_tremor`), returning 400 Bad Request on unrecognized payloads.
- **Lockfile Permission Hardening**: Restricted file permissions on `game_state.json.lock` from `0o666` to `0o600` (owner read/write only).
- **VBA Transport Symlink Mitigation**: Used unique randomized temporary filenames (`/tmp/ma_payload_<time>_<rnd>.json`) on macOS to mitigate sticky `/tmp` symlink attacks.
- **Excel Injection & Coordinate Validation**: Hardened VBA action handlers (`SET_VALUE`, `HIJACK_TYPE`, `SPREAD_BLOOD_SCAB`) to validate cell coordinates via `IsValidCellAddress`, and centralized formula prefix neutralization into `NeutralizeFormulaPrefix` handling prefixes (`=`, `+`, `-`, `@`) even when preceded by whitespace.

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
