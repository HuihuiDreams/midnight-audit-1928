# Design — The Midnight Audit (1928)

> Implements [`requirements.md`](requirements.md). Architecture rules: [`../../steering/architecture.md`](../../steering/architecture.md). Visual rules: [`../../steering/aesthetic_autopsy.md`](../../steering/aesthetic_autopsy.md).

## 1. Three-Tier "Frankenstein" Architecture

```text
┌──────────────────────────────┐   HTTP JSON (127.0.0.1:8000)   ┌──────────────────────────────┐
│ Excel 1990s Client (.xlsm)   │ ─────────────────────────────▶ │ Local Python Daemon (FastAPI)│
│ src/vba/*.bas, *.cls         │ ◀───────── actions[] ───────── │ src/backend/server.py        │
│ Offline: HandleOfflineEvent  │                                └──────────────┬───────────────┘
└──────────────────────────────┘                                               │ shared file
                                                                  game_state.json (+ .lock)
┌──────────────────────────────┐   JSON-RPC 2.0 over stdio                     │
│ Kiro Agent (The Auditor)     │ ─────────────────────────────▶ ┌──────────────┴───────────────┐
│ .kiro/settings/mcp.json      │ ◀────────── tool results ───── │ MCP Server midnight-audit-mcp│
└──────────────────────────────┘                                │ src/backend/mcp_server.py    │
                                                                └──────────────────────────────┘
```

| Tier | Component | Responsibility |
| :--- | :--- | :--- |
| Client | `ThisWorkbook.cls` | `Workbook_Open` strips the UI and binds `Ctrl+Shift+R`; `Workbook_BeforeClose` restores it and cancels `OnTime` timers. |
| Client | `Sheet1_Archive.cls` | `Worksheet_Change` / `Worksheet_SelectionChange` forward edits and button clicks to `PostEvent`. |
| Client | `M_DaemonBridge.bas` | Transport (`MSXML2.ServerXMLHTTP.6.0` on Windows, `curl` via `MacScript` on macOS), pure-VBA JSON parser, action dispatcher, `HandleOfflineEvent`. |
| Client | `M_HorrorFX.bas` | `ThudBeep`, `ScreenTremor`, `ThunderInvert`, `SpreadBloodScab`, `RenderPixelFace`, eye blink timers, ambient whispers. |
| Daemon | `server.py` | `/api/status`, `/api/event`, `/api/pixel_radar`, `/api/haunt`, `/api/banish`, `/api/reset`; origin check and security headers. Port from `SERVER_PORT` (default 8000). |
| Engine | `puzzle_state.py` | `PuzzleEngine` state machine (`PhaseEnum`), ledger data, radar matrix, ritual judgement, haunt queue. |
| Agent | `mcp_server.py` | Tools `inspect_ledger`, `haunt_spreadsheet`, `judge_ritual`; stdio loop with a 64 KB line cap. |
| Build | `scripts/build_ledger.py` | Offline `openpyxl` generation of `Midnight_Audit_1928_Template.xlsx`. Never touches a live workbook. |

The Daemon and the MCP Server are separate processes. They share no memory; `game_state.json` is the only channel between them.

## 2. `game_state.json` File-Locked Persistence

- **Location**: `GAME_STATE_FILE` env var, defaulting to the project root. Tests redirect it to `tmp_path` in `tests/conftest.py`.
- **Lock**: `file_lock()` takes an exclusive lock on `<state>.lock` (created `0o600`) using `fcntl.flock` on Unix or `msvcrt.locking` on Windows. The lock is re-entrant per thread through a depth counter, so `queue_haunt` can hold it across `load_state` → mutate → `save_state`.
- **Atomic writes**: `save_state` writes to a `NamedTemporaryFile` in the same directory, then calls `os.replace`. Readers never observe a partial file.
- **Read-modify-write**: every mutating call (`handle_cell_change`, `handle_reagent_spray`, `judge_ritual`, `queue_haunt`, `pop_pending_effects`) reloads state under the lock first, so a haunt queued by Kiro is visible to the next VBA `/api/status` poll.
- **Bounds**: `pending_effects` is capped at 50 (oldest dropped); haunt messages are truncated to 2000 characters.
- **Serialised fields**: `to_dict()` / `from_dict()` cover phase, `row13_awakened`, `intruder_revealed`, `archive_sealed`, `ledger_data`, and `pending_effects`.

## 3. Phase State Machine

```text
THE_AUDIT_DISCREPANCY ──H7 = 7.00──▶ THE_UNSEEN_INTRUDER ──reagent_spray──▶ HIJACKED_CIPHER
        ▲                                                                       │
        │ /api/reset                                          B18 = SEAL THE DEEP VAULT
        │                                                                       ▼
  ARCHIVE SEALED ◀──────── /api/banish | judge_ritual | [SEAL ARCHIVE] ── MIDNIGHT_SETTLEMENT
```

Wrong inputs never regress a phase. They return blood-scab and thud actions only.

## 4. 30×30 Radar Coordinates (`K20:AN49`)

| Property | Value |
| :--- | :--- |
| Origin | `K20` (column 11, row 20) |
| Extent | `AN49` (column 40, row 49) |
| Size | 30 columns × 30 rows |
| Cell geometry | row height 12 pt, column width 2.2 (1:1) |
| Matrix index → cell | `grid[r][c]` → column `11 + c`, row `20 + r` |
| Eye / Abyss Core | `W34:X35` → `grid[14..15][12..13]`, blinking cells `W34`, `X34`, `W35`, `X35` |
| Pre-spray state | ghostly skull watermark with glitch tokens (`#ROT!`, `#REF!`, `???`) on perimeter margins only |
| Reveal | `/api/pixel_radar` returns `{rows: 30, cols: 30, start_cell: "K20", end_cell: "AN49", grid, blinking_cells}`; offline, `RenderPixelFace` paints the same matrix |
| Footer plaque | `K50:AN50` `🕯 ANNEX SUB-VAULT 13 SANCTUM \| EPICENTER W34:X35` |

Radar palette: Bone Paper `#D3CEB9`, Carbon `#181614`, Dried Blood `#2E0F0D`, Phosphor Green `#3B533E`, Decaying Paper `#C5BFA8`.

## 5. Kiro Integration

- **MCP registration**: `.kiro/settings/mcp.json` runs `uv run --with-requirements requirements.txt python -m src.backend.mcp_server` from the workspace root, with `autoApprove` set for all three tools. Every workspace must have `uv` on `PATH`.
- **Persona**: `.kiro/steering/cosmic_entity_persona.md` defines the Auditor's voice for haunt messages.
- **Verification hook**: `.kiro/hooks/verify-backend-and-ledger.json` runs `uv run --with-requirements requirements.txt python -m pytest -q` on save of `src/backend/*.py` or `scripts/build_ledger.py`, then regenerates the template if the suite passes. Every workspace must have `uv` on `PATH`.
