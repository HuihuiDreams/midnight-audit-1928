# Specification: Puzzle Engine & State Machine

## 1. Overview & 4-Phase Game Loop

*The Midnight Audit (1928)* is structured as a self-contained 4-phase puzzle loop designed to be completed in 3 to 5 minutes by any player without prior Lovecraftian lore knowledge. All clues are self-contained within the spreadsheet's "Handover Note" (Yellow Post-It) and column structures.

```text
[Phase 1: The Audit Discrepancy]
  - Calculate overdue late fee (Days > 100 * $0.05)
  - Unlocks Row 13 Tremor & Censored Borrower Records
               │
               ▼
[Phase 2: The Unseen Intruder (30x30 Grid)]
  - Click "Spray Developer" Reagent button on corrupted floorplan
  - Renders 30x30 Eldritch Entity Pixel Face + Blinking Eye
               │
               ▼
[Phase 3: Hijacked Typing & Cipher]
  - Decode ROT-3 4-word sealing cipher ("SEAL THE DEEP VAULT")
  - Entity briefly hijacks typing ("YOUR SALARY CANNOT SAVE YOU")
               │
               ▼
[Phase 4: Midnight Settlement]
  - Submit banishment seal to `/api/banish` or click [SEAL ARCHIVE]
  - Thunder strobe inversion + Screen tremor
  - Final Cold Ash Stamp: `[ ARCHIVE SEALED - 00:01 AM ]`
```

---

## 2. Phase Detailed Specifications

### Phase 1: Overdue Ledger Audit (The Audit Discrepancy)
- **Starting State**:
  - Ledger contains rows 6 to 12 of borrowing records.
  - Row 7: Record `ARK-007`, Borrower: `Wilbur Whateley`, Tome: `Necronomicon (Dee Trans.)`, Due Date: `1928-05-26`, Overdue Days: `140`.
  - Column H ("Late Fee Paid ($)") is blank for Row 7. Status in Column I is `"FLAGGED"`.
- **Player Action**:
  - Yellow Handover Note Rule 1: *"For records overdue > 100 days, calculate late fee ($0.05 per overdue day) in Column H to balance delinquent ledger."*
  - Correct input in cell `H7`: `140 * 0.05 = 7.00` (accepts `7`, `7.0`, `7.00`, `$7.00`).
- **Triggered Effect**:
  - Cell `I7` changes to `"BALANCED (UNHOLY)"`.
  - **The Row 13 Abyss awakens**: Row 13 (A13:I13) shakes; text appears in red/bone font: `"STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"`.
  - Censored Rows 14-16 are unlocked: moving selection over Rows 14-16 inverts background `#000000` to `#D3CEB9` revealing the hidden borrower coordinates: `"ARCHIVE COORDINATE: RADAR GRID K20:AN49"`.
  - System advances to Phase 2.

### Phase 2: The Unseen Intruder (30x30 Radar Grid)
- **Starting State**:
  - Grid region `K20:AN49` (30 columns by 30 rows) represents the Annex Basement Floorplan.
  - Cells are filled with glitch data (`#REF!`, `#ROT!`, `???`).
  - Handover Note Rule 2: *"If Annex Basement plan exhibits spatial corruption (#ROT!), spray chemical developer [BUTTON: SPRAY REAGENT] to reveal floorplan anomalies."*
- **Player Action**:
  - Player clicks `SPRAY REAGENT` button or runs `ApplyReagentDeveloper` macro (or daemon event).
- **Triggered Effect**:
  - A 30x30 matrix of pixel colors is written to `K20:AN49` row by row with a 15ms stagger.
  - Pixel values map to an Eldritch Eye/Demon Face using palette colors:
    - Background: `#D3CEB9` (Bone Paper)
    - Outline / Shadows: `#181614` (Carbon)
    - Pupil / Void: `#2E0F0D` (Dried Blood)
    - Iris: `#3B533E` (Phosphor Green)
  - Eye center cells (`W34:X35`) start a background timer blinking between `#3B533E` and `#2E0F0D` every 1.5 seconds.
  - Subtitle pops up: *"SOMETHING LURKS IN THE DEEP VAULT"*.
  - System advances to Phase 3.

