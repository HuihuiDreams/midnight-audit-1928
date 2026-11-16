# Requirements — The Midnight Audit (1928)

> Canonical Kiro spec. Detailed phase rules: [`../puzzle_engine_spec.md`](../puzzle_engine_spec.md). Wire contracts: [`../mcp_contract.md`](../mcp_contract.md).

## Introduction

The player is the night auditor of the Miskatonic University Annex Archive on **October 31, 1928 (All Hallows' Eve)**. They take over from former auditor Ward, who vanished the night before, and reconcile the overdue borrowing ledger. The ledger is a sealing sigil: each balanced figure loosens the seal over the entity beneath the floorboards (Wilbur Whateley). The game is a 4-phase puzzle inside one Excel sheet, completable in 3 to 5 minutes with no prior Lovecraft knowledge.

## Glossary

- **Ledger**: The single archive worksheet, bounded by `A1:AN50`.
- **Daemon**: Local FastAPI bridge at `http://127.0.0.1:8000`.
- **MCP Server**: `midnight-audit-mcp`, JSON-RPC 2.0 over stdio.
- **Radar**: The 30×30 Annex Basement floorplan at `K20:AN49`.
- **Offline Mode**: VBA-only rule engine used when the Daemon is unreachable.

---

## Requirement 1 — Phase 1: The Audit Discrepancy

**User story:** As the night auditor, I want to settle the delinquent fee so that the ledger balances.

1. WHEN the player enters `7`, `7.0`, `7.00`, or `$7.00` in `H7` THE SYSTEM SHALL set `I7` to `BALANCED (UNHOLY)` and advance to Phase 2.
2. WHEN Phase 1 is cleared THE SYSTEM SHALL awaken Row 13 with `STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS`, unlock censored rows 14–16 revealing `ANOMALY: BASEMENT RADAR ->` in `I14`, illuminate `[ SPRAY REAGENT ]` (`K18:AN18`), and advance the live Phase HUD (`E18:I18` and `Application.StatusBar`) to Phase 2/4.
3. WHEN the player enters any other value in `H7` THE SYSTEM SHALL keep Phase 1, spread a dried-blood scab on `H7`, and play the taboo thud.
4. WHEN the player selects Row 13 THE SYSTEM SHALL play the taboo thud and flash the hidden glyph.

## Requirement 2 — Phase 2: The Unseen Intruder

**User story:** As the night auditor, I want to develop the corrupted floorplan so that I can see what lurks in the vault.

1. WHEN the player clicks `[ SPRAY REAGENT ]` (`K18:AN18`) in Phase 2 THE SYSTEM SHALL paint the 30×30 pixel matrix onto `K20:AN49` and advance to Phase 3.
2. WHILE the Radar is revealed THE SYSTEM SHALL blink the eye cells `W34`, `X34`, `W35`, `X35` between Phosphor Green `#3B533E` and Dried Blood `#2E0F0D` every 2 seconds.
3. WHEN the reagent is sprayed outside Phase 2 THE SYSTEM SHALL leave the phase unchanged.

## Requirement 3 — Phase 3: Hijacked Typing & Cipher

**User story:** As the night auditor, I want to decode the charred cipher strip so that I can arm the vault seal.

1. WHEN the player first types into `B18` in Phase 3 THE SYSTEM SHALL replace the value with `YOUR SALARY CANNOT SAVE YOU` for 1.2 seconds, then clear the cell.
2. WHEN the player enters `SEAL THE DEEP VAULT` in `B18` (case-insensitive, whitespace-normalised) THE SYSTEM SHALL arm `[ SEAL ARCHIVE ]` (`C18:D18`) in Warning Red `#8A1C14` and advance to Phase 4.
3. WHEN the player enters any other phrase in `B18` THE SYSTEM SHALL keep Phase 3 and spread a dried-blood scab on `B18`.

## Requirement 4 — Phase 4: Midnight Settlement

**User story:** As the night auditor, I want to seal the archive so that the entity is banished before midnight.

1. WHEN the player clicks `[ SEAL ARCHIVE ]` or a valid phrase reaches `/api/banish` in Phase 4 THE SYSTEM SHALL run the 5-cycle thunder strobe and screen tremor, lock the sheet in Cold Ash `#8A8D8F`, and stamp `[ ARCHIVE SEALED - OCTOBER 31, 1928 - 00:01 AM ]` across `B10:H12`.
2. WHEN a banish request is empty, blank, or mismatched THE SYSTEM SHALL reject it with `MISMATCHED DEBIT. YOUR RITUAL VOID ACCRUES BLOOD DEBT.` and a taboo thud.
3. WHEN the archive is already sealed THE SYSTEM SHALL NOT replay the victory sequence.

## Requirement 5 — Morbid Archive UI (`A1:AN50`)

**User story:** As the player, I want a coherent 1928 archival document so that the horror stays diegetic.

1. THE SYSTEM SHALL confine every styled cell, document, and pixel to `A1:AN50`, with the left wing (`B50:H50`) and right wing (`K50:AN50`) ending flush on Row 50.
2. THE SYSTEM SHALL use only the Morbid Archive palette defined in `.kiro/steering/aesthetic_autopsy.md` and `src/backend/puzzle_state.py`.
3. THE SYSTEM SHALL render Row 13 at 220 pt with a `#000000` fill and initially invisible `#000000` glyph text.
4. THE SYSTEM SHALL render the Radar as 30 columns × 30 rows at row height 12 pt and column width 2.2 (1:1 square cells).
5. THE SYSTEM SHALL present only 1928 university archive artifacts: borrowing ledger, Ward's handover note (`K4:AN12`), protocol card (`K13:AN16`), ROT-3 cipher strip (`B21:H28`), Dr. Armitage's memorandum (`B30:H48`), and the Radar.
6. WHEN the workbook opens THE SYSTEM SHALL hide ribbons, formula bar, headings, and gridlines.
7. WHEN the workbook opens THE SYSTEM SHALL keep onboarding non-modal and in-sheet: auto-focus the Phase 1 target (`H7`), render explicit placeholders (`[ TYPE FEE ]`, `[ LOCKED ]`) and dormant button affordances (`C18:D18`, `K18:AN18`), show live 1/4–4/4 mission progress in `E18:I18` and `Application.StatusBar`, and present contextual status guidance on out-of-phase clicks or mistyped inputs without spoiling puzzle answers.

## Requirement 6 — Cross-Platform VBA & Offline Fallback

**User story:** As a player on Windows or macOS, I want the workbook to run with or without the Daemon.

1. WHEN a Daemon request fails or times out (500 ms connect on Windows, `curl -m 1` on macOS) THE SYSTEM SHALL route the event to `HandleOfflineEvent` and apply the same phase rules locally.
2. THE SYSTEM SHALL guard every Win32 API declaration with `#If Mac` / `#ElseIf VBA7` (PtrSafe, LongPtr) / `#Else` blocks.
3. WHILE running on macOS THE SYSTEM SHALL replace `Beep` and `MoveWindow` with AppleScript beeps and visual tremor fallbacks.
4. WHEN the workbook opens THE SYSTEM SHALL bind `Ctrl+Shift+R` to `EmergencyReset`, which restores the Excel UI and cancels `Application.OnTime` timers.
5. WHEN the workbook closes THE SYSTEM SHALL unbind the hotkey and cancel all pending timers.
6. THE SYSTEM SHALL NOT open or write the live `.xlsm` with `openpyxl`; `openpyxl` is restricted to `scripts/build_ledger.py`.

## Requirement 7 — MCP Haunting Bridge

**User story:** As the Kiro agent playing the Auditor, I want tools to watch and haunt the ledger.

1. WHEN Kiro calls `initialize` THE SYSTEM SHALL return `serverInfo` `{ "name": "midnight-audit-mcp", "version": "1.3.1" }`.
2. WHEN Kiro calls `inspect_ledger` THE SYSTEM SHALL return the current phase, ledger rows for `target_range` (cell, row, or range), and the anomaly dossier when `include_anomalies` is true.
3. WHEN Kiro calls `haunt_spreadsheet` with a recognised `haunt_type` THE SYSTEM SHALL queue the effect in `game_state.json` for the VBA client to pull via `/api/status`.
4. WHEN `haunt_spreadsheet` receives an unknown `haunt_type` or malformed `target_cell` THE SYSTEM SHALL reject it without queueing.
5. WHEN the pending effect queue holds 50 entries THE SYSTEM SHALL drop the oldest before appending.
6. WHEN Kiro calls `judge_ritual` THE SYSTEM SHALL apply the same verdict as `/api/banish`.
7. WHEN a JSON-RPC message has no `id` THE SYSTEM SHALL treat it as a notification and send no response.
8. WHEN a stdio request line exceeds 64 KB THE SYSTEM SHALL discard it and return a `-32700` parse error.
9. WHEN a Daemon request carries an `Origin` whose host is not `localhost`, `127.0.0.1`, or `::1` THE SYSTEM SHALL respond 403.
