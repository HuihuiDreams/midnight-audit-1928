import os
import zipfile
from datetime import date, timedelta

import openpyxl
from scripts.build_ledger import build_ledger_workbook, TEMPLATE_FILENAME

def test_build_ledger_generates_file(tmp_path):
    output_path = str(tmp_path / "test_output_ledger.xlsx")

    wb = build_ledger_workbook(output_path)
    assert os.path.exists(output_path)
    
    # Reload and inspect
    loaded_wb = openpyxl.load_workbook(output_path)
    assert "Audit_Ledger_1928" in loaded_wb.sheetnames
    ws = loaded_wb["Audit_Ledger_1928"]

    # Verify Row 13 Abyss
    assert ws.row_dimensions[13].height == 220
    row13_fill = ws["A13"].fill.start_color.rgb
    # Openpyxl hex can be '00000000' or 'FF000000' or '000000'
    assert row13_fill in ["00000000", "FF000000", "000000"]
    assert "STOP AUDITING ROW 13" in ws["A13"].value
    assert ws["A13"].font.name == "Courier New"
    assert ws["A13"].font.color.rgb in ["00000000", "FF000000", "000000"]

    # Verify Wilbur Whateley in Row 7
    assert ws["B7"].value == "Wilbur Whateley"
    assert ws["G7"].value == 140
    assert ws["H7"].value == "[ TYPE FEE ]"
    assert ws["H7"].number_format == "$#,##0.00"

    # Verify Handover note exists & Halloween enhancements (Full-width K4:AN12)
    assert "NIGHT AUDITOR HANDOVER NOTE" in ws["K4"].value
    assert "MISKATONIC ANNEX ARCHIVE" in ws["K4"].value
    assert "Date: Oct 31, 1928 (All Hallows' Eve)" in ws["K4"].value
    assert "HALLOWEEN MIDNIGHT CUSTODIAL AUDIT" in ws["A3"].value
    assert "RULE 1" in ws["K4"].value
    assert "RULE 2" in ws["K4"].value
    assert "RULE 3" in ws["K4"].value
    # The midnight clock's late interest is announced in Ward's own hand, without spoilers
    assert "Each wrong entry costs a minute. Seal it before midnight." in ws["K4"].value
    assert "K4:AN12" in [str(r) for r in ws.merged_cells.ranges]
    assert "K13:AN16" in [str(r) for r in ws.merged_cells.ranges]

    # Verify 1928 Retro Horror Typography Hierarchy
    assert ws["A2"].font.name == "Copperplate"
    assert ws["K2"].font.name == "Copperplate"
    assert ws["K19"].font.name == "Copperplate"
    assert ws["A3"].font.name == "Baskerville"
    assert ws["A5"].font.name == "Copperplate"
    assert ws["K4"].font.name == "Bradley Hand"
    assert ws["K13"].font.name == "American Typewriter"
    assert ws["B30"].font.name == "American Typewriter"
    assert ws["A13"].font.name == "Courier New"
    assert ws["B21"].font.name == "Courier New"

    # Verify 30x30 Radar grid exists at K20:AN49
    assert ws["K20"].value is not None
    assert ws["AN49"].value is not None
    assert ws["K19"].value is not None
    assert "RADAR" in ws["K19"].value

    # Verify Interactive Button Cells & A18/B18 dormant Phase 1 styling
    assert "EMERGENCY OVERRIDE" in ws["A18"].value
    assert ws["A18"].fill.start_color.rgb in ["00C5BFA8", "FFC5BFA8", "C5BFA8"]
    assert ws["A18"].border.left.style == "thin"
    assert ws["B18"].value == "[ LOCKED ]"
    assert ws["B18"].fill.start_color.rgb in ["00C5BFA8", "FFC5BFA8", "C5BFA8"]
    assert ws["C18"].value == "[ SEAL ARCHIVE ]"
    assert ws["K18"].value == "[ SPRAY REAGENT ]"

    # Verify 1928 Retro & Halloween Horror Atmosphere Enhancements
    assert ws.views.sheetView[0].showGridLines is False
    # Full-bleed dark desk canvas (eliminating raw white Excel background)
    assert ws["J1"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["A30"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    # Engraved inverted masthead banner
    assert ws["A2"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["A2"].font.color.rgb in ["00D3CEB9", "FFD3CEB9", "D3CEB9"]
    # Accounting double-red vertical audit lines on Column H
    assert ws["H6"].border.left.style == "double"
    assert ws["H7"].border.left.style == "double"
    # Pinned Lamp Label & Charred Cipher Key Strip artifacts
    assert "SANATORIUM KEROSENE LAMP" in ws["K13"].value
    assert "CHARRED CIPHER KEY STRIP" in ws["B21"].value
    assert "VHDO WKH GHHS YDXOW" in ws["B21"].value
    assert "CUSTODIAL WAX SEAL" in ws["E18"].value
    assert "1/4:" in ws["E18"].value
    assert "OCCULT ALTAR" in ws["K3"].value

    # Verify spoiler-free & coordinate-independent diegetic guidance
    for doc_cell in ("K4", "K13", "B30"):
        doc_text = ws[doc_cell].value
        assert "$7.00" not in doc_text
        assert "[x]" not in doc_text
        for hidden_ref in ("Cell H7", "Cell B18", "K20:AN49", "C18:D18"):
            assert hidden_ref not in doc_text
    assert "K20:AN49" not in ws["I14"].value
    assert "Excel" not in ws["K13"].value and "Ctrl+Shift" not in ws["K13"].value  # 1928 artifact, no modern UI

    # Verify Dormant Phase 1 Buttons & Custodial Wax Seal borders
    # 1. Dormant dark buttons until unlocked by phase progression, with seamless composite borders
    assert ws["C18"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["C18"].font.color.rgb in ["008A8D8F", "FF8A8D8F", "8A8D8F"]
    assert ws["C18"].border.top.color.rgb in ["00454F48", "FF454F48", "454F48"]
    assert ws["K18"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["K18"].font.color.rgb in ["008A8D8F", "FF8A8D8F", "8A8D8F"]
    assert ws["K18"].border.top.color.rgb in ["00454F48", "FF454F48", "454F48"]
    assert ws["E18"].border.top.style == "double"
    assert ws["E18"].border.top.color.rgb in ["008A1C14", "FF8A1C14", "8A1C14"]
    # Verify seamless composite borders without internal green dividing lines
    assert (ws.cell(row=18, column=12).border.left is None or ws.cell(row=18, column=12).border.left.style is None)
    assert (ws.cell(row=18, column=6).border.left is None or ws.cell(row=18, column=6).border.left.style is None)

    # 2. Ordered Dithering on Charred Ash Strips
    assert ws["C29"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["D29"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]
    assert ws["C49"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["D49"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]

    # 3. Special Collections Card in K13:AN16 (absorbing Row 13 height across full 30-col width)
    assert ws["K13"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]
    assert ws["K3"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]

    # Verify Clean Margins & Desk Gutter Spacer (Columns A and J remain carbon desk canvas)
    assert ws["A31"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["J31"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["J43"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]

    # Lower-Left Memorandum at B30:H48 and Flush Plaques on Row 50
    assert "DR. HENRY ARMITAGE" in ws["B30"].value
    assert ws["B30"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]
    assert "DR. H. ARMITAGE RESTRICTED DIRECTIVE" in ws["B50"].value
    assert ws["B50"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]
    assert "ANNEX SUB-VAULT 13 SANCTUM" in ws["K50"].value
    assert ws["K50"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]
    assert ws.row_dimensions[50].height == 20

    # 4. Verify Radar Grid Integrity (Radar cells in Column K are untouched by sprites)
    glitch_tokens = ["#ROT!", "#REF!", "#N/A", "??", "[VOID]", "#ERR!"]
    assert ws["K27"].value in glitch_tokens
    assert ws["K39"].value in glitch_tokens

    # 5. Verify K20:AN49 30x30 16-Bit Sanctum Coordinates
    assert ws["W34"].fill.start_color.rgb in ["00000000", "FF000000", "000000"]  # abyss pupil
    assert ws["W32"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]  # socket brow
    assert ws["L21"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]  # horn tip
    # Left candle
    assert ws["N30"].fill.start_color.rgb in ["00E5D982", "FFE5D982", "E5D982"]  # flame tip
    assert ws["N31"].fill.start_color.rgb in ["00D9681A", "FFD9681A", "D9681A"]  # orange flame core
    assert ws["M34"].fill.start_color.rgb in ["00D3CEB9", "FFD3CEB9", "D3CEB9"]  # ivory wax
    assert ws["M40"].fill.start_color.rgb in ["00454F48", "FF454F48", "454F48"]  # brass saucer
    # Right pumpkin
    assert ws["AK31"].fill.start_color.rgb in ["00454F48", "FF454F48", "454F48"]  # pumpkin stem
    assert ws["AJ34"].fill.start_color.rgb in ["00E5D982", "FFE5D982", "E5D982"]  # glowing eye left
    assert ws["AL34"].fill.start_color.rgb in ["00E5D982", "FFE5D982", "E5D982"]  # glowing eye right
    assert ws["AK36"].fill.start_color.rgb in ["00D9681A", "FFD9681A", "D9681A"]  # orange rind

    # 6. Verify Unified A1:AN50 Boundary (no bottom-right protrusion)
    assert ws["K51"].value is None
    assert ws["K51"].style_id == 0
    assert ws["AO10"].style_id == 0
    assert ws["AP10"].style_id == 0
    assert ws.column_dimensions["AN"].width == 2.2
    assert ws.column_dimensions["AO"].width != 2.2
    assert ws.column_dimensions["AP"].width != 2.2


def test_build_ledger_archive_contents_are_reproducible(tmp_path):
    first_output = tmp_path / "first.xlsx"
    second_output = tmp_path / "second.xlsx"

    build_ledger_workbook(first_output)
    build_ledger_workbook(second_output)

    with zipfile.ZipFile(first_output) as first_archive, zipfile.ZipFile(second_output) as second_archive:
        first_contents = {name: first_archive.read(name) for name in first_archive.namelist()}
        second_contents = {name: second_archive.read(name) for name in second_archive.namelist()}

    assert first_contents == second_contents

GAME_NIGHT = date(1928, 10, 31)
VISIBLE_ROWS = range(6, 13)
CENSORED_ROWS = range(14, 17)


def _ledger_sheet(tmp_path):
    output_path = str(tmp_path / "ledger.xlsx")
    build_ledger_workbook(output_path)
    return openpyxl.load_workbook(output_path)["Audit_Ledger_1928"]


def test_every_overdue_count_runs_to_the_game_night(tmp_path):
    ws = _ledger_sheet(tmp_path)

    for row in (*VISIBLE_ROWS, *CENSORED_ROWS):
        due = date.fromisoformat(ws.cell(row=row, column=6).value)
        days = ws.cell(row=row, column=7).value
        assert due + timedelta(days=days) == GAME_NIGHT, ws.cell(row=row, column=1).value


def test_every_loan_is_checked_out_before_it_is_due(tmp_path):
    ws = _ledger_sheet(tmp_path)

    for row in (*VISIBLE_ROWS, *CENSORED_ROWS):
        checkout = date.fromisoformat(ws.cell(row=row, column=5).value)
        due = date.fromisoformat(ws.cell(row=row, column=6).value)
        assert checkout < due, ws.cell(row=row, column=1).value


def test_paid_fees_are_five_cents_per_overdue_day(tmp_path):
    ws = _ledger_sheet(tmp_path)

    for row in VISIBLE_ROWS:
        fee = ws.cell(row=row, column=8).value
        if row == 7:
            assert fee == "[ TYPE FEE ]"
        elif fee is not None:
            assert round(ws.cell(row=row, column=7).value * 0.05, 2) == fee, ws.cell(row=row, column=1).value
    assert round(ws["G7"].value * 0.05, 2) == 7.0   # Wilbur's unpaid fee is the Phase 1 answer


def test_only_wilbur_exceeds_the_hundred_day_threshold_of_rule_1(tmp_path):
    ws = _ledger_sheet(tmp_path)

    over_threshold = [ws.cell(row=r, column=1).value for r in VISIBLE_ROWS if ws.cell(row=r, column=7).value > 100]

    assert over_threshold == ["ARK-007"]


def test_sheet_ledger_matches_the_engine_records(tmp_path):
    from src.backend.puzzle_state import PuzzleEngine
    ws = _ledger_sheet(tmp_path)

    for row, record in PuzzleEngine().ledger_data.items():
        assert ws.cell(row=row, column=1).value == record["id"]
        assert ws.cell(row=row, column=2).value == record["borrower"]
        assert ws.cell(row=row, column=7).value == record["overdue"]
        expected_fee = "[ TYPE FEE ]" if record["fee"] is None else record["fee"]
        assert ws.cell(row=row, column=8).value == expected_fee
        assert ws.cell(row=row, column=9).value == record["status"]
