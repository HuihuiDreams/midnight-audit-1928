# Architecture & Cross-Platform Constraints — The Midnight Audit (1928)

## 1. Heterogeneous "Frankenstein" System Architecture

The Midnight Audit stitches three disparate eras of computing into an unholy, living puzzle game:

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

## 2. Windows File Exclusive Lock Avoidance (Crucial Constraint)

> [!CAUTION]
> **Never open or write to an active `.xlsm` file via `openpyxl` while Excel has it open.**
> Windows enforces a mandatory exclusive file lock on `.xlsm`. Invoking `openpyxl.load_workbook()` or `.save()` on an open workbook causes `PermissionError: [Errno 13] Permission denied`.

### Design Rules:
1. **Offline Template Generation Only**: `openpyxl` is strictly restricted to pre-game build scripts (`scripts/build_ledger.py`) to generate the initial blank/formatted workbook.
2. **In-Flight Cell Mutation**:
   - Primary: VBA hooks report user actions via lightweight HTTP POST requests to `http://127.0.0.1:8000/api/event`.
   - VBA applies the returned JSON mutation instructions (`Interior.Color`, `Value`, `Font.Color`, `Blink`) directly inside the Excel application thread.
   - Haunts queued by the Agent are fetched by a 3-second `Application.OnTime` heartbeat (`GET /api/pending`, `StartHauntPolling` / `StopHauntPolling`); the poller is cancelled on `EmergencyReset`, workbook close, and archive seal, and never falls back to the offline engine.
   - The midnight clock is a client-only `Application.OnTime` timer (`MidnightClockTick`, every 20 s, `StartMidnightClock` / `StopMidnightClock` in `M_HorrorFX.bas`). It is cancelled at the same points as the poller and on foreclosure; the daemon does not track it.
   - Camera moves change only `ThisWorkbook.Windows(1)` (`Zoom`, `ScrollRow`, `ScrollColumn`), never `ActiveWindow`, which can belong to another workbook.
   - Secondary (Windows optional): `xlwings` / COM dispatch can be used if explicit out-of-process control is desired, but the HTTP API bridge is the canonical cross-platform mechanism.
3. **Offline Fallback**: If the Python daemon is unreachable, the VBA client automatically falls back to an embedded, zero-dependency offline puzzle rule engine without crashing.

---

## 3. Cross-Platform VBA Architecture & PtrSafe Specifications

To guarantee seamless execution across Windows (32-bit & 64-bit Office) and macOS:

### 3.1 Conditional Compilation Headers
Every Windows API declaration must be protected with `#If...#ElseIf...#End If` directives:

```vba
#If Mac Then
    ' macOS native or AppleScript fallbacks (no Win32 DLLs)
#ElseIf VBA7 Then
    ' 64-bit Office on Windows (PtrSafe mandatory, LongPtr for handles/pointers)
    Private Declare PtrSafe Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)
    Private Declare PtrSafe Function BeepAPI Lib "kernel32" Alias "Beep" (ByVal dwFreq As Long, ByVal dwDuration As Long) As Long
    Private Declare PtrSafe Function GetForegroundWindow Lib "user32" () As LongPtr
    Private Declare PtrSafe Function MoveWindow Lib "user32" (ByVal hWnd As LongPtr, ByVal x As Long, ByVal y As Long, ByVal nWidth As Long, ByVal nHeight As Long, ByVal bRepaint As Long) As Long
    Private Declare PtrSafe Function GetWindowRect Lib "user32" (ByVal hWnd As LongPtr, lpRect As RECT) As Long
#Else
    ' 32-bit legacy Office on Windows
    Private Declare Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)
    Private Declare Function BeepAPI Lib "kernel32" Alias "Beep" (ByVal dwFreq As Long, ByVal dwDuration As Long) As Long
    Private Declare Function GetForegroundWindow Lib "user32" () As Long
    Private Declare Function MoveWindow Lib "user32" (ByVal hWnd As Long, ByVal x As Long, ByVal y As Long, ByVal nWidth As Long, ByVal nHeight As Long, ByVal bRepaint As Long) As Long
    Private Declare Function GetWindowRect Lib "user32" (ByVal hWnd As Long, lpRect As RECT) As Long
#End If
```

### 3.2 macOS Audio & Tremor Fallbacks
- On macOS, `kernel32` and `user32` are absent. Audio calls fall back to `MacScript("beep")` or terminal visual flash.
- Screen tremor on macOS flickers the ledger header (`FlashKeroseneLamp`) instead of moving a window: there is no safe window handle, and scrolling `ActiveWindow` can hit another workbook. On Windows the tremor moves `Application.Hwnd` only, and only while Excel is the foreground window.

### 3.3 HTTP Transport
- Windows: `CreateObject("MSXML2.ServerXMLHTTP.6.0")` with 500ms timeout.
- macOS: `MacScript("do shell script ""curl -s -m 1 ...""")` or fallback to Offline Mode.

### 3.4 Emergency Escape Hatch (`Ctrl+Shift+R`)
Stripping Excel UI (hiding toolbars, formula bars, scrollbars) poses a risk of locking the user out of their application if an error occurs. An infallible `EmergencyReset` routine bound to `Ctrl+Shift+R` must always be registered on `Workbook_Open` and restored on `Workbook_BeforeClose`.

### 3.5 ASCII-Only VBA Sources
The VBE imports `.bas` / `.cls` files with the system ANSI code page, so UTF-8 glyphs (em-dashes, arrows, emoji) arrive as mojibake. Every file in `src/vba/` must stay pure ASCII (enforced by `tests/test_fixes_verification.py`). Build non-ASCII characters at runtime with `ChrW`, e.g. the HUD candle in `WaxSealLabel()` (UTF-16 surrogate pair `ChrW(55357) & ChrW(56687)` plus the variation selector `ChrW(65039)`). Lit buttons use Bone Paper (`#D3CEB9`) text, never pure white.