### Phase 3: Hijacked Typing & Cipher (The Possession)
- **Starting State**:
  - Handover Note Rule 3: *"Emergency Vault Override requires transcribing the sealed 4-word phrase into Cell B18. Warning: cipher strip is shifted by 3 positions."*
  - Cipher Strip printed in cells:
    - Encrypted: `VHDO WKH GHHS YDXOW`
    - ROT-3 Key: `A->X, B->Y, C->Z, D->A...`
    - Plaintext: `SEAL THE DEEP VAULT`
- **Player Action**:
  - Player begins typing into cell `B18` (`Override Code`).
- **Triggered Effect**:
  - On the first input attempt or partial input, the Entity temporarily hijacks the cell value, replacing it for 1.2 seconds with:
    `"YOUR SALARY CANNOT SAVE YOU"`
    accompanied by a low-frequency rumble.
  - Cell then clears, allowing the player to enter the true code: `SEAL THE DEEP VAULT` (case-insensitive, trims whitespace).
  - Once verified, button `[SEAL ARCHIVE]` lights up red (`#8A1C14`).
  - System advances to Phase 4.

### Phase 4: Midnight Settlement (The Banishment)
- **Player Action**:
  - Player clicks `[SEAL ARCHIVE]` or submits the ritual to the backend daemon endpoint `/api/banish`.
- **Triggered Effect**:
  - Thunder Strobe: 5 rapid flash cycles inverting sheet background between `#FFFFFF` and `#000000`.
  - Window tremor shakes the Excel interface for 600ms.
  - The entire sheet is locked into Cold Ash Gray (`#8A8D8F`).
  - Giant stamped banner placed across `B10:H12`:
    `========================================`
    `[ ARCHIVE SEALED - OCTOBER 14, 1928 - 00:01 AM ]`
    `ALL BALANCES CANCELLED BY ORDER OF ARMITAGE`
    `========================================`
  - Game ends with complete victory.

---

## 3. Offline Fallback Logic

When the Python Daemon is not running:
1. `PostEvent` in `src/vba/M_DaemonBridge.bas` catches connection timeouts (`curl` or `MSXML2.ServerXMLHTTP` failure) via `On Error GoTo FallbackHandler`.
2. It immediately routes the event to `HandleOfflineEvent(eventType, cellCoord, cellVal, buttonName)` in `src/vba/M_DaemonBridge.bas`.
3. `HandleOfflineEvent` maintains `gLocalPhase` (1 to 4) and executes the exact phase rules and sensory feedback by invoking procedures in `src/vba/M_HorrorFX.bas`:
   - **Phase 1 (H7)**: Validates overdue fee `Abs(Val(cleanVal) - 7.00) < 0.01`. If valid, updates cell `I7` to `"BALANCED (UNHOLY)"`, awakens Row 13 (`"STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"`), reveals censored rows 14-16, triggers `ThudBeep` and `ScreenTremor`, and advances `gLocalPhase` to 2. If invalid, triggers `SpreadBloodScab` on `H7` and `ThudBeep`.
   - **Phase 2 (reagent_spray / SPRAY_REAGENT)**: Calls `RenderPixelFace(ws)` in `M_HorrorFX.bas` to paint the 30x30 floorplan (`K20:AN49`), starts eye blinking via `StartEyeBlink` / `ToggleEyeBlink`, triggers `ThudBeep`, and advances `gLocalPhase` to 3.
   - **Phase 3 (B18 Override Code)**: On initial interaction (`gHijackTriggered = False`), hijacks typing with `"YOUR SALARY CANNOT SAVE YOU"` in dried blood font, rumbles with `ThudBeep`, pauses 1.2s via `PlatformSleep`, and clears the cell. On subsequent input, checks `Trim(UCase(cellVal)) = "SEAL THE DEEP VAULT"`. If matched, arms the `[ SEAL ARCHIVE ]` button in `C18:D18` (`COLOR_WARNING_RED`) and advances `gLocalPhase` to 4. If invalid, triggers `SpreadBloodScab` on `B18` and `ThudBeep`.
   - **Phase 4 (banish / SEAL ARCHIVE)**: Calls `StopEyeBlink`, `ThunderInvert`, and `ScreenTremor` in `M_HorrorFX.bas`, paints the Cold Ash banishment stamp across `B10:H12` (`[ ARCHIVE SEALED - OCTOBER 14, 1928 - 00:01 AM ]`), and displays the termination notification.
Thus the `.xlsm` file remains 100% playable in standalone offline mode without any external Python daemon or dependencies.
