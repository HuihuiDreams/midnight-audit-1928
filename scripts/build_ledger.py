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
# 30x30 16-Bit Pixel Art Matrix (Scheme B: All Hallows' Candlelit Sanctum)
# Rendered inside Primary Visible Viewport onto Square-Pixel Radar (K20:AN49)
# ==============================================================================
RADAR_16BIT_SANCTUM = [
    "#####DDDDDDDD####DDDDDDDD#####",  # 00 (Row 20): Gothic Crypt Arch Header
    "#D..#D#...#DD....DD#...#D#..D#",  # 01 (Row 21): Sweeping Horn tips (L21 at r=1,c=1 is D)
    "#...,.#D#.#DD....DD#.#D#.,...#",  # 02 (Row 22): Sweeping outer & inner demon horns
    "#.....,.#D#DD,,,,DD#D#.,.....#",  # 03 (Row 23): Horn curve & skull crown highlight
    "#......,.#DDD....DDD#.,......#",  # 04 (Row 24): Cranial dome top
    "#.......#DD..DDDD..DD#.......#",  # 05 (Row 25): Forehead blood scarification
    "#......,#D...DRRD...D#,......#",  # 06 (Row 26): Frontal bone & ritual blood mark
    "#.....,#D....DRRD....D#,.....#",  # 07 (Row 27): Upper brow
    "#DDDDD#D..............D#DDDDD#",  # 08 (Row 28): Dark crypt alcove arches left & right
    "#DXXXD#D..............D#DXXXD#",  # 09 (Row 29): Deep shadow alcoves for candle & pumpkin
    "#DXYXD#D,,,........,,,D#DXXXD#",  # 10 (Row 30): Left flame tip (Y at N30) | Heavy brow ridge
    "#DYOYD#DDDDD,,..,,DDDDD#DXGXD#",  # 11 (Row 31): Candle flame (YOY) | Brow | Pumpkin stem (G at AK31)
    "#DYYYD#DDDDDDD..DDDDDDD#DGGGD#",  # 12 (Row 32): White-hot flame | Socket brow (W32 is D) | Stem base
    "#DXXXD#DDDDPPPPDDPPPPDD#ROOOR#",  # 13 (Row 33): Candle wick | Phosphor Iris | Pumpkin crown
    "#D...D#DDDDPXXPDDPXXPDD#OYOYO#",  # 14 (Row 34): Ivory candle wax | W34:X35 (XX) | 2 Pumpkin Eyes (AJ34, AL34)
    "#D.,..#DDDDPXXPDDPXXPDD#OYOYO#",  # 15 (Row 35): Melting wax drip | W34:X35 (XX) | Pumpkin Eyes
    "#D...D#DDDDPPPPDDPPPPDD#OOOOO#",  # 16 (Row 36): Candle wax shaft | Lower Iris | Pumpkin bridge (AK36 is O)
    "#D.,..#DDDDDDDXXDDDDDDD#OOYOO#",  # 17 (Row 37): Candle wax shaft | Nasal apex | Carved nose (Y)
    "#D...D.,#DDDDXXXXDDDD#,#OOOOO#",  # 18 (Row 38): Candle shaft | Nasal cavity | Upper lip
    "#DGGGD..,#DDDXXXXDDD#,.#OYOYO#",  # 19 (Row 39): Brass candle cup | Maxilla | Jagged grin
    "#GGGGGG..#D........D#..#OYYYO#",  # 20 (Row 40): Brass saucer tray | Upper jaw | Blazing mouth
    "##GGGG#..#D.X.XX.X.D#..#ROOOR#",  # 21 (Row 41): Saucer handle | Skull teeth | Lower pumpkin
    "#DXXXXD..#DXXXXXXXXD#..#DXXXD#",  # 22 (Row 42): Candle shadow | Void mouth | Pumpkin shadow
    "#DDDDDD..#D.X.XX.X.D#..#DDDDD#",  # 23 (Row 43): Plinth top | Lower teeth | Plinth top
    "#########,#DDDDDDDD#,#########",  # 24 (Row 44): Stone Altar Ledge & mandible
    "#####DDDDDDD#R..R#DDDDDDD#####",  # 25 (Row 45): Blood drips & stone altar plinth
    "#G,,#.......#R..R#.......#,,G#",  # 26 (Row 46): Crypt base pillars
    "#,,,#........#RR#........#,,,#",  # 27 (Row 47): Pooled blood
    "#G,,#....................#,,G#",  # 28 (Row 48): Crypt floor
    "#####GGGGGGGGGGGGGGGGGGGG#####",  # 29 (Row 49): Crypt south wall
]

