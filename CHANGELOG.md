# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Yellow Handover Note Full 30-Column Layout & Handwritten Typography (`K4:AN12`, `Bradley Hand`)**:
  - Expanded Ward's sticky note across all 30 columns (`K4:AN12`, spanning Rows 4..12 at ~221pt height), eliminating the artificial column AN/Row 12 drop-shadow gaps that cramped the text.
  - Tailored line lengths (<50 chars) and switched font to `Bradley Hand` (bold, 9.5pt), providing an authentic organic ink-pen handwriting aesthetic (replacing plain/flat sans fonts) and ensuring 100% of the header, Rules 1-3, and Ward's bottom warning (`🩸 WARNING: Never alter or inspect Row 13. — Former Auditor Ward (Missing since Oct 30, 11:59 PM)`) are fully visible without truncation.
- **Charred Cipher Key Strip Full Box Display (`B21:H28`)**:
  - Expanded the charred ROT-3 cipher strip from `B21:H25` (60pt) to `B21:H28` (8 rows × 12pt = 96pt), giving all 6 lines of `Courier New` monospace cipher text and the bottom box border `╚════════════════════════════════════════════════════════════════════════════╝` comfortable breathing room with zero clipping.
  - Shifted the charred ash dither to Row 29 and re-anchored Dr. Henry Armitage's Archival Memorandum to `B30:H48` (19 rows = 228pt), preserving symmetrical alignment with Row 50 plaques (`B50:H50` and `K50:AN50`).
- **Emergency Override Label Clean Wrapping (`A18`) & Column A Width**:
  - Widened Column A from 16 to 19 and updated `A18` to `"EMERGENCY OVERRIDE\nCODE (PHASE 3):"` in `Copperplate` bold (8.5pt), completely eliminating text truncation against cell `B18`.
- **Radar Bottom Plaque Geometry & Text Display (`K50:AN50`)**:
  - Refined the footer plaque under the 30x30 micro-pixel canvas to `"🕯️ ANNEX SUB-VAULT 13 SANCTUM | EPICENTER W34:X35"` (49 characters) at 8pt `Copperplate` bold centered, completely eliminating text truncation across the 390pt cell width while maintaining strict symmetry with the left-wing directive plaque (`B50:H50`).
- **Holistic Layout Convergence & Boundary Enforcement (`A1:AN50`)**:
  - Grounded the layout strictly in 1928 Miskatonic University lore and enforced the global `A1:AN50` canvas boundary, embedding the 30x30 16-bit candlelit sanctum pixel art directly within `K20:AN49` and removing non-canon exterior blocks (`Rows 51..80` and `Columns AO..BC`).
- **1928 Archival Plaque & Table Header Typography (`Copperplate`)**:
  - Upgraded table column headers (`A5:I5`) and classification banner (`A1`) to `Copperplate` bold (9.5pt), reinforcing the vintage 1928 bank/library ledger aesthetic.
- **Universal Agent Working Guidelines (`AGENTS.md`)**: Established standardized repository development and collaboration guidelines for all AI agents and human contributors:
  - Architectural retrospective and design principles: strict adherence to the original Miskatonic University 1928 story lore and rejection of narrative drift (e.g., coroner autopsy reports or unrelated clip-art).
  - Holistic UI design principles: strict `A1:AN50` canvas boundary alignment, zero irregular protruding blocks, natural absorption of the 220pt Row 13 Abyss, and dedicated 30x30 1:1 micro-pixel canvas (`K20:AN49`).
  - Strict compliance with Karpathy Guidelines (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution).
  - Test-Driven Development (TDD) protocol requiring test synchronization and 100% pytest pass rate.
  - Mandatory changelog and specification synchronization procedures.
- **16-Bit High-Density Micro-Pixel Art Sanctum (Option B: `K51:BC80`)**: Built a dedicated 16-bit fine micro-grid occult relic gallery on an unconstrained canvas below the radar (`Rows 51..80`, `Columns K..BC`) with uniform 12pt row heights and 2.2 column widths (~16px x 16px 1:1 square micro-pixels):
  1. *16-Bit Sanatorium Kerosene Candle* (`K52:V79`, 12x28): Elaborate tallow dripping down a fluted candle body, brass saucer with sculpted finger loop, and glowing layered phosphor green/gold flame core.
  2. *16-Bit Occult Horned Cranium* (`X52:AK79`, 14x28): Anatomical human skull with curved ram horns, zygomatic arches, nasal aperture void, dual glowing phosphor pupils (`AA63`, `AH63`), ivory teeth, and mental protuberance.
  3. *16-Bit Halloween Jack-o'-Lantern* (`AM52:AZ79`, 14x28): Ribbed pumpkin rind with twisted woody vine stem, glowing triangular candlelight eyes (`AP62`, `AW62`), carved nose cavity, and multi-tier jagged saw-tooth grin blazing with internal candlefire.
  4. *Occult Relic Plaques (`K51:BC51`, `K80:BC80`)*: Header and footer forensic catalog banners with solid Carbon Desk borders.
