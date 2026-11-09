#!/usr/bin/env python3
"""
The Midnight Audit (1928) — Ledger Builder Script
Generates the pre-formatted Morbid Archive template with 1928 visual styling,
full-bleed desk canvas, accounting double-ruled borders, Row 13 Abyss (220pt height),
pinned dossier handover notes, and 30x30 corrupted blueprint radar grid.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from src.backend.puzzle_state import PALETTE

TEMPLATE_FILENAME = "Midnight_Audit_1928_Template.xlsx"

# Palette definitions derived from single source of truth (openpyxl hex format without '#')
HEX_PALETTE = {k: v.lstrip("#") for k, v in PALETTE.items()}

COLOR_BONE_PAPER = HEX_PALETTE["BONE_PAPER"]
COLOR_DECAYING_PAPER = HEX_PALETTE["DECAYING_PAPER"]
COLOR_CARBON = HEX_PALETTE["CARBON"]
COLOR_HOSPITAL_GREEN = HEX_PALETTE["HOSPITAL_GREEN"]
COLOR_DRIED_BLOOD = HEX_PALETTE["DRIED_BLOOD"]
COLOR_YELLOW_NOTE = HEX_PALETTE["YELLOW_NOTE"]
COLOR_WARNING_RED = HEX_PALETTE["WARNING_RED"]
COLOR_PHOSPHOR_GREEN = HEX_PALETTE["PHOSPHOR_GREEN"]
COLOR_COLD_ASH = HEX_PALETTE["COLD_ASH"]
COLOR_ABYSS = "000000"
COLOR_PUMPKIN_ORANGE = "D9681A"

# ==============================================================================
# ==============================================================================
# ASCII Pixel Art Sprite Matrices (5 to 6 columns wide)
# Rendered inside Primary Visible Viewport onto Square-Pixel Grid (W4:AN12)
# ==============================================================================
# 5 columns wide x 9 rows tall (Columns W..AA, Rows 4..12)
SPRITE_CANDLE = [
    "..f..",  # Row 4:  Flame tip (warning red)
    ".fFf.",  # Row 5:  Flame body with glowing phosphor core
    "..W..",  # Row 6:  White-hot flame core
    "..w..",  # Row 7:  Charred candle wick
    ".CCC.",  # Row 8:  Pale bone candle wax shaft
    ".cCCc",  # Row 9:  Melting wax drips
    ".bBb.",  # Row 10: Brass candle saucer cup
    "bBBBB",  # Row 11: Brass saucer tray & finger loop handle
    ".SSS.",  # Row 12: Cast desk shadow (terminates above Row 13 Abyss)
]

# 6 columns wide x 9 rows tall (Columns AC..AH, Rows 4..12)
SPRITE_SKULL = [
    ".bbbb.",  # Row 4:  Cranial dome
    "bBBBBb",  # Row 5:  Upper cranium & suture line
    "bBDDBb",  # Row 6:  Forehead bloodstain
    "BBBBBB",  # Row 7:  Heavy brow ridge
    "bXEEXb",  # Row 8:  Eye sockets (abyss) with glowing phosphor pupils (E at AE8 & AF8)
    ".bXXb.",  # Row 9:  Nasal cavity void (XX) & cheekbones
    ".bBBb.",  # Row 10: Maxilla upper jaw
    ".BCBC.",  # Row 11: Grinning skeletal teeth
    "..bb..",  # Row 12: Mandible chin
]

# 5 columns wide x 9 rows tall (Columns AJ..AN, Rows 4..12)
SPRITE_PUMPKIN = [
    "..gG.",  # Row 4:  Crooked stem tip (hospital green & phosphor)
    "..G..",  # Row 5:  Stem base
    ".oOo.",  # Row 6:  Pumpkin crown (vibrant orange rind with crimson outline)
    "oEOEo",  # Row 7:  Triangular carved glowing eyes (E at AK7 & AM7)
    "o.E.o",  # Row 8:  Carved glowing nose
    "oEoEo",  # Row 9:  Carved saw-tooth mouth with pumpkin tooth
    "oEEEo",  # Row 10: Lower mouth glowing candle fire
    ".oOo.",  # Row 11: Pumpkin lower belly
    "..S..",  # Row 12: Cast desk shadow
]

def render_pixel_sprite(ws, start_row: int, start_col: int, sprite_map: list, char_fill_map: dict):
    """Renders a pixel art sprite matrix onto Excel cells with seamless borderless tiles."""
    for r_idx, line in enumerate(sprite_map):
        for c_idx, char in enumerate(line):
            if char in char_fill_map:
                cell = ws.cell(row=start_row + r_idx, column=start_col + c_idx)
                cell.fill = char_fill_map[char]
                cell.border = None

def build_ledger_workbook(output_path: str = TEMPLATE_FILENAME) -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = "Audit_Ledger_1928"
    # Hide raw Excel gridlines so the sheet reads as a 1928 archival artifact, not a modern spreadsheet
    ws.views.sheetView[0].showGridLines = False
    ws.views.sheetView[0].zoomScale = 85
    ws.sheet_view.zoomScale = 85

    # Styling helpers
    font_stamp = Font(name="Courier New", size=9, bold=True, color=COLOR_WARNING_RED)
    font_title = Font(name="Courier New", size=15, bold=True, color=COLOR_BONE_PAPER)
    font_subtitle = Font(name="Courier New", size=9.5, italic=True, color=COLOR_CARBON)
    font_header = Font(name="Courier New", size=11, bold=True, color=COLOR_CARBON)
    font_body = Font(name="Courier New", size=10, bold=False, color=COLOR_CARBON)
    font_flagged = Font(name="Courier New", size=10, bold=True, color=COLOR_WARNING_RED)
    font_hidden = Font(name="Courier New", size=14, bold=True, color=COLOR_ABYSS)
    font_censored = Font(name="Courier New", size=10, bold=False, color=COLOR_ABYSS)
    font_note = Font(name="Courier New", size=10, bold=False, color=COLOR_CARBON)
    font_seal = Font(name="Courier New", size=9, bold=True, color=COLOR_WARNING_RED)
    font_desk_footer = Font(name="Courier New", size=9, italic=True, color=COLOR_HOSPITAL_GREEN)

    fill_bone = PatternFill(fill_type="solid", start_color=COLOR_BONE_PAPER, end_color=COLOR_BONE_PAPER)
    fill_decay = PatternFill(fill_type="solid", start_color=COLOR_DECAYING_PAPER, end_color=COLOR_DECAYING_PAPER)
    fill_carbon = PatternFill(fill_type="solid", start_color=COLOR_CARBON, end_color=COLOR_CARBON)
    fill_blood = PatternFill(fill_type="solid", start_color=COLOR_DRIED_BLOOD, end_color=COLOR_DRIED_BLOOD)
    fill_hospital = PatternFill(fill_type="solid", start_color=COLOR_HOSPITAL_GREEN, end_color=COLOR_HOSPITAL_GREEN)
    fill_abyss = PatternFill(fill_type="solid", start_color=COLOR_ABYSS, end_color=COLOR_ABYSS)
    fill_note = PatternFill(fill_type="solid", start_color=COLOR_YELLOW_NOTE, end_color=COLOR_YELLOW_NOTE)
    fill_spray = PatternFill(fill_type="solid", start_color=COLOR_PHOSPHOR_GREEN, end_color=COLOR_PHOSPHOR_GREEN)
    fill_red = PatternFill(fill_type="solid", start_color=COLOR_WARNING_RED, end_color=COLOR_WARNING_RED)
    fill_pumpkin = PatternFill(fill_type="solid", start_color=COLOR_PUMPKIN_ORANGE, end_color=COLOR_PUMPKIN_ORANGE)

    char_fill_map = {
        ".": fill_carbon,
        "F": fill_spray,
        "f": fill_red,
        "w": fill_abyss,
        "W": fill_bone,
        "C": fill_bone,
        "c": fill_decay,
        "D": fill_blood,
        "d": fill_red,
        "B": fill_decay,
        "b": fill_bone,
        "S": fill_abyss,
        "E": fill_spray,
        "X": fill_abyss,
        "G": fill_hospital,
        "g": fill_spray,
        "O": fill_pumpkin,
        "o": fill_red,
        "R": fill_red,
    }

    thin_border = Border(
        left=Side(style='thin', color=COLOR_HOSPITAL_GREEN),
        right=Side(style='thin', color=COLOR_HOSPITAL_GREEN),
        top=Side(style='thin', color=COLOR_HOSPITAL_GREEN),
        bottom=Side(style='thin', color=COLOR_HOSPITAL_GREEN)
    )

    header_border = Border(
        left=Side(style='thin', color=COLOR_CARBON),
        right=Side(style='thin', color=COLOR_CARBON),
        top=Side(style='medium', color=COLOR_CARBON),
        bottom=Side(style='double', color=COLOR_CARBON)
    )

    abyss_border = Border(
        left=Side(style='thin', color=COLOR_DRIED_BLOOD),
        right=Side(style='thin', color=COLOR_DRIED_BLOOD),
        top=Side(style='double', color=COLOR_WARNING_RED),
        bottom=Side(style='double', color=COLOR_WARNING_RED)
    )

    # 0. Full-Bleed Desk Canvas Backdrop (Rows 1..60, Cols 1..52)
    # Eliminates all raw modern Excel white background cells around and below the ledger
    for r in range(1, 61):
        ws.row_dimensions[r].height = 18
        for c in range(1, 53):
            ws.cell(row=r, column=c).fill = fill_carbon

    # Outer Parchment Folio Margin (A1:I19)
    for r in range(1, 20):
        for c in range(1, 10):
            ws.cell(row=r, column=c).fill = fill_decay

    # 1. Row 1: 1928 Archival Classification & Blood-Wax Stamp Header
    ws.row_dimensions[1].height = 20
    ws.merge_cells("A1:F1")
    ws["A1"] = "  FORM MU-1928-VIII  |  RESTRICTED CUSTODIAL LEDGER  |  ARKHAM, MASS."
    ws["A1"].font = Font(name="Courier New", size=9, bold=True, color=COLOR_CARBON)
    ws["A1"].alignment = Alignment(horizontal="left", vertical="center")

    ws.merge_cells("G1:I1")
    ws["G1"] = "🩸 [ ALL HALLOWS' EVE — 11:47 PM ]  "
    ws["G1"].font = font_stamp
    ws["G1"].alignment = Alignment(horizontal="right", vertical="center")

    for c in range(1, 10):
        ws.cell(row=1, column=c).fill = fill_decay
        ws.cell(row=1, column=c).border = Border(
            top=Side(style='medium', color=COLOR_CARBON),
            bottom=Side(style='thin', color=COLOR_CARBON)
        )

    # 2. Document Title Banners (Rows 2-3: Engraved Dark Header & Ledger Subtitle)
    ws.merge_cells("A2:I2")
    ws["A2"] = "  MISKATONIC UNIVERSITY — ANNEX ARCHIVE DELINQUENCY LEDGER"
    ws["A2"].font = font_title
    ws["A2"].alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[2].height = 28

    for c in range(1, 10):
        cell = ws.cell(row=2, column=c)
        cell.fill = fill_carbon
        cell.border = Border(
            left=Side(style='medium', color=COLOR_CARBON) if c == 1 else None,
            right=Side(style='medium', color=COLOR_CARBON) if c == 9 else None,
            top=Side(style='medium', color=COLOR_CARBON),
            bottom=Side(style='double', color=COLOR_WARNING_RED)
        )

    ws.merge_cells("A3:I3")
    ws["A3"] = "  FISCAL PERIOD: OCTOBER 1928 | HALLOWEEN MIDNIGHT CUSTODIAL AUDIT | ALL BALANCES SUBJECT TO CUSTODIAL SEAL"
    ws["A3"].font = font_subtitle
    ws["A3"].alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[3].height = 20

    for c in range(1, 10):
        cell = ws.cell(row=3, column=c)
        cell.fill = fill_bone
        cell.border = thin_border

    # Row 4: Accounting Double-Rule Separator Strip (18pt height matching 1:1 square pixel aspect ratio)
    ws.row_dimensions[4].height = 18
    for c in range(1, 10):
        cell = ws.cell(row=4, column=c)
        cell.fill = fill_decay
        cell.border = Border(
            top=Side(style='thin', color=COLOR_HOSPITAL_GREEN),
            bottom=Side(style='double', color=COLOR_CARBON)
        )

    # 3. Table Column Headers (Row 5)
    headers = [
        "Record ID",
        "Borrower Name",
        "Department / Town",
        "Catalog / Tome Title",
        "Checkout Date",
        "Due Date",
        "Overdue Days",
        "Late Fee Paid ($)",
        "Audit Status"
    ]
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=5, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_decay
        cell.border = header_border
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[5].height = 28

    # 4. Active Borrower Records (Rows 6-12) — 1928 Alternating Ledger Stripes & Red Audit Column Rules
    records = [
        ("ARK-001", "Henry Armitage", "Dept of Rare Books", "Cultes des Goules", "1928-09-01", "1928-10-01", 12, 0.60, "CLEARED"),
        ("ARK-007", "Wilbur Whateley", "Dunwich Settlement", "Necronomicon (Dee Trans.)", "1928-04-15", "1928-05-26", 140, None, "FLAGGED"),
        ("ARK-012", "Francis Morgan", "Dept of Archaeology", "Book of Eibon", "1928-08-10", "1928-09-08", 35, 1.75, "CLEARED"),
        ("ARK-019", "Warren Rice", "Dept of Classical Lang", "De Vermis Mysteriis", "1928-06-20", "1928-07-25", 80, 4.00, "CLEARED"),
        ("ARK-023", "Asenath Waite", "Innsmouth Requisition", "Unaussprechlichen Kulten", "1928-09-10", "1928-09-28", 15, 0.75, "CLEARED"),
        ("ARK-031", "Pickman, R.U.", "Boston Fine Arts", "Ars Magna Lucis et Umbrae", "1928-06-01", "1928-07-10", 95, 4.75, "CLEARED"),
        ("ARK-040", "Edward Derby", "Dept of Literature", "Liber Ivonis", "1928-10-01", "1928-10-08", 5, 0.25, "CLEARED"),
    ]

    for i, row_data in enumerate(records, start=6):
        ws.row_dimensions[i].height = 22
        is_even_row = (i % 2 == 1)
        row_fill = fill_decay if is_even_row else fill_bone
        for j, val in enumerate(row_data, start=1):
            cell = ws.cell(row=i, column=j, value=val)
            cell.font = font_body
            cell.fill = row_fill

            # Classic 1920s bookkeeper vertical double-red audit rule on Column H (Late Fee)
            if j == 8:
                if i == 7:
                    # Active input target H7: highlighted bone paper with blood-red focus frame
                    cell.fill = fill_bone
                    cell.border = Border(
                        left=Side(style='double', color=COLOR_WARNING_RED),
                        right=Side(style='double', color=COLOR_WARNING_RED),
                        top=Side(style='medium', color=COLOR_WARNING_RED),
                        bottom=Side(style='medium', color=COLOR_WARNING_RED)
                    )
                else:
                    cell.border = Border(
                        left=Side(style='double', color=COLOR_WARNING_RED),
                        right=Side(style='double', color=COLOR_WARNING_RED),
                        top=Side(style='thin', color=COLOR_HOSPITAL_GREEN),
                        bottom=Side(style='thin', color=COLOR_HOSPITAL_GREEN)
                    )
            else:
                cell.border = thin_border

            # Format currency, numbers & status
            if j == 1:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.font = Font(name="Courier New", size=10, bold=True, color=COLOR_CARBON)
            elif j in (5, 6):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif j == 7:  # Overdue Days
                cell.alignment = Alignment(horizontal="right", vertical="center")
                if i == 7:
                    cell.font = font_flagged
            elif j == 8:  # Fee
                cell.alignment = Alignment(horizontal="right", vertical="center")
                if val is not None:
                    cell.number_format = "$#,##0.00"
            elif j == 9:  # Status
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if val == "FLAGGED":
                    cell.font = font_flagged
                    cell.fill = fill_bone

    # 5. Row 13: The Abyss (Height = 220) — Blood-Rimmed Open Grave
    ws.row_dimensions[13].height = 220
    for col_idx in range(1, 10):
        cell = ws.cell(row=13, column=col_idx)
        cell.fill = fill_abyss
        cell.border = abyss_border

    ws.merge_cells("A13:I13")
    ws["A13"] = "STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"
    ws["A13"].font = font_hidden
    ws["A13"].alignment = Alignment(horizontal="center", vertical="center")

    # 6. Censored Rows (Rows 14-16)
    censored_records = [
        ("ARK-066", "[EXPUNGED BY ORDER]", "Dunwich Vault", "The Seven Cryptical Books", "1928-01-01", "1928-01-13", 273, None, "COORDINATE: RADAR GRID K20:AN49"),
        ("ARK-067", "[NAME MUTATED]", "Kadath Sub-basement", "Pnakotic Manuscripts", "1927-10-31", "1927-11-13", 345, None, "ACCESS DENIED"),
        ("ARK-068", "Keziah Mason", "Arkham Witch House", "Azathoth & Other Horrors", "1692-05-01", "1692-05-19", 86320, None, "REMAINS UNBURIED"),
    ]
    for i, row_data in enumerate(censored_records, start=14):
        ws.row_dimensions[i].height = 19
        for j, val in enumerate(row_data, start=1):
            cell = ws.cell(row=i, column=j, value=val)
            cell.font = font_censored
            cell.fill = fill_abyss
            cell.border = Border(
                left=Side(style='thin', color=COLOR_DRIED_BLOOD),
                right=Side(style='thin', color=COLOR_DRIED_BLOOD),
                top=Side(style='thin', color=COLOR_DRIED_BLOOD),
                bottom=Side(style='double', color=COLOR_CARBON) if i == 16 else Side(style='thin', color=COLOR_DRIED_BLOOD)
            )
            # Prevent text overflow across adjacent gutter columns
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, shrink_to_fit=True)
        # Explicitly enforce clean carbon desk canvas on gutter column J for censored rows
        ws.cell(row=i, column=10).fill = fill_carbon

    # Row 17: Archival Brass Binding Strip
    ws.row_dimensions[17].height = 12
    ws.merge_cells("A17:I17")
    ws["A17"] = "  ─── CUSTODIAL VAULT CONTAINMENT PROTOCOL (SEALING CIPHER REQUIRED BELOW) ───"
    ws["A17"].font = Font(name="Courier New", size=8.5, italic=True, color=COLOR_HOSPITAL_GREEN)
    ws["A17"].alignment = Alignment(horizontal="left", vertical="center")
    for c in range(1, 10):
        ws.cell(row=17, column=c).fill = fill_decay
        ws.cell(row=17, column=c).border = thin_border

    # 7. Row 18: Emergency Vault Override Input & Wax Seal Stamp
    ws.row_dimensions[18].height = 30
    ws["A18"] = "EMERGENCY OVERRIDE CODE (PHASE 3):"
    ws["A18"].font = font_header
    ws["A18"].fill = fill_decay
    ws["A18"].border = thin_border
    ws["A18"].alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    ws["B18"].font = Font(name="Courier New", size=11, bold=True, color=COLOR_CARBON)
    ws["B18"].fill = fill_bone
    ws["B18"].border = Border(
        left=Side(style='double', color=COLOR_WARNING_RED),
        right=Side(style='double', color=COLOR_WARNING_RED),
        top=Side(style='medium', color=COLOR_DRIED_BLOOD),
        bottom=Side(style='medium', color=COLOR_DRIED_BLOOD)
    )
    ws["B18"].alignment = Alignment(horizontal="center", vertical="center")

    # Phase 4 Button: [ SEAL ARCHIVE ] (C18:D18)
    ws.merge_cells("C18:D18")
    seal_btn = ws["C18"]
    seal_btn.value = "[ SEAL ARCHIVE ]"
    seal_btn.font = Font(name="Courier New", size=10, bold=True, color=COLOR_DECAYING_PAPER)
    seal_btn.fill = fill_hospital
    seal_btn.alignment = Alignment(horizontal="center", vertical="center")
    for c in range(3, 5):
        cell = ws.cell(row=18, column=c)
        cell.fill = fill_hospital
        cell.border = Border(
            left=Side(style='medium', color=COLOR_BONE_PAPER) if c == 3 else None,
            right=Side(style='medium', color=COLOR_CARBON) if c == 4 else None,
            top=Side(style='medium', color=COLOR_BONE_PAPER),
            bottom=Side(style='medium', color=COLOR_CARBON)
        )

    # Row 18 trailer (E18:I18) — Official Custodial Wax Seal Authentication Box
    ws.merge_cells("E18:I18")
    ws["E18"] = "🕯️ CUSTODIAL WAX SEAL: [ UNSEALED — BREACH IMMINENT ]"
    ws["E18"].font = font_seal
    ws["E18"].alignment = Alignment(horizontal="center", vertical="center")
    for c in range(5, 10):
        cell = ws.cell(row=18, column=c)
        cell.fill = fill_bone
        cell.border = Border(
            top=Side(style='double', color=COLOR_WARNING_RED),
            bottom=Side(style='double', color=COLOR_WARNING_RED),
            left=Side(style='medium', color=COLOR_WARNING_RED) if c == 5 else None,
            right=Side(style='medium', color=COLOR_WARNING_RED) if c == 9 else None
        )

    # Row 19: Ledger Folio Bottom Edge & Brass Plaque
    ws.row_dimensions[19].height = 20
    ws.merge_cells("A19:I19")
    ws["A19"] = "  MISKATONIC UNIVERSITY PRESS — FORMALDEHYDE PRESERVED FOLIO  |  DO NOT REMOVE FROM NIGHT DESK"
    ws["A19"].font = font_desk_footer
    ws["A19"].alignment = Alignment(horizontal="left", vertical="center")
    for c in range(1, 10):
        cell = ws.cell(row=19, column=c)
        cell.fill = fill_decay
        cell.border = Border(
            top=Side(style='thin', color=COLOR_HOSPITAL_GREEN),
            bottom=Side(style='double', color=COLOR_CARBON),
            left=Side(style='medium', color=COLOR_CARBON) if c == 1 else None,
            right=Side(style='medium', color=COLOR_CARBON) if c == 9 else None
        )

    # 8. Desk Artifact Below Ledger (B21:H26) — Torn 1928 Western Union / Arkham Sanatorium Field Note
    ws.merge_cells("B21:H25")
    telegram_cell = ws["B21"]
    telegram_cell.value = (
        "╔═══ [ POCKET FIELD ARTIFACT — CHARRED CIPHER KEY STRIP ] ═══════════════════╗\n"
        "║  FOUND ON DESK OF MISSING AUDITOR WARD (OCT 30, 1928 — 11:59 PM):          ║\n"
        "║  STANDARD ALPHABET :  A B C D E F G H I J K L M N O P Q R S T U V W X Y Z  ║\n"
        "║  DESK STRIP (ROT-3):  D E F G H I J K L M N O P Q R S T U V W X Y Z A B C  ║\n"
        "║  \"When the floorboards groan, shift three steps back from the abyss...\"    ║\n"
        "╚════════════════════════════════════════════════════════════════════════════╝"
    )
    telegram_cell.font = Font(name="Courier New", size=9.5, bold=False, color=COLOR_BONE_PAPER)
    telegram_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    for r in range(21, 26):
        for c in range(2, 9):
            tc = ws.cell(row=r, column=c)
            tc.fill = fill_blood
            tc.border = Border(
                top=Side(style='double', color=COLOR_WARNING_RED) if r == 21 else None,
                bottom=Side(style='double', color=COLOR_WARNING_RED) if r == 25 else None,
                left=Side(style='medium', color=COLOR_WARNING_RED) if c == 2 else None,
                right=Side(style='medium', color=COLOR_WARNING_RED) if c == 8 else None
            )

    # Charred crumbling ash ordered dither on Row 26 (cols 2..8)
    for c in range(2, 9):
        ash_cell = ws.cell(row=26, column=c)
        if c in (2, 8):
            ash_cell.fill = fill_carbon
        else:
            ash_cell.fill = fill_blood if c % 2 == 0 else fill_carbon

    # 9. Right Wing Top Header (K2:AN3) — Sub-Basement Blueprint Telemetry Banner
    ws.merge_cells("K2:AN2")
    ws["K2"] = "  MISKATONIC ANNEX — SUB-BASEMENT STRUCTURAL TELEMETRY & DOSSIER WING"
    ws["K2"].font = Font(name="Courier New", size=12, bold=True, color=COLOR_BONE_PAPER)
    ws["K2"].alignment = Alignment(horizontal="left", vertical="center")
    for c in range(11, 41):
        cell = ws.cell(row=2, column=c)
        cell.fill = fill_blood
        cell.border = Border(
            top=Side(style='medium', color=COLOR_WARNING_RED),
            bottom=Side(style='double', color=COLOR_WARNING_RED),
            left=Side(style='medium', color=COLOR_WARNING_RED) if c == 11 else None,
            right=Side(style='medium', color=COLOR_WARNING_RED) if c == 40 else None
        )

    # 10. Yellow Handover Note (K4:U16) + Cast Drop Shadow (V) & Occult Altar Triptych (W3:AN16)
    ws.merge_cells("K4:U16")
    note_cell = ws["K4"]
    note_cell.value = (
        "[📎 MISKATONIC ANNEX ARCHIVE — NIGHT MEMO]\n"
        "═══════════════════════════════════════════════\n"
        "--- NIGHT AUDITOR HANDOVER NOTE ---\n"
        "Date: Oct 31, 1928 (All Hallows' Eve)\n"
        "Shift: 11:00 PM - 07:00 AM | Station: Desk 04\n"
        "═══════════════════════════════════════════════\n\n"
        "RULE 1: Delinquent Borrowing Verification\n"
        "Verify all delinquent borrowings. Any record\n"
        "overdue > 100 days must have its late penalty\n"
        "calculated in Column H ($0.05 per overdue day)\n"
        "to lift the red flag.\n\n"
        "RULE 2: Basement Floorplan Surveillance\n"
        "If Annex Basement floorplan radar displays\n"
        "spatial anomalies (#ROT!), spray chemical\n"
        "reagent to expose it: [CLICK: SPRAY REAGENT]\n\n"
        "RULE 3: Sealing & Vault Breach Protocol\n"
        "In case of structural breach, transcribe the\n"
        "4-word sealing code into Cell B18. Note:\n"
        "the cipher strip on the desk is ROT-3:\n"
        "  CIPHER: 'VHDO WKH GHHS YDXOW' (ROT-3)\n\n"
        "───────────────────────────────────────────────\n"
        "🩸 WARNING: Never alter or inspect Row 13.\n"
        "- Former Auditor Ward (Missing since Oct 30)"
    )
    note_cell.font = font_note
    note_cell.fill = fill_note
    note_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    for r in range(4, 17):
        for c in range(11, 22):
            cell = ws.cell(row=r, column=c)
            cell.fill = fill_note
            cell.border = Border(
                top=Side(style='double', color=COLOR_DRIED_BLOOD) if r == 4 else None,
                bottom=Side(style='medium', color=COLOR_CARBON) if r == 16 else None,
                left=Side(style='medium', color=COLOR_CARBON) if c == 11 else None,
                right=Side(style='medium', color=COLOR_CARBON) if c == 21 else None,
            )

    # Physical Drop-Shadow with 50% Bayer ordered dithering (Column V & Row 17)
    for r in range(5, 18):
        cell = ws.cell(row=r, column=22)
        cell.fill = fill_blood if (r + 22) % 2 == 0 else fill_carbon
    for c in range(12, 23):
        cell = ws.cell(row=17, column=c)
        cell.fill = fill_blood if (17 + c) % 2 == 0 else fill_carbon
    # Chamfered dog-eared corner on outer shadow edge (Row 17, Col 22)
    ws.cell(row=17, column=22).fill = fill_carbon

    # 10b. Right Wing Occult Altar Triptych (W3:AN16) — True 1:1 Square Pixel Art
    # Top plaque for 1928 Halloween Occult Relic Shelf (Row 3, Cols 23..40)
    ws.merge_cells("W3:AN3")
    altar_header = ws["W3"]
    altar_header.value = "  [ 🕯️ 1928 OCCULT ALTAR: KEROSENE CANDLE  |  💀 MEMENTO MORI  |  🎃 JACK-O'-LANTERN ]"
    altar_header.font = Font(name="Courier New", size=8.5, bold=True, color=COLOR_BONE_PAPER)
    altar_header.alignment = Alignment(horizontal="center", vertical="center")
    altar_header.fill = fill_blood
    for c in range(23, 41):
        cell = ws.cell(row=3, column=c)
        cell.fill = fill_blood
        cell.border = Border(
            top=Side(style='medium', color=COLOR_WARNING_RED),
            bottom=Side(style='double', color=COLOR_WARNING_RED),
            left=Side(style='medium', color=COLOR_WARNING_RED) if c == 23 else None,
            right=Side(style='medium', color=COLOR_WARNING_RED) if c == 40 else None,
        )

    # Render all 3 pixel-art sprites side-by-side onto square columns W..AN (Rows 4..12)
    # Sprite 1: 1928 Dripping Kerosene Candle (W4:AA12, cols 23..27)
    render_pixel_sprite(ws, start_row=4, start_col=23, sprite_map=SPRITE_CANDLE, char_fill_map=char_fill_map)

    # Spacing divider column AB (col 28)
    for r in range(4, 13):
        ws.cell(row=r, column=28).fill = fill_carbon

    # Sprite 2: Occult Memento Mori Skull (AC4:AH12, cols 29..34)
    render_pixel_sprite(ws, start_row=4, start_col=29, sprite_map=SPRITE_SKULL, char_fill_map=char_fill_map)

    # Spacing divider column AI (col 35)
    for r in range(4, 13):
        ws.cell(row=r, column=35).fill = fill_carbon

    # Sprite 3: Halloween Jack-o'-Lantern Pumpkin (AJ4:AN12, cols 36..40)
    render_pixel_sprite(ws, start_row=4, start_col=36, sprite_map=SPRITE_PUMPKIN, char_fill_map=char_fill_map)

    # 10c. Right Wing Dossier Card: Arkham Police & Sanatorium Incident Evidence Box (W13:AN16)
    ws.merge_cells("W13:AN16")
    dossier_cell = ws["W13"]
    dossier_cell.value = (
        "╔══ [ 🕯️ ARKHAM POLICE & SANATORIUM — INCIDENT EVIDENCE ] ══╗\n"
        "║ EVIDENCE VAULT CASE #1928-XI: MIDNIGHT AUDIT DISAVOWED    ║\n"
        "║ CONFISCATED RELICS PINNED TO OCCULT ALTAR (ROWS 4-12):    ║\n"
        "║   • 1928 SANATORIUM KEROSENE LAMP (DRIPPING BONE WAX)     ║\n"
        "║   • OCCULT MEMENTO MORI SKULL (GLOWING PHOSPHOR OCULAR)   ║\n"
        "║   • ALL HALLOWS' JACK-O'-LANTERN (CARVED CORNER CUTS)     ║\n"
        "║                                                           ║\n"
        "║ FORENSIC DIRECTIVE: PRIOR TO EMERGENCY VAULT SEAL (B18),  ║\n"
        "║ DEPRESS [ SPRAY REAGENT ] TO EXPOSE BASEMENT TELEMETRY.   ║\n"
        "╚═══════════════════════════════════════════════════════════╝"
    )
    dossier_cell.font = Font(name="Courier New", size=8.5, bold=False, color=COLOR_BONE_PAPER)
    dossier_cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    dossier_cell.fill = fill_blood
    for r in range(13, 17):
        for c in range(23, 41):
            cell = ws.cell(row=r, column=c)
            cell.fill = fill_blood
            cell.border = Border(
                top=Side(style='double', color=COLOR_WARNING_RED) if r == 13 else None,
                bottom=Side(style='double', color=COLOR_WARNING_RED) if r == 16 else None,
                left=Side(style='medium', color=COLOR_WARNING_RED) if c == 23 else None,
                right=Side(style='medium', color=COLOR_WARNING_RED) if c == 40 else None,
            )

    # Row 17 buffer under dossier
    for c in range(23, 41):
        ws.cell(row=17, column=c).fill = fill_carbon

    # 11. Phase 2 Button: [ SPRAY REAGENT ] (K18:AN18)
    ws.merge_cells("K18:AN18")
    spray_btn = ws["K18"]
    spray_btn.value = "[ SPRAY REAGENT ]"
    spray_btn.font = Font(name="Courier New", size=10.5, bold=True, color=COLOR_BONE_PAPER)
    spray_btn.fill = fill_spray
    spray_btn.alignment = Alignment(horizontal="center", vertical="center")
    for c in range(11, 41):
        cell = ws.cell(row=18, column=c)
        cell.fill = fill_spray
        cell.border = Border(
            top=Side(style='medium', color=COLOR_BONE_PAPER),
            bottom=Side(style='medium', color=COLOR_CARBON),
            left=Side(style='medium', color=COLOR_BONE_PAPER) if c == 11 else None,
            right=Side(style='medium', color=COLOR_CARBON) if c == 40 else None
        )

    # 12. 30x30 Radar Grid (K20:AN49)
    ws.merge_cells("K19:AN19")
    radar_title = ws["K19"]
    radar_title.value = "ANNEX BASEMENT PLAN RADAR (30x30) — CORRUPTED"
    radar_title.font = Font(name="Courier New", size=11, bold=True, color=COLOR_WARNING_RED)
    radar_title.alignment = Alignment(horizontal="center", vertical="center")
    for c in range(11, 41):
        rc = ws.cell(row=19, column=c)
        rc.fill = fill_decay
        rc.border = Border(
            top=Side(style='medium', color=COLOR_CARBON),
            bottom=Side(style='double', color=COLOR_CARBON),
            left=Side(style='medium', color=COLOR_CARBON) if c == 11 else None,
            right=Side(style='medium', color=COLOR_CARBON) if c == 40 else None
        )

    glitch_tokens = ["#ROT!", "#REF!", "#N/A", "??", "[VOID]", "#ERR!"]
    for r in range(20, 50):
        ws.row_dimensions[r].height = 14
        for c in range(11, 41):
            cell = ws.cell(row=r, column=c)
            token = glitch_tokens[(r * 7 + c * 13) % len(glitch_tokens)]
            cell.value = token

            # Ghostly 30x30 eldritch horned skull & eye silhouette in corrupted radar watermark
            r_idx = r - 20
            c_idx = c - 11
            dr = r_idx - 14
            dc = c_idx - 14
            dist_sq = dr * dr + dc * dc

            is_horn = (r_idx < 10) and ((c_idx == r_idx or c_idx == (29 - r_idx)) or (abs(c_idx - 8) <= 1 and r_idx < 8) or (abs(c_idx - 21) <= 1 and r_idx < 8))
            is_socket = (12 <= r_idx <= 17 and 10 <= c_idx <= 15)
            is_pupil = (14 <= r_idx <= 15 and 12 <= c_idx <= 13)
            is_mouth = (20 <= r_idx <= 22 and 10 <= c_idx <= 19)
            is_outer_skull = (120 <= dist_sq <= 170)

            if is_pupil:
                # Black cosmic pupil core
                cell.fill = fill_abyss
                cell.font = Font(name="Courier New", size=8, bold=True, color=COLOR_WARNING_RED)
            elif is_socket:
                # Faint glowing eye socket
                cell.fill = fill_blood
                cell.font = Font(name="Courier New", size=8, bold=True, color=COLOR_PHOSPHOR_GREEN)
            elif is_mouth or is_horn:
                # Blood-stained mouth and curving occult horns
                cell.fill = fill_blood
                cell.font = Font(name="Courier New", size=8, bold=True, color=COLOR_WARNING_RED)
            elif is_outer_skull:
                # 50% ordered Bayer dither along skull perimeter
                cell.fill = fill_blood if (r + c) % 2 == 0 else fill_decay
                cell.font = Font(name="Courier New", size=8, color=COLOR_CARBON)
            elif dist_sq < 120:
                # Cranium interior with organic shadow
                if dist_sq <= 30:
                    cell.fill = fill_blood if (r + c) % 2 == 0 else fill_decay
                    cell.font = Font(name="Courier New", size=8, bold=True, color=COLOR_WARNING_RED)
                else:
                    cell.fill = fill_decay
                    cell.font = Font(name="Courier New", size=8, color=COLOR_CARBON)
            else:
                # Outer radar coordinate field with 50% Bayer ordered dither
                cell.fill = fill_decay if (r + c) % 2 == 0 else fill_bone
                cell.font = Font(name="Courier New", size=8, color=COLOR_HOSPITAL_GREEN)

            cell.border = Border(
                top=Side(style='medium', color=COLOR_CARBON) if r == 20 else Side(style='thin', color=COLOR_HOSPITAL_GREEN),
                bottom=Side(style='medium', color=COLOR_CARBON) if r == 49 else Side(style='thin', color=COLOR_HOSPITAL_GREEN),
                left=Side(style='medium', color=COLOR_CARBON) if c == 11 else Side(style='thin', color=COLOR_HOSPITAL_GREEN),
                right=Side(style='medium', color=COLOR_CARBON) if c == 40 else Side(style='thin', color=COLOR_HOSPITAL_GREEN)
            )
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # 13. Lower Left Desk Canvas Artifacts (Columns B..H / Rows 28..50)
    # Typed 1928 Archival Incident Dossier & Autopsy Log (replaces stretched wide pixel sprites)
    ws.merge_cells("B28:H48")
    autopsy_cell = ws["B28"]
    autopsy_cell.value = (
        "╔════ [ ARKHAM POLICE & SANATORIUM — INCIDENT DOSSIER & AUTOPSY LOG ] ════╗\n"
        "║ CASE FILE #1928-10-31 | CLASSIFICATION: CUSTODIAL CORPSE DISPOSITION    ║\n"
        "║ SUBJECT: NIGHT AUDITOR WARD (DECEASED / RETRIEVED FROM ANNEX SUB-VAULT)  ║\n"
        "╠═════════════════════════════════════════════════════════════════════════╣\n"
        "║ CORONER AUTOPSY OBSERVATIONS (DR. M. PEASLEE, ARKHAM CORONER):          ║\n"
        "║   1. Rigor mortis absent; tissues necrotic with black viscous ichor.    ║\n"
        "║   2. Epigastric cavity punctured; floorboard splinters embedded deep.   ║\n"
        "║   3. Cranial sutures fractured along non-Euclidean logarithmic spirals. ║\n"
        "║   4. Retinal tissue bioluminescent with phosphor green fungal spore.    ║\n"
        "║                                                                         ║\n"
        "║ PROPERTY RECOVERED FROM DECEASED'S AUDIT STATION:                       ║\n"
        "║   [x] Charred ROT-3 cipher strip ('VHDO WKH GHHS YDXOW' -> shift back 3)║\n"
        "║   [x] Annex sub-basement telemetry blueprint (spatial anomaly at K20)   ║\n"
        "║   [x] Chemical reagent bottle (Formaldehyde / Phosphor green solution)  ║\n"
        "║                                                                         ║\n"
        "║ CUSTODIAL DIRECTIVE FOR REPLACEMENT AUDITOR:                            ║\n"
        "║   • DO NOT TOUCH OR INSPECT ROW 13. HE SLEEPS BENEATH THE FLOORBOARDS.  ║\n"
        "║   • CALCULATE OVERDUE PENALTY FOR RECORD ARK-007 (WILBUR WHATELEY).     ║\n"
        "║   • SPRAY REAGENT ON RADAR GRID (K20:AN49) TO UNCOVER VAULT ANOMALIES.  ║\n"
        "║   • TRANSCRIBE SEALING CODE TO B18 AND ENGAGE [ SEAL ARCHIVE ] CUSTODY. ║\n"
        "╚═════════════════════════════════════════════════════════════════════════╝"
    )
    autopsy_cell.font = Font(name="Courier New", size=8.5, bold=False, color=COLOR_BONE_PAPER)
    autopsy_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    autopsy_cell.fill = fill_blood
    for r in range(28, 49):
        for c in range(2, 9):
            tc = ws.cell(row=r, column=c)
            tc.fill = fill_blood
            tc.border = Border(
                top=Side(style='double', color=COLOR_WARNING_RED) if r == 28 else None,
                bottom=Side(style='double', color=COLOR_WARNING_RED) if r == 48 else None,
                left=Side(style='medium', color=COLOR_WARNING_RED) if c == 2 else None,
                right=Side(style='medium', color=COLOR_WARNING_RED) if c == 8 else None,
            )

    # Charred ash dither on Row 49 (cols 2..8)
    for c in range(2, 9):
        ash_cell = ws.cell(row=49, column=c)
        if c in (2, 8):
            ash_cell.fill = fill_carbon
        else:
            ash_cell.fill = fill_blood if c % 2 == 0 else fill_carbon

    # Anchored Lower Desk Artifact Plaque (B50:H50)
    ws.row_dimensions[50].height = 20
    ws.merge_cells("B50:H50")
    relic_label = ws["B50"]
    relic_label.value = "[ 📁 ARKHAM SANATORIUM AUTOPSY DOSSIER  |  CONFIDENTIAL EVIDENCE FILE #1928-XI ]"
    relic_label.font = Font(name="Courier New", size=8.5, bold=True, color=COLOR_BONE_PAPER)
    relic_label.alignment = Alignment(horizontal="center", vertical="center")
    relic_label.fill = fill_blood
    for c in range(2, 9):
        cell = ws.cell(row=50, column=c)
        cell.fill = fill_blood
        cell.border = Border(
            top=Side(style='thin', color=COLOR_WARNING_RED),
            bottom=Side(style='double', color=COLOR_WARNING_RED),
            left=Side(style='medium', color=COLOR_WARNING_RED) if c == 2 else None,
            right=Side(style='medium', color=COLOR_WARNING_RED) if c == 8 else None,
        )

    # Column widths
    col_widths = {
        1: 16,  # A: Record ID / Override Label
        2: 18,  # B: Borrower Name
        3: 21,  # C: Department
        4: 25,  # D: Tome Title
        5: 12,  # E: Checkout Date
        6: 12,  # F: Due Date
        7: 13,  # G: Overdue Days
        8: 18,  # H: Late Fee Paid
        9: 18,  # I: Status
        10: 3,  # J: Desk Gutter Spacer
    }
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # Radar & right wing columns K to AN (11 to 40) square aspect ratio
    for col_idx in range(11, 41):
        ws.column_dimensions[get_column_letter(col_idx)].width = 3.5

    # Right desk margin columns AO to AZ (41 to 52)
    for col_idx in range(41, 53):
        ws.column_dimensions[get_column_letter(col_idx)].width = 3.5

    wb.save(output_path)
    return wb

if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.dirname(__file__)), TEMPLATE_FILENAME)
    build_ledger_workbook(output)
    print(f"Successfully generated {output}")

