import os
import pytest
import openpyxl
from scripts.build_ledger import build_ledger_workbook, TEMPLATE_FILENAME

def test_build_ledger_generates_file():
    output_path = "tests/test_output_ledger.xlsx"
    if os.path.exists(output_path):
        os.remove(output_path)

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
    assert ws["H7"].value is None

    # Verify Handover note exists & Halloween enhancements
    assert "NIGHT AUDITOR HANDOVER NOTE" in ws["K4"].value
    assert "[📎 MISKATONIC ANNEX ARCHIVE — NIGHT MEMO]" in ws["K4"].value
    assert "Date: Oct 31, 1928 (All Hallows' Eve)" in ws["K4"].value
    assert "HALLOWEEN MIDNIGHT CUSTODIAL AUDIT" in ws["A3"].value
    assert "RULE 1" in ws["K4"].value
    assert "RULE 2" in ws["K4"].value
    assert "RULE 3" in ws["K4"].value

    # Verify 30x30 Radar grid exists at K20:AN49
    assert ws["K20"].value is not None
    assert ws["AN49"].value is not None
    assert ws["K19"].value is not None
    assert "RADAR" in ws["K19"].value

    # Verify Interactive Button Cells
    assert ws["C18"].value == "[ SEAL ARCHIVE ]"
    assert ws["K18"].value == "[ SPRAY REAGENT ]"

    # Cleanup
    if os.path.exists(output_path):
        os.remove(output_path)