- **True Square-Pixel Occult Altar Triptych (`W4:AN12`)**: Replaced non-square stretched sprites with handcrafted 1:1 true square pixel art sprites on square-width columns (`width = 3.5`):
  1. *1928 Sanatorium Kerosene Candle* (`W4:AA12`): 5x9 pixel art featuring dripping bone wax, brass saucer with finger loop handle, and glowing phosphor green flame core.
  2. *Occult Memento Mori Skull* (`AC4:AH12`): 6x9 pixel art with cranium dome, suture crack, deep eye socket void, glowing green phosphor pupils (`AE8`, `AF8`), maxilla, and grinning teeth.
  3. *Halloween Jack-o'-Lantern Pumpkin* (`AJ4:AN12`): 5x9 pixel art with withered stem, triangular carved glowing eyes (`AK7`), jagged saw-tooth mouth, and vibrant pumpkin orange rind (`#D9681A` at `AL11`).
  4. *Occult Altar Header & Evidence Dossier Card* (`W3:AN16`): Added an engraved brass altar plaque at `W3:AN3` and an authentic Arkham Police & Sanatorium Incident Evidence Box in `W13:AN16` utilizing the 220pt Row 13 height for readable forensic evidence cards.
- **Arkham Coroner Autopsy Dossier (`B28:H48`)**: Replaced the 8:1 horizontally stretched smears below the cipher key with a richly detailed, typed 1928 coroner autopsy log and custodial directive bounded by double-red rules, dithered ash, and an official evidence plaque (`B50:H50`).
- **50% Bayer Ordered Dithering**: Softened physical drop shadows on the yellow handover note (`V5:V17`, `L17:V17`) with a 2x2 Bayer checkerboard dither pattern and dog-eared corner chamfer.
- **Charred Ash Crumbling Edge (`B26:H26`, `B49:H49`)**: Added dithered crumbling ash and dog-eared paper curl beneath the Charred Cipher Key Strip and Autopsy Dossier artifacts.
- **Tactile 3D Action Button Bevels & Seamless Composite Borders**: Upgraded `[ SEAL ARCHIVE ]` (`C18:D18`) and `[ SPRAY REAGENT ]` (`K18:AN18`) with bone paper highlights (top/left) and carbon shadows (bottom/right), removing internal green dividing lines for seamless mechanical button feedback, and cleaned internal borders on the Custodial Wax Seal box (`E18:I18`).
- **Concentric Radar Dither Anomaly (`K20:AN49`)**: Implemented ordered dithering gradient across pre-spray corrupted radar cells, transitioning from deep dried blood scab to decaying paper.

### Changed

- **Annex Basement Radar De-Cluttering & Silhouette Clarity (`K20:AN49`)**: Removed text error noise (`#ROT!`, `#REF!`, `[VOID]`, etc.) from the entity face and skull interior cells so the pixel-art geometry is crisp and unobstructed. Retained glitch tokens exclusively on perimeter scanning margins, while rendering solid dried-blood ram horns and revealing the central Cosmic Eye / Abyss Core at `W34:X35`.
- **Compact Ledger Column Widths & Viewport Fit (`A1:AN50`)**: Tightened ledger columns A..I to 156 total units and set `zoomScale = 85` so the entire sheet, including the 30x30 radar and occult altar sprites, fits 100% inside the visible display without right-edge clipping.
- **Handover Note Proportioned Memo Card (`K4:U16`)**: Rebalanced Post-It note to 11 columns (`K4:U16`) with structured typographic dividers and 9pt font, leaving columns `W..AN` open for the square-pixel altar triptych.
- **Spray Reagent Full-Width Action Bar**: Expanded `[ SPRAY REAGENT ]` button (`K18:AN18`) and radar header (`K19:AN19`) to match the 30x30 radar grid geometry, updating click interception across `K18:AN18` in `Sheet1_Archive.cls`.

- **Pumpkin Sprite Containment & Vertical Symmetry (`AJ4:AN12`)**: Corrected `SPRITE_PUMPKIN` rows 10 and 11 from 6 columns to strict 5-column symmetric matrices (`"oEEEo"` and `".oOo."`), eliminating horizontal spill into margin column AO and centering the jack-o'-lantern on Column AL.
- **Corrupted Radar Ghostly Watermark (`K20:AN49`)**: Rendered a faint, ghostly 30x30 horned demonic skull and cosmic eye silhouette beneath the glitch tokens in the pre-spray state using organic blood and decaying paper fills, matching the revealed occult anatomy.
- **Text Overflow in Censored Cell `I14`**: Added `wrap_text=True` and `shrink_to_fit=True` to prevent text from leaking across column J into the yellow handover note.
- **A18 Label Background & Text Truncation**: Styled A18 with Decaying Paper fill (`#C5BFA8`) and Hospital Green thin border; widened Column A to 20 and enabled 2-line word wrapping at 28pt height to eliminate text truncation behind cell B18.
- **Letterhead Banner Paper Fill**: Added Bone Paper (`#D3CEB9`) background fill and hairline borders to title banners `A2:I2` and `A3:I3`, eliminating raw unstyled white patches.
- **Row 18 Control Bar Completion**: Set `D18` button background fill and styled trailing cells `E18:I18` with Bone Paper fill and thin borders, closing off the bottom table perimeter.
- **Phase 4 Cold Ash Stamp Text Collisions**: Cleared range `B10:H12` (`.Value = Empty`) before applying Cold Ash banishment stamp in `M_DaemonBridge.bas`, preventing visual collisions with existing borrower entries.

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