def build_ledger_workbook(output_path: str = TEMPLATE_FILENAME) -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = "Audit_Ledger_1928"
    # Hide raw Excel gridlines so the sheet reads as a 1928 archival artifact, not a modern spreadsheet
    ws.views.sheetView[0].showGridLines = False
    ws.views.sheetView[0].zoomScale = 85
    ws.sheet_view.zoomScale = 85

    # Retro Horror Typography Hierarchy (1928 New England Gothic & Archival Typewriter)
    FONT_DISPLAY = "Copperplate"          # Engraved stone/brass plaques, titles, stamps & buttons
    FONT_SERIF = "Baskerville"            # 1928 New England book-plate headers & formal labels
    FONT_TYPEWRITER = "American Typewriter"  # Authentic uneven ribbon typewriter for desk memos & notes
    FONT_MONO = "Courier New"             # Strict monospace for ledger numbers, Row 13 Abyss & ROT-3 cipher
    FONT_HANDWRITTEN = "Bradley Hand"     # Organic hasty handwriting for Ward's handover note

    # Styling helpers
    font_stamp = Font(name=FONT_DISPLAY, size=9.5, bold=True, color=COLOR_WARNING_RED)
    font_title = Font(name=FONT_DISPLAY, size=14, bold=True, color=COLOR_BONE_PAPER)
    font_subtitle = Font(name=FONT_SERIF, size=10, italic=True, color=COLOR_CARBON)
    font_header = Font(name=FONT_DISPLAY, size=9.5, bold=True, color=COLOR_CARBON)
    font_body = Font(name=FONT_MONO, size=10, bold=False, color=COLOR_CARBON)
    font_flagged = Font(name=FONT_MONO, size=10, bold=True, color=COLOR_WARNING_RED)
    font_hidden = Font(name=FONT_MONO, size=14, bold=True, color=COLOR_ABYSS)
    font_censored = Font(name=FONT_MONO, size=10, bold=False, color=COLOR_ABYSS)
    font_note = Font(name=FONT_HANDWRITTEN, size=9.5, bold=True, color=COLOR_CARBON)
    font_seal = Font(name=FONT_DISPLAY, size=9, bold=True, color=COLOR_WARNING_RED)
    font_desk_footer = Font(name=FONT_SERIF, size=9.5, italic=True, color=COLOR_HOSPITAL_GREEN)

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

    # 0. Full-Bleed Desk Canvas Backdrop (Rows 1..52, Cols 1..42)
    # Eliminates all raw modern Excel white background cells around and below the ledger
    for r in range(1, 53):
        ws.row_dimensions[r].height = 18
        for c in range(1, 43):
            ws.cell(row=r, column=c).fill = fill_carbon

    # Outer Parchment Folio Margin (A1:I19)
    for r in range(1, 20):
        for c in range(1, 10):
            ws.cell(row=r, column=c).fill = fill_decay

    # 1. Row 1: 1928 Archival Classification & Blood-Wax Stamp Header
    ws.row_dimensions[1].height = 20
    ws.merge_cells("A1:F1")
    ws["A1"] = "  FORM MU-1928-VIII  |  RESTRICTED CUSTODIAL LEDGER  |  ARKHAM, MASS."
    ws["A1"].font = Font(name=FONT_DISPLAY, size=9, bold=True, color=COLOR_CARBON)
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
        ws.row_dimensions[i].height = 25
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
                cell.font = Font(name=FONT_MONO, size=10, bold=True, color=COLOR_CARBON)
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
    ws["A17"].font = Font(name=FONT_SERIF, size=9, italic=True, color=COLOR_HOSPITAL_GREEN)
    ws["A17"].alignment = Alignment(horizontal="left", vertical="center")
    for c in range(1, 10):
        ws.cell(row=17, column=c).fill = fill_decay
        ws.cell(row=17, column=c).border = thin_border

    # 7. Row 18: Emergency Vault Override Input & Wax Seal Stamp
    ws.row_dimensions[18].height = 34
    ws["A18"] = "EMERGENCY OVERRIDE\nCODE (PHASE 3):"
    ws["A18"].font = Font(name=FONT_DISPLAY, size=8.5, bold=True, color=COLOR_CARBON)
    ws["A18"].fill = fill_decay
    ws["A18"].border = thin_border
    ws["A18"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws["B18"].font = Font(name=FONT_MONO, size=11, bold=True, color=COLOR_CARBON)
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
    seal_btn.font = Font(name=FONT_DISPLAY, size=10, bold=True, color=COLOR_DECAYING_PAPER)
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

    # 8. Desk Artifact Below Ledger (B21:H28) — Torn 1928 Field Note / Charred ROT-3 Strip
    ws.merge_cells("B21:H28")
    telegram_cell = ws["B21"]
    telegram_cell.value = (
        "╔═══ [ POCKET FIELD ARTIFACT — CHARRED CIPHER KEY STRIP ] ═══════════════════╗\n"
        "║  FOUND ON DESK OF MISSING AUDITOR WARD (OCT 30, 1928 — 11:59 PM):          ║\n"
        "║  STANDARD ALPHABET :  A B C D E F G H I J K L M N O P Q R S T U V W X Y Z  ║\n"
        "║  DESK STRIP (ROT-3):  D E F G H I J K L M N O P Q R S T U V W X Y Z A B C  ║\n"
        "║  \"When the floorboards groan, shift three steps back from the abyss...\"    ║\n"
        "╚════════════════════════════════════════════════════════════════════════════╝"
    )
    telegram_cell.font = Font(name=FONT_MONO, size=9, bold=False, color=COLOR_BONE_PAPER)
    telegram_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    for r in range(21, 29):
        for c in range(2, 9):
            tc = ws.cell(row=r, column=c)
            tc.fill = fill_blood
            tc.border = Border(
                top=Side(style='double', color=COLOR_WARNING_RED) if r == 21 else None,
                bottom=Side(style='double', color=COLOR_WARNING_RED) if r == 28 else None,
                left=Side(style='medium', color=COLOR_WARNING_RED) if c == 2 else None,
                right=Side(style='medium', color=COLOR_WARNING_RED) if c == 8 else None
            )

    # Charred crumbling ash ordered dither on Row 29 (cols 2..8)
    for c in range(2, 9):
        ash_cell = ws.cell(row=29, column=c)
        if c in (2, 8):
            ash_cell.fill = fill_carbon
        else:
            ash_cell.fill = fill_blood if c % 2 == 0 else fill_carbon

    # 9. Right Wing Top Header (K2:AN3) — Sub-Basement Blueprint Telemetry Banner
    ws.merge_cells("K2:AN2")
    ws["K2"] = "  MISKATONIC ANNEX — SUB-BASEMENT STRUCTURAL TELEMETRY & DOSSIER WING"
    ws["K2"].font = Font(name=FONT_DISPLAY, size=12, bold=True, color=COLOR_BONE_PAPER)
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

    # 9b. Right Wing Sub-Banner (K3:AN3)
    ws.merge_cells("K3:AN3")
    altar_header = ws["K3"]
    altar_header.value = "  [ 🕯️ 1928 OCCULT ALTAR & SPECIAL COLLECTIONS — HANDOVER & REAGENT PROTOCOL ]"
    altar_header.font = Font(name=FONT_DISPLAY, size=9, bold=True, color=COLOR_BONE_PAPER)
    altar_header.alignment = Alignment(horizontal="center", vertical="center")
    altar_header.fill = fill_blood
    for c in range(11, 41):
        cell = ws.cell(row=3, column=c)
        cell.fill = fill_blood
        cell.border = Border(
            top=Side(style='medium', color=COLOR_WARNING_RED),
            bottom=Side(style='double', color=COLOR_WARNING_RED),
            left=Side(style='medium', color=COLOR_WARNING_RED) if c == 11 else None,
            right=Side(style='medium', color=COLOR_WARNING_RED) if c == 40 else None,
        )

    # 10. Full-Width Yellow Handover Note (K4:AN12, 30 columns wide x 9 rows tall)
    ws.merge_cells("K4:AN12")
    note_cell = ws["K4"]
    note_cell.value = (
        "  [📎 MISKATONIC ANNEX ARCHIVE — NIGHT AUDITOR HANDOVER NOTE]\n"
        "  Date: Oct 31, 1928 (All Hallows' Eve)  |  Station: Desk 04\n"
        "  ─────────────────────────────────────────────────────────\n"
        "  • RULE 1 (Delinquent Audit): Verify overdue borrowings (>100d).\n"
        "    Enter late fee ($0.05/day) in Column H to clear red flag.\n"
        "  • RULE 2 (Basement Surveillance): If radar (K20:AN49) displays\n"
        "    spatial anomalies (#ROT!), spray reagent: [ SPRAY REAGENT ].\n"
        "  • RULE 3 (Vault Sealing): Decode desk ROT-3 strip into Cell B18:\n"
        "    'VHDO WKH GHHS YDXOW' -> click [ SEAL ARCHIVE ] button.\n"
        "  ─────────────────────────────────────────────────────────\n"
        "  🩸 WARNING: Never alter or inspect Row 13.\n"
        "     — Former Auditor Ward (Missing since Oct 30, 11:59 PM)"
    )
    note_cell.font = font_note
    note_cell.fill = fill_note
    note_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    for r in range(4, 13):
        for c in range(11, 41):
            cell = ws.cell(row=r, column=c)
            cell.fill = fill_note
            cell.border = Border(
                top=Side(style='double', color=COLOR_DRIED_BLOOD) if r == 4 else None,
                bottom=Side(style='medium', color=COLOR_CARBON) if r == 12 else None,
                left=Side(style='medium', color=COLOR_CARBON) if c == 11 else None,
                right=Side(style='medium', color=COLOR_CARBON) if c == 40 else None,
            )

    # 10c. Full-Width Special Collections Night Protocol Card (K13:AN16 — 30 cols wide x 277pt tall)
    ws.merge_cells("K13:AN16")
    dossier_cell = ws["K13"]
    dossier_cell.value = (
        "  🕯️ [ MISKATONIC SPECIAL COLLECTIONS — NIGHT PROTOCOL & REAGENT APPARATUS ]\n"
        "  ARCHIVE DIRECTIVE #1928-X  |  AUTHORITY: DR. H. ARMITAGE  |  STATION: SUB-VAULT 13\n"
        "  ─────────────────────────────────────────────────────────────────────────────────────────\n"
        "  I. OVERDUE CUSTODY LOCK (BORROWER: WHATELEY, WILBUR / RECORD ARK-007)\n"
        "     • Tome: Necronomicon (John Dee Translation, Restricted Vault Folio)\n"
        "     • Status: 140 Days Delinquent — Calculate & enter $7.00 penalty in Cell H7.\n\n"
        "  II. SANATORIUM KEROSENE LAMP & IBN-GHAZI REAGENT ATOMIZER\n"
        "     • Brass reagent atomizer pressurized with glowing phosphor developer mist.\n"
        "     • Depress [ SPRAY REAGENT ] below to expose the unseen entity in Grid K20:AN49.\n\n"
        "  III. MIDNIGHT VAULT SEALING (MANDATORY PRIOR TO 12:00 AM STROKE)\n"
        "     • Decode missing Auditor Ward's charred ROT-3 strip ('VHDO WKH GHHS YDXOW').\n"
        "     • Enter the 4-word banishment phrase into Cell B18 and click [ SEAL ARCHIVE ]."
    )
    dossier_cell.font = Font(name=FONT_TYPEWRITER, size=9.5, bold=False, color=COLOR_BONE_PAPER)
    dossier_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    dossier_cell.fill = fill_blood
    for r in range(13, 17):
        for c in range(11, 41):
            cell = ws.cell(row=r, column=c)
            cell.fill = fill_blood
            cell.border = Border(
                top=Side(style='double', color=COLOR_WARNING_RED) if r == 13 else None,
                bottom=Side(style='double', color=COLOR_WARNING_RED) if r == 16 else None,
                left=Side(style='medium', color=COLOR_WARNING_RED) if c == 11 else None,
                right=Side(style='medium', color=COLOR_WARNING_RED) if c == 40 else None,
            )

    # Row 17 buffer under protocol card (K17:AN17)
    for c in range(11, 41):
        ws.cell(row=17, column=c).fill = fill_carbon

    # 11. Phase 2 Button: [ SPRAY REAGENT ] (K18:AN18)
    ws.merge_cells("K18:AN18")
    spray_btn = ws["K18"]
    spray_btn.value = "[ SPRAY REAGENT ]"
    spray_btn.font = Font(name=FONT_DISPLAY, size=11, bold=True, color=COLOR_BONE_PAPER)
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
    radar_title.font = Font(name=FONT_DISPLAY, size=11, bold=True, color=COLOR_WARNING_RED)
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
    char_to_fill = {
        "#": fill_carbon,
        "G": fill_hospital,
        "D": fill_blood,
        "X": fill_abyss,
        "Y": fill_note,
        "R": fill_red,
        "P": fill_spray,
        "O": fill_pumpkin,
        ",": fill_decay,
    }

    for r in range(20, 50):
        ws.row_dimensions[r].height = 12
        r_idx = r - 20
        row_str = RADAR_16BIT_SANCTUM[r_idx]
        for c in range(11, 41):
            cell = ws.cell(row=r, column=c)
            c_idx = c - 11
            char = row_str[c_idx]

            if char == ".":
                if 1 <= c_idx <= 5 and 14 <= r_idx <= 18:
                    cell.fill = fill_bone
                else:
                    cell.fill = fill_decay if (r + c) % 2 == 0 else fill_bone
            else:
                cell.fill = char_to_fill.get(char, fill_carbon)

            if c_idx in (0, 29) or (r_idx >= 26 and c_idx in range(5, 12)):
                cell.value = glitch_tokens[(r * 7 + c * 13) % len(glitch_tokens)]
                cell.font = Font(name=FONT_MONO, size=7, color=COLOR_HOSPITAL_GREEN)
            else:
                cell.value = None

            cell.border = Border(
                top=Side(style='medium', color=COLOR_CARBON) if r == 20 else Side(style='thin', color=COLOR_HOSPITAL_GREEN),
                bottom=Side(style='medium', color=COLOR_CARBON) if r == 49 else Side(style='thin', color=COLOR_HOSPITAL_GREEN),
                left=Side(style='medium', color=COLOR_CARBON) if c == 11 else Side(style='thin', color=COLOR_HOSPITAL_GREEN),
                right=Side(style='medium', color=COLOR_CARBON) if c == 40 else Side(style='thin', color=COLOR_HOSPITAL_GREEN)
            )
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # 13. Lower Left Desk Canvas Artifacts (Columns B..H / Rows 30..50)
    # Dr. Henry Armitage's Restricted Archival Memorandum
    ws.merge_cells("B30:H48")
    armitage_cell = ws["B30"]
    armitage_cell.value = (
        "  📜 [ MISKATONIC UNIVERSITY LIBRARY — RESTRICTED ARCHIVAL MEMORANDUM ]\n"
        "  MEMORANDUM #1928-10-31  |  FROM: DR. HENRY ARMITAGE, CHIEF LIBRARIAN\n"
        "  TO: NIGHT SHIFT AUDITOR (DESK 04)  |  SUBJECT: SUB-VAULT 13 ANOMALIES\n"
        "  ─────────────────────────────────────────────────────────────────────────────────────────\n"
        "  ARCHIVAL INCIDENT LOG (ALL HALLOWS' EVE — OCTOBER 31, 1928):\n"
        "    1. Following Wilbur Whateley's nocturnal trespass, the campus watchdogs have\n"
        "       barked incessantly at the reinforced floorboards beneath Row 13.\n"
        "    2. Night Auditor Ward vanished from Desk 04 at 11:59 PM last evening, leaving\n"
        "       only a charred ROT-3 cipher strip and an unsealed delinquency ledger.\n"
        "    3. A pungent odour of ozonized tar and formaldehyde seeps through the sub-basement\n"
        "       stone joints; the timber beams exhibit non-Euclidean structural warping.\n\n"
        "  CUSTODIAL INSTRUCTIONS FOR TONIGHT'S SHIFT:\n"
        "    [x] Step 1: Audit Row 7 (Whateley, W. — 140 days overdue @ $0.05/day -> $7.00 in H7).\n"
        "    [x] Step 2: Discharge Ibn-Ghazi reagent ([ SPRAY REAGENT ]) over the 30x30\n"
        "                sub-basement floorplan (K20:AN49) to expose the entity's eye.\n"
        "    [x] Step 3: Shift 'VHDO WKH GHHS YDXOW' three letters back -> enter in Cell B18.\n"
        "    [x] Step 4: Depress [ SEAL ARCHIVE ] (C18:D18) prior to the stroke of midnight."
    )
    armitage_cell.font = Font(name=FONT_TYPEWRITER, size=9, bold=False, color=COLOR_BONE_PAPER)
    armitage_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    armitage_cell.fill = fill_blood
    for r in range(30, 49):
        for c in range(2, 9):
            tc = ws.cell(row=r, column=c)
            tc.fill = fill_blood
            tc.border = Border(
                top=Side(style='double', color=COLOR_WARNING_RED) if r == 30 else None,
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
    relic_label.value = "  📜 ARCHIVAL FOLIO #1928-31B  |  DR. H. ARMITAGE RESTRICTED DIRECTIVE  |  VAULT SEAL REQUIRED"
    relic_label.font = Font(name=FONT_DISPLAY, size=9, bold=True, color=COLOR_BONE_PAPER)
    relic_label.alignment = Alignment(horizontal="center", vertical="center")
    relic_label.fill = fill_blood
    for c in range(2, 9):
        cell = ws.cell(row=50, column=c)
        cell.fill = fill_blood
        cell.border = Border(
            top=Side(style='double', color=COLOR_WARNING_RED),
            bottom=Side(style='double', color=COLOR_WARNING_RED),
            left=Side(style='medium', color=COLOR_WARNING_RED) if c == 2 else None,
            right=Side(style='medium', color=COLOR_WARNING_RED) if c == 8 else None,
        )

    # Flush Right Wing Plaque (K50:AN50)
    ws.merge_cells("K50:AN50")
    k50_cell = ws["K50"]
    k50_cell.value = "🕯️ ANNEX SUB-VAULT 13 SANCTUM | EPICENTER W34:X35"
    k50_cell.font = Font(name=FONT_DISPLAY, size=8, bold=True, color=COLOR_BONE_PAPER)
    k50_cell.alignment = Alignment(horizontal="center", vertical="center")
    k50_cell.fill = fill_blood
    for c in range(11, 41):
        cell = ws.cell(row=50, column=c)
        cell.fill = fill_blood
        cell.border = Border(
            top=Side(style='double', color=COLOR_WARNING_RED),
            bottom=Side(style='double', color=COLOR_WARNING_RED),
            left=Side(style='medium', color=COLOR_WARNING_RED) if c == 11 else None,
            right=Side(style='medium', color=COLOR_WARNING_RED) if c == 40 else None,
        )

    # Column widths
    col_widths = {
        1: 21,  # A: Record ID / Override Label (generous width for EMERGENCY OVERRIDE)
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

    # Radar & right wing columns K to AP (11 to 42) square aspect ratio (fine micro-grid)
    for col_idx in range(11, 43):
        ws.column_dimensions[get_column_letter(col_idx)].width = 2.2

    wb.save(output_path)
    return wb

if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.dirname(__file__)), TEMPLATE_FILENAME)
    build_ledger_workbook(output)
    print(f"Successfully generated {output}")

