#!/usr/bin/env python3
"""
The Midnight Audit (1928) — VBA Entity Face Sync
Regenerates the entity-face block in src/vba/M_HorrorFX.bas from ENTITY_FACE_MATRIX and
ENTITY_FACE_LEGEND in src/backend/puzzle_state.py (the single source of truth), so the
offline Excel fallback and the daemon's /api/pixel_radar always draw the same 30x30 face.

Run after editing the matrix:  python scripts/sync_vba_radar.py
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.backend.puzzle_state import ENTITY_FACE_LEGEND, ENTITY_FACE_MATRIX

VBA_FILE = os.path.join(PROJECT_ROOT, "src", "vba", "M_HorrorFX.bas")
BEGIN_MARKER = "' BEGIN GENERATED ENTITY FACE"
END_MARKER = "' END GENERATED ENTITY FACE"
FALLBACK_COLOR = "COLOR_BONE_PAPER"

def render_block() -> str:
    lines = [
        f"{BEGIN_MARKER} - do not edit by hand; run scripts/sync_vba_radar.py",
        "' Source of truth: ENTITY_FACE_MATRIX and ENTITY_FACE_LEGEND in src/backend/puzzle_state.py",
        "Private Function EntityFaceRow(ByVal r As Long) As String",
        "    Select Case r",
    ]
    for number, row in enumerate(ENTITY_FACE_MATRIX, start=1):
        lines.append(f'        Case {number}: EntityFaceRow = "{row}"')
    lines += [
        "    End Select",
        "End Function",
        "",
        "Private Function EntityFaceColor(ByVal ch As String) As Long",
        "    Select Case ch",
    ]
    for char, palette_name in ENTITY_FACE_LEGEND.items():
        lines.append(f'        Case "{char}": EntityFaceColor = COLOR_{palette_name}')
    lines += [
        f"        Case Else: EntityFaceColor = {FALLBACK_COLOR}",
        "    End Select",
        "End Function",
        END_MARKER,
    ]
    return "\n".join(lines)

def sync(path: str = VBA_FILE) -> bool:
    """Rewrite the generated block in place. Returns True when the file changed."""
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    start = source.index(BEGIN_MARKER)
    end = source.index(END_MARKER) + len(END_MARKER)
    updated = source[:start] + render_block() + source[end:]
    if updated == source:
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    return True

if __name__ == "__main__":
    print("Updated" if sync() else "Already up to date", VBA_FILE)
