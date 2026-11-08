import sys
import json
from typing import Dict, Any, List, Optional
from src.backend.puzzle_state import PuzzleEngine

engine = PuzzleEngine()

def list_tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": "inspect_ledger",
            "description": "Inspect the active 1928 archive ledger, current game phase, auditor records, and supernatural anomalies.",
            "inputSchema": {
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
        },
        {
            "name": "haunt_spreadsheet",
            "description": "Trigger an eldritch haunting in the player's active Excel spreadsheet (whisper, cell overwrite, lamp flicker, tremor, etc.).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "haunt_type": {
                        "type": "string",
                        "enum": ["cell_text", "flicker_lamp", "thunder_invert", "ink_spread", "whisper", "screen_tremor"],
                        "description": "Type of supernatural haunting effect."
                    },
                    "target_cell": {
                        "type": "string",
                        "description": "Target cell coordinate (e.g. 'B18', 'A13', 'H7')."
                    },
                    "message": {
                        "type": "string",
                        "description": "Haunting dialogue or text mutation to inject."
                    }
                },
                "required": ["haunt_type"]
            }
        },
        {
            "name": "judge_ritual",
            "description": "Evaluate an auditor's sealing ritual or incantation to determine if the cosmic entity is banished.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "phrase": {
                        "type": "string",
                        "description": "The banishment incantation or override phrase entered by the player."
                    }
                },
                "required": ["phrase"]
            }
        }
    ]

def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    global engine

    if name == "inspect_ledger":
        target = arguments.get("target_range")
        state = engine.get_state()
        
        lines = [
            "=== THE MIDNIGHT AUDIT (1928) - LEDGER INSPECTION ===",
            f"Current Phase: {state['phase']} ({state['phase_name']})",
            f"Row 13 Awakened: {state['row13_awakened']}",
            f"Intruder Revealed: {state['intruder_revealed']}",
            f"Archive Sealed: {state['archive_sealed']}",
            ""
        ]

        if target:
            t_upper = target.strip().upper()
            lines.append(f"[Inspecting Cell/Range {t_upper}]")
            if "7" in t_upper or "H7" in t_upper:
                r7 = engine.ledger_data[7]
                lines.append(f"Row 7: {r7['borrower']} | Overdue: {r7['overdue']} days | Fee Paid: {r7['fee']} | Status: {r7['status']}")
            elif "13" in t_upper:
                lines.append("Row 13: [PURE BLACK ABYSS] - Text hidden unless inverted.")
                if state["row13_awakened"]:
                    lines.append("Abyss Message: 'STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS'")
            elif "18" in t_upper or "B18" in t_upper:
                lines.append(f"Cell B18: Override Code Cell (Phase 3). Hijack triggered: {engine.hijack_triggered}")
            else:
                lines.append(f"Target range {t_upper} appears standard or within ledger scope.")
        else:
            lines.append("Active Ledger Records:")
            for row_idx, r in engine.ledger_data.items():
                lines.append(f"  Row {row_idx}: {r['id']} | {r['borrower']} | Due Overdue: {r['overdue']}d | Fee: {r['fee']} | {r['status']}")

        return {"content": [{"type": "text", "text": "\n".join(lines)}]}

    elif name == "haunt_spreadsheet":
        haunt_type = arguments.get("haunt_type", "whisper")
        target_cell = arguments.get("target_cell")
        message = arguments.get("message", "THE AUDIT WATCHES")
        
        engine.queue_haunt(haunt_type, target_cell, message)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Queued haunting effect '{haunt_type}' on cell '{target_cell}' with message: \"{message}\"."
                }
            ]
        }

    elif name == "judge_ritual":
        phrase = arguments.get("phrase", "")
        res = engine.judge_ritual(phrase)
        if res["banished"]:
            text = f"RITUAL SUCCESSFUL! {res['message']}\nSTAMP: {res['stamp']}"
        else:
            text = f"RITUAL REJECTED: {res['message']}"
        return {"content": [{"type": "text", "text": text}]}

    else:
        return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}

def handle_json_rpc(request: Dict[str, Any]) -> Dict[str, Any]:
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "midnight-audit-mcp",
                    "version": "1.0.0"
                }
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": list_tools()
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        result = call_tool(tool_name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": result
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

def run_stdio_server():
    """Stdio transport for MCP integration with Kiro IDE or Claude."""
    sys.stderr.write("The Midnight Audit MCP Server started over stdio.\n")
    sys.stderr.flush()
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            req = json.loads(line)
            resp = handle_json_rpc(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    run_stdio_server()
