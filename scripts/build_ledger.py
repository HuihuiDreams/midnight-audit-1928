#!/usr/bin/env python3
"""
The Midnight Audit (1928) — Ledger Builder Script
Generates the pre-formatted Morbid Archive template with 1928 visual styling,
Row 13 Abyss (220pt height), yellow handover notes, and 30x30 corrupted radar grid.
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

def build_ledger_workbook(output_path: str = TEMPLATE_FILENAME) -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = "Audit_Ledger_1928"
    ws.views.sheetView[0].showGridLines = True

    # Styling helpers
    font_title = Font(name="Courier New", size=15, bold=True, color=COLOR_CARBON)
    font_subtitle = Font(name="Courier New", size=10, italic=True, color=COLOR_HOSPITAL_GREEN)
    font_header = Font(name="Courier New", size=11, bold=True, color=COLOR_CARBON)
    font_body = Font(name="Courier New", size=10, bold=False, color=COLOR_CARBON)
    font_flagged = Font(name="Courier New", size=10, bold=True, color=COLOR_WARNING_RED)
    font_hidden = Font(name="Courier New", size=14, bold=True, color=COLOR_ABYSS)
    font_censored = Font(name="Courier New", size=10, bold=False, color=COLOR_ABYSS)
    font_note = Font(name="Courier New", size=10, bold=False, color=COLOR_CARBON)

    fill_bone = PatternFill(fill_type="solid", start_color=COLOR_BONE_PAPER, end_color=COLOR_BONE_PAPER)
    fill_decay = PatternFill(fill_type="solid", start_color=COLOR_DECAYING_PAPER, end_color=COLOR_DECAYING_PAPER)
    fill_abyss = PatternFill(fill_type="solid", start_color=COLOR_ABYSS, end_color=COLOR_ABYSS)
    fill_note = PatternFill(fill_type="solid", start_color=COLOR_YELLOW_NOTE, end_color=COLOR_YELLOW_NOTE)

    thin_border = Border(
        left=Side(style='thin', color=COLOR_HOSPITAL_GREEN),
        right=Side(style='thin', color=COLOR_HOSPITAL_GREEN),
        top=Side(style='thin', color=COLOR_HOSPITAL_GREEN),
        bottom=Side(style='thin', color=COLOR_HOSPITAL_GREEN)
    )

    thick_note_border = Border(
        left=Side(style='medium', color=COLOR_CARBON),
        right=Side(style='medium', color=COLOR_CARBON),
        top=Side(style='medium', color=COLOR_CARBON),
        bottom=Side(style='medium', color=COLOR_CARBON)
    )

    # 1. Document Title Banners
    ws.merge_cells("A2:I2")
    ws["A2"] = "MISKATONIC UNIVERSITY — ANNEX ARCHIVE DELINQUENCY LEDGER"
    ws["A2"].font = font_title
    ws["A2"].alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[2].height = 24

    ws.merge_cells("A3:I3")
    ws["A3"] = "FISCAL PERIOD: OCTOBER 1928 | HALLOWEEN MIDNIGHT CUSTODIAL AUDIT | ALL BALANCES SUBJECT TO CUSTODIAL SEAL"
    ws["A3"].font = font_subtitle
    ws["A3"].alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[3].height = 18

    for r in (2, 3):
        for c in range(1, 10):
            cell = ws.cell(row=r, column=c)
            cell.fill = fill_bone
            cell.border = thin_border

    # 2. Table Column Headers
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
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[5].height = 26

    # 3. Active Borrower Records (Rows 6-12)
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
        ws.row_dimensions[i].height = 20
        for j, val in enumerate(row_data, start=1):
            cell = ws.cell(row=i, column=j, value=val)
            cell.font = font_body
            cell.fill = fill_bone
            cell.border = thin_border
            
            # Format currency & numbers
            if j == 7: # Overdue Days
                cell.alignment = Alignment(horizontal="right", vertical="center")
            elif j == 8: # Fee
                cell.alignment = Alignment(horizontal="right", vertical="center")
                if val is not None:
                    cell.number_format = "$#,##0.00"
            elif j == 9: # Status
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if val == "FLAGGED":
                    cell.font = font_flagged

    # 4. Row 13: The Abyss (Height = 220)
    ws.row_dimensions[13].height = 220
    for col_idx in range(1, 10):
        cell = ws.cell(row=13, column=col_idx)
        cell.fill = fill_abyss
        cell.border = thin_border

    ws.merge_cells("A13:I13")
    ws["A13"] = "STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"
    ws["A13"].font = font_hidden
    ws["A13"].alignment = Alignment(horizontal="center", vertical="center")

    # 5. Censored Rows (Rows 14-16)
    censored_records = [
        ("ARK-066", "[EXPUNGED BY ORDER]", "Dunwich Vault", "The Seven Cryptical Books", "1928-01-01", "1928-01-13", 273, None, "COORDINATE: RADAR GRID K20:AN49"),
        ("ARK-067", "[NAME MUTATED]", "Kadath Sub-basement", "Pnakotic Manuscripts", "1927-10-31", "1927-11-13", 345, None, "ACCESS DENIED"),
        ("ARK-068", "Keziah Mason", "Arkham Witch House", "Azathoth & Other Horrors", "1692-05-01", "1692-05-19", 86320, None, "REMAINS UNBURIED"),
    ]
    for i, row_data in enumerate(censored_records, start=14):
        ws.row_dimensions[i].height = 18
        for j, val in enumerate(row_data, start=1):
            cell = ws.cell(row=i, column=j, value=val)
            cell.font = font_censored
            cell.fill = fill_abyss
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="left", vertical="center")

    # 6. Row 18: Emergency Vault Override Input
    ws.row_dimensions[18].height = 28
    ws["A18"] = "EMERGENCY OVERRIDE CODE (PHASE 3):"
    ws["A18"].font = font_header
    ws["A18"].fill = fill_decay
    ws["A18"].border = thin_border
    ws["A18"].alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    
    ws["B18"].font = Font(name="Courier New", size=11, bold=True, color=COLOR_CARBON)
    ws["B18"].fill = fill_bone
    ws["B18"].border = Border(
        left=Side(style='medium', color=COLOR_DRIED_BLOOD),
        right=Side(style='medium', color=COLOR_DRIED_BLOOD),
        top=Side(style='medium', color=COLOR_DRIED_BLOOD),
        bottom=Side(style='medium', color=COLOR_DRIED_BLOOD)
    )
    ws["B18"].alignment = Alignment(horizontal="center", vertical="center")

    # Phase 4 Button: [ SEAL ARCHIVE ] (C18:D18)
    ws.merge_cells("C18:D18")
    seal_btn = ws["C18"]
    seal_btn.value = "[ SEAL ARCHIVE ]"
    seal_btn.font = Font(name="Courier New", size=10, bold=True, color=COLOR_DECAYING_PAPER)
    fill_seal = PatternFill(fill_type="solid", start_color=COLOR_HOSPITAL_GREEN, end_color=COLOR_HOSPITAL_GREEN)
    seal_btn.fill = fill_seal
    seal_btn.alignment = Alignment(horizontal="center", vertical="center")
    for c in range(3, 5):
        cell = ws.cell(row=18, column=c)
        cell.fill = fill_seal
        cell.border = thin_border

    # Row 18 trailer (E18:I18)
    for c in range(5, 10):
        cell = ws.cell(row=18, column=c)
        cell.fill = fill_bone
        cell.border = thin_border

    # 7. Yellow Handover Note (Post-It across full radar width K4:AN16)
    ws.merge_cells("K4:AN16")
    note_cell = ws["K4"]
    note_cell.value = (
        "[📎 MISKATONIC ANNEX ARCHIVE — NIGHT MEMO]\n"
        "--- NIGHT AUDITOR HANDOVER NOTE ---\n"
        "Date: Oct 31, 1928 (All Hallows' Eve) | Shift: 11:00 PM - 07:00 AM\n\n"
        "RULE 1: Verify all delinquent borrowings. Any record overdue by > 100 days must have its late penalty calculated in Column H ($0.05 per overdue day) to lift the red flag.\n\n"
        "RULE 2: If the Annex Basement floorplan radar displays spatial anomalies (#ROT!), spray the chemical reagent [CLICK: SPRAY REAGENT] to expose the intruder.\n\n"
        "RULE 3: In case of structural breach, transcribe the 4-word sealing code into Cell B18. Note: the cipher strip on the desk is shifted by 3 letters:\n"
        "  CIPHER: 'VHDO WKH GHHS YDXOW' (ROT-3)\n\n"
        "WARNING: Under no circumstances alter or inspect Row 13.\n"
        "- Former Auditor Ward (Missing since yesterday)"
    )
    note_cell.font = font_note
    note_cell.fill = fill_note
    note_cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    
    for r in range(4, 17):
        for c in range(11, 41):
            cell = ws.cell(row=r, column=c)
            cell.fill = fill_note
            cell.border = Border(
                top=Side(style='medium', color=COLOR_CARBON) if r == 4 else None,
                bottom=Side(style='medium', color=COLOR_CARBON) if r == 16 else None,
                left=Side(style='medium', color=COLOR_CARBON) if c == 11 else None,
                right=Side(style='medium', color=COLOR_CARBON) if c == 40 else None,
            )

    # Phase 2 Button: [ SPRAY REAGENT ] (K18:AN18)
    ws.merge_cells("K18:AN18")
    spray_btn = ws["K18"]
    spray_btn.value = "[ SPRAY REAGENT ]"
    spray_btn.font = Font(name="Courier New", size=10, bold=True, color=COLOR_BONE_PAPER)
    fill_spray = PatternFill(fill_type="solid", start_color=COLOR_PHOSPHOR_GREEN, end_color=COLOR_PHOSPHOR_GREEN)
    spray_btn.fill = fill_spray
    spray_btn.alignment = Alignment(horizontal="center", vertical="center")
    for c in range(11, 41):
        cell = ws.cell(row=18, column=c)
        cell.fill = fill_spray
        cell.border = thin_border

    # 8. 30x30 Radar Grid (K20:AN49)
    ws.merge_cells("K19:AN19")
    radar_title = ws["K19"]
    radar_title.value = "ANNEX BASEMENT PLAN RADAR (30x30) — CORRUPTED"
    radar_title.font = font_header
    radar_title.alignment = Alignment(horizontal="center", vertical="center")

    glitch_tokens = ["#ROT!", "#REF!", "#N/A", "??", "[VOID]", "#ERR!"]
    for r in range(20, 50):
        ws.row_dimensions[r].height = 14
        for c in range(11, 41):
            cell = ws.cell(row=r, column=c)
            token = glitch_tokens[(r * 7 + c * 13) % len(glitch_tokens)]
            cell.value = token
            cell.font = Font(name="Courier New", size=8, color=COLOR_HOSPITAL_GREEN)
            cell.fill = fill_decay if (r + c) % 2 == 0 else fill_bone
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # Column widths
    col_widths = {
        1: 20, # A: Record ID / Override Label
        2: 24, # B: Borrower Name
        3: 26, # C: Department
        4: 32, # D: Tome Title
        5: 15, # E: Checkout Date
        6: 15, # F: Due Date
        7: 15, # G: Overdue Days
        8: 20, # H: Late Fee Paid
        9: 24, # I: Status
        10: 4, # J: Spacer
    }
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # Radar columns K to AN (11 to 40) square aspect ratio
    for col_idx in range(11, 41):
        ws.column_dimensions[get_column_letter(col_idx)].width = 4.0

    wb.save(output_path)
    return wb

if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.dirname(__file__)), TEMPLATE_FILENAME)
    build_ledger_workbook(output)
    print(f"Successfully generated {output}")
