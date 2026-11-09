# The Midnight Audit (1928)

> *"Inspired by H.P. Lovecraft's The Dunwich Horror (1928)"*

[![Kiroween 2026 Hackathon](https://img.shields.io/badge/Kiroween_2026-Frankenstein_Track-8A1C14.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-454F48.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Excel VBA](https://img.shields.io/badge/Client-Excel_VBA_1990s-D3CEB9.svg)](#)

---

## 📖 Introduction & The "Frankenstein" Concept

**The Midnight Audit (1928)** is an unholy heterogeneous stitch of technologies across four decades:
- **Client (1990s)**: A decaying Microsoft Excel VBA workbook masquerading as the Miskatonic University Annex Archive delinquency ledger.
- **Local Daemon (2026)**: A modern Python FastAPI microservice maintaining state synchronization and event buffering.
- **Agentic Brain (2026)**: A Kiro IDE Agent integrated via Model Context Protocol (MCP) that monitors auditor keystrokes and haunts the spreadsheet in real time.

### 🩸 Zero-Barrier Principle (3–5 Minute Playthrough)
No prior knowledge of the Cthulhu Mythos is required. The experience is framed 100% within the mundane task of late-night bookkeeping. All clues are self-contained within the in-spreadsheet yellow "Handover Note".

---

## 🕹️ Quickstart & Playthrough Guide

### Step 1: Clone & Setup Local Backend (Optional for Offline Play)
```bash
# Clone the repository
git clone https://github.com/example/the-midnight-audit-1928.git
cd "The Midnight Audit (1928)"

# Setup Python Virtual Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the Local Daemon Bridge
python3 -m src.backend.server
# (or: python3 src/backend/server.py)
```
*(The daemon will run on `http://127.0.0.1:8000` by default; custom port can be set via `SERVER_PORT`)*

### Step 2: Generate or Open the Ledger
```bash
# Generate the initial Morbid Archive template
python3 scripts/build_ledger.py
```

#### Importing VBA Modules into Excel (One-time Setup)
The generator builds the layout and data as `Midnight_Audit_1928_Template.xlsx`. To enable the full interactive horror simulation:
1. Open `Midnight_Audit_1928_Template.xlsx` in Microsoft Excel.
2. Open the Visual Basic Editor: press **`Alt + F11`** on Windows or **`Opt + F11`** on macOS (or *Tools > Macro > Visual Basic Editor*).
3. **Import Standard Modules (`.bas`)**:
   - In the menu, select **File > Import File...** (or right-click the VBA project tree).
   - Import the three `.bas` modules located in `src/vba/`:
     - `src/vba/M_Bootstrap.bas`
     - `src/vba/M_DaemonBridge.bas`
     - `src/vba/M_HorrorFX.bas`
4. **Wire Document Class Modules (`.cls`)**:
   - ⚠️ *Important*: `Sheet1_Archive.cls` and `ThisWorkbook.cls` are Excel document class modules. Importing them via *File > Import File* creates detached class modules that will not intercept worksheet/workbook events.
   - Open `src/vba/Sheet1_Archive.cls` in a text editor, copy its code, double-click **`Sheet1 (Audit_Ledger_1928)`** in the VBA Project window, and paste the code into the sheet's code pane.
   - Open `src/vba/ThisWorkbook.cls` in a text editor, copy its code, double-click **`ThisWorkbook`** in the VBA Project window, and paste the code into the workbook's code pane.
5. **Save as `.xlsm`**:
   - Go to **File > Save As...**, choose file format **Excel Macro-Enabled Workbook (.xlsm)**, and name it `Midnight_Audit_1928_Template.xlsm`.

### Step 3: Excel Security & Macro Settings
1. When prompted by Excel, click **"Enable Content"** or **"Enable Macros"**.
2. **Emergency Reset**: If at any point the stripped UI hides standard controls, press **`Ctrl + Shift + R`** to instantly restore standard Excel toolbars, ribbons, and formula bars.

### Step 4: Solve the 4-Phase Audit Loop
1. **Phase 1 (The Audit Discrepancy)**: Read Rule 1 on the Yellow Handover Note. Check borrower `Wilbur Whateley` in Row 7 (Overdue: 140 days). Type `$7.00` into `H7` (140 × $0.05). Watch Row 13 awaken.
2. **Phase 2 (The Unseen Intruder)**: Read Rule 2. On the 30x30 Annex Floorplan radar, click `[SPRAY REAGENT]` (or run developer macro). Watch the pixel face manifest and eyes blink.
3. **Phase 3 (The Hijacked Typing)**: Read Rule 3. Decode the ROT-3 cipher strip (`VHDO WKH GHHS YDXOW` -> `SEAL THE DEEP VAULT`). Attempt to type into Cell `B18` — observe the spectre temporarily hijack the cell with sinister warnings before entering the true phrase.
4. **Phase 4 (The Midnight Settlement)**: Click `[SEAL ARCHIVE]`. Thunder lightning flashes, screen shakes, and the ledger is permanently stamped closed at `00:01 AM`.

---

## 🏛️ System Architecture

```text
┌────────────────────────────────────────────────────────┐
│             Excel 1990s Client (.xlsm / VBA)           │
│  - Morbid Archive UI (Stripped menus, Courier New)    │
│  - Worksheet Event Hooks (Change, SelectionChange)     │
│  - Sensory FX (Cell spreading, eye blink, screen tremor)│
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP POST / Event Queue (JSON)
                           ▼
┌────────────────────────────────────────────────────────┐
│             Local Python Daemon (2026)                  │
│  - FastAPI Bridge (localhost:8000)                     │
│  - State Machine & Event Buffering (game_state.json)   │
│  - Dual-mode (Daemon Active vs Offline Fallback)       │
└──────────────────────────┬─────────────────────────────┘
                           │ JSON-RPC 2.0 (stdio / SSE)
                           ▼
┌────────────────────────────────────────────────────────┐
│             Kiro Agentic IDE (Agentic Mastermind)      │
│  - Model Context Protocol (MCP) Server                 │
│  - Tools: inspect_ledger, haunt_spreadsheet, judge... │
│  - Dynamic Haunting & Eldritch Personality Injection   │
└────────────────────────────────────────────────────────┘
```

---

## 🛡️ Kiro Specification System (`/.kiro`)

This project is built under strict compliance with Kiro agent steering and specification standards:
- [`.kiro/steering/architecture.md`](.kiro/steering/architecture.md): Cross-platform PtrSafe VBA rules and Windows file-lock avoidance.
- [`.kiro/steering/aesthetic_autopsy.md`](.kiro/steering/aesthetic_autopsy.md): "Morbid Archive" color palette, font rules, and Row 13 Abyss.
- [`.kiro/steering/cosmic_entity_persona.md`](.kiro/steering/cosmic_entity_persona.md): Wilbur Whateley's bureaucratic demon persona.
- [`.kiro/specs/puzzle_engine_spec.md`](.kiro/specs/puzzle_engine_spec.md): 4-phase state transitions and offline fallback rules.
- [`.kiro/specs/mcp_contract.md`](.kiro/specs/mcp_contract.md): JSON-RPC MCP tool schemas and HTTP Bridge contracts.

---

## 🧪 Testing

Run automated backend and puzzle verification tests:
```bash
pytest tests/ -v
```

---

## 📜 License
MIT License. Inspired by H.P. Lovecraft's *The Dunwich Horror* (1928, Public Domain).
