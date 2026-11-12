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

# Install uv once for Kiro MCP and verification hooks.
# macOS with Homebrew:
brew install uv
# Other platforms: https://docs.astral.sh/uv/getting-started/installation
uv --version

# Start the Local Daemon Bridge
python3 -m src.backend.server
# (or: python3 src/backend/server.py)
```
*(The daemon will run on `http://127.0.0.1:8000` by default; custom port can be set via `SERVER_PORT`)*

### Step 2: Kiro MCP Integration (Optional)
The workspace ships with `.kiro/settings/mcp.json`. Kiro starts the `midnight-audit-mcp` server with `uv`, so install `uv` before opening this project in Kiro. After the configuration reloads, the MCP tools `inspect_ledger`, `haunt_spreadsheet`, and `judge_ritual` are available to the agent.

The save hook at `.kiro/hooks/verify-backend-and-ledger.json` also requires `uv`. When a backend Python file or `scripts/build_ledger.py` is saved, it runs the full suite and rebuilds the template only after tests pass.

Verify the same command manually:

```bash
uv run --with-requirements requirements.txt python -m pytest -q && \
  uv run --with-requirements requirements.txt python scripts/build_ledger.py
```

### Step 3: Generate or Open the Ledger
```bash
# Generate the initial Morbid Archive template
python3 scripts/build_ledger.py
```

#### Importing VBA Modules into Excel (One-time Setup)
Because `openpyxl` generates `.xlsx` styling and layout while Excel compiles macros into a binary `vbaProject.bin` container, you only need to import the VBA modules in Excel **once** and save as `.xlsm`. Every subsequent time you open the `.xlsm` file, it is immediately playable:

1. **Open the Template**: Open `Midnight_Audit_1928_Template.xlsx` in Microsoft Excel.
2. **Open the Visual Basic Editor**:
   - **Windows**: Press **`Alt + F11`**
   - **macOS**: Press **`Fn + Option + F11`** (or top menu: *Tools > Macro > Visual Basic Editor*).
3. **Import the 3 Standard Modules (`.bas`)**:
   - In the VBE menu, select **File > Import File...** and import the 3 `.bas` files from `src/vba/`:
     - `src/vba/M_Bootstrap.bas`
     - `src/vba/M_DaemonBridge.bas`
     - `src/vba/M_HorrorFX.bas`
4. **Paste the 2 Document Event Classes (`.cls` — Copy & Paste Only)**:
   - ⚠️ *Important*: `Sheet1_Archive.cls` and `ThisWorkbook.cls` are Excel document class modules. Do **not** use *File > Import File* for them (importing creates detached class modules that won't intercept worksheet/workbook events).
   - Double-click **`Sheet1 (Audit_Ledger_1928)`** in the left VBA Project tree, open `src/vba/Sheet1_Archive.cls` in a text editor, copy everything **starting from line 10 (`Option Explicit`) to the end** (skip lines 1–9 `VERSION 1.0 CLASS ... Attribute VB_...`), and paste it into the `Sheet1` code pane.
   - Double-click **`ThisWorkbook`** in the left VBA Project tree, open `src/vba/ThisWorkbook.cls` in a text editor, copy everything **starting from line 10 (`Option Explicit`) to the end**, and paste it into the `ThisWorkbook` code pane.
5. **Save as `.xlsm`**:
   - Return to Excel, go to **File > Save As...**, choose file format **Excel Macro-Enabled Workbook (`.xlsm`)**, and save it as `Midnight_Audit_1928_Template.xlsm`.

### Step 4: Excel Security & Macro Settings
1. Close and reopen `Midnight_Audit_1928_Template.xlsm`. When prompted by Excel, click **"Enable Content"** or **"Enable Macros"** (`Workbook_Open` will automatically launch the 1928 archive UI).
2. **Emergency Reset (`Ctrl + Shift + R`)**: If at any point you want to restore standard Excel toolbars, ribbons, formula bars, and gridlines, press **`Ctrl + Shift + R`** (or run the `EmergencyReset` macro).

### Step 5: Solve the 4-Phase Audit Loop
1. **Phase 1 (The Audit Discrepancy)**: Read Rule 1 on the Yellow Handover Note (`K4:AN12`). Check borrower `Wilbur Whateley` in Row 7 (Overdue: 140 days). Type `7.00` (or `$7.00`) into **`H7`** (140 × $0.05) and press Enter. Watch Row 13 awaken.
2. **Phase 2 (The Unseen Intruder)**: Read Rule 2. Click the green **`[ SPRAY REAGENT ]`** bar (`K18:AN18`). Watch the 30×30 occult sanctum and blinking cosmic eye (`W34:X35`) manifest.
3. **Phase 3 (The Hijacked Typing)**: Read Rule 3. Decode the charred ROT-3 cipher strip (`B21:H28`: `VHDO WKH GHHS YDXOW` -> `SEAL THE DEEP VAULT`). Type anything into Cell **`B18`** first to experience the typewriter hijacking (`YOUR SALARY CANNOT SAVE YOU`), then enter **`SEAL THE DEEP VAULT`** and press Enter — `[ SEAL ARCHIVE ]` (`C18:D18`) turns warning red.
4. **Phase 4 (The Midnight Settlement)**: Click **`[ SEAL ARCHIVE ]`** (`C18:D18`). Thunder lightning flashes, the window trembles, and the ledger is permanently stamped closed at `OCTOBER 31, 1928 - 00:01 AM`.

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

## 🛡️ Kiro Specification System (`/.kiro`) & Agent Guidelines

This project is built under strict compliance with Kiro agent steering and specification standards:
- [`.kiro/steering/agent_guidelines.md`](.kiro/steering/agent_guidelines.md): Core agent working guidelines, holistic UI design standards, Karpathy guidelines, TDD protocols, and story lore grounding.
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
