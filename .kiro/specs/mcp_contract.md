# MCP Contract & HTTP Daemon API Specification

## 1. Overview

The communication architecture bridges the 1990s Excel VBA environment, the local Python daemon, and the 2026 Kiro Agent via two channels:
1. **HTTP Bridge API** (`http://127.0.0.1:8000/api/...`): Invoked directly by VBA macros via `MSXML2.ServerXMLHTTP` or curl.
2. **Kiro Model Context Protocol (MCP) Server**: Standard JSON-RPC 2.0 tool interface running over stdio, allowing the Kiro IDE Agent to inspect the active spreadsheet and inject live hauntings.

---

## 2. HTTP Daemon Bridge API Contract

### 2.1 `GET /api/status`
Returns the current phase, active anomalies, and queued instructions for the VBA client.
- **Request**: `GET /api/status`
- **Response** (`application/json`):
```json
{
  "phase": 1,
  "phase_name": "THE_AUDIT_DISCREPANCY",
  "row13_awakened": false,
  "intruder_revealed": false,
  "archive_sealed": false,
  "pending_effects": [
    {
      "type": "cell_text",
      "cell": "A13",
      "value": "STOP AUDITING ROW 13."
    }
  ]
}
```

### 2.2 `POST /api/event`
Dispatched by VBA when a critical worksheet event occurs (e.g., cell edit, button click).
- **Request Body**:
```json
{
  "event_type": "cell_change",
  "cell": "H7",
  "value": "7.00"
}
```
- **Response**:
```json
{
  "accepted": true,
  "current_phase": 2,
  "message": "Overdue balance settled. The abyss stirs.",
  "actions": [
    {
      "command": "SET_VALUE",
      "cell": "I7",
      "value": "BALANCED (UNHOLY)"
    },
    {
      "command": "AWAKEN_ROW_13",
      "cell": "A13",
      "text": "STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"
    },
    {
      "command": "TRIGGER_FX",
      "effect": "THUD_BEEP"
    }
  ]
}
```

### 2.3 `POST /api/banish`
Processes the final banishing ritual command or code phrase.
- **Request Body**:
```json
{
  "phrase": "SEAL THE DEEP VAULT"
}
```
- **Response**:
```json
{
  "banished": true,
  "stamp": "[ ARCHIVE SEALED - OCTOBER 31, 1928 - 00:01 AM ]",
  "actions": [
    {
      "command": "TRIGGER_FX",
      "effect": "THUNDER_STROBE"
    },
    {
      "command": "TRIGGER_FX",
      "effect": "SCREEN_TREMOR"
    },
    {
      "command": "LOCK_SHEET",
      "color": "#8A8D8F"
    }
  ]
}
```

### 2.4 `GET /api/pixel_radar`
Returns the 30x30 matrix of hex colors for rendering the chemical developer reveal in Phase 2.
- **Response**:
```json
{
  "rows": 30,
  "cols": 30,
  "start_cell": "K20",
  "grid": [
    ["#D3CEB9", "#D3CEB9", "#181614", ...],
    ...
  ],
  "blinking_cells": ["W34", "X34", "W35", "X35"]
}
```

---

## 3. Kiro Model Context Protocol (MCP) Tool Schemas

The MCP server exposes three tools to the Kiro Agent:

### 3.1 Tool: `inspect_ledger`
Allows the Kiro Agent to inspect the current state of the ledger, player inputs, and active phase.
- **Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "target_range": {
      "type": "string",
      "description": "Optional cell or range to inspect (e.g. 'H7', 'A13:I13', 'B18'). If omitted, returns entire ledger summary."
    },
    "include_anomalies": {
      "type": "boolean",
      "description": "Whether to include hidden supernatural states and coordinates."
    }
  }
}
```
- **Returns**: Formatted text summary of cell contents, phase status, and auditor progress.

### 3.2 Tool: `haunt_spreadsheet`
Empowers the Kiro Agent to intervene dynamically in the spreadsheet, overwriting text, flickering the screen, or spreading bloodstains.
- **Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "haunt_type": {
      "type": "string",
      "enum": ["cell_text", "flicker_lamp", "thunder_invert", "ink_spread", "whisper", "screen_tremor"],
      "description": "Type of supernatural effect to trigger."
    },
    "target_cell": {
      "type": "string",
      "description": "Target cell coordinate (e.g. 'B18', 'A13', 'H7')."
    },
    "message": {
      "type": "string",
      "description": "Spectral dialogue or text mutation to inject."
    }
  },
  "required": ["haunt_type"]
}
```
- **Returns**: Confirmation that the haunting action was placed in the dispatch queue.

### 3.3 Tool: `judge_ritual`
Allows the Kiro Agent to evaluate a freeform player ritual or sealing incantation.
- **Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "phrase": {
      "type": "string",
      "description": "The banishment incantation or override phrase entered by the player."
    }
  },
  "required": ["phrase"]
}
```
- **Returns**: Judgement object indicating whether the ritual succeeds, along with supernatural dialogue and concluding effects.
