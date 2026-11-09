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

    # Verify Handover note exists & Halloween enhancements (Full-width K4:AN12)
    assert "NIGHT AUDITOR HANDOVER NOTE" in ws["K4"].value
    assert "MISKATONIC ANNEX ARCHIVE" in ws["K4"].value
    assert "Date: Oct 31, 1928 (All Hallows' Eve)" in ws["K4"].value
    assert "HALLOWEEN MIDNIGHT CUSTODIAL AUDIT" in ws["A3"].value
    assert "RULE 1" in ws["K4"].value
    assert "RULE 2" in ws["K4"].value
    assert "RULE 3" in ws["K4"].value
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

    # Verify Interactive Button Cells & A18/B18 styling
    assert "EMERGENCY OVERRIDE" in ws["A18"].value
    assert ws["A18"].fill.start_color.rgb in ["00C5BFA8", "FFC5BFA8", "C5BFA8"]
    assert ws["A18"].border.left.style == "thin"
    assert ws["B18"].fill.start_color.rgb in ["00D3CEB9", "FFD3CEB9", "D3CEB9"]
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
    assert "CUSTODIAL WAX SEAL" in ws["E18"].value
    assert "OCCULT ALTAR" in ws["K3"].value

    # Verify Pixel-Art Enhancements: 3D Bevels, Ordered Dithering, and Special Collections Card
    # 1. 3D Bevels on Action Buttons & Custodial Wax Seal
    assert ws["C18"].border.top.color.rgb in ["00D3CEB9", "FFD3CEB9", "D3CEB9"]
    assert ws["C18"].border.bottom.color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["K18"].border.top.color.rgb in ["00D3CEB9", "FFD3CEB9", "D3CEB9"]
    assert ws["K18"].border.bottom.color.rgb in ["00181614", "FF181614", "181614"]
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

    # Verify Clean Margins & Desk Gutter Spacer (Col A, Col J, and Margin Col AO remain clean carbon desk canvas)
    assert ws["A31"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["J31"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["J43"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["AO10"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["AO11"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]

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
    assert ws["K51"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["AO10"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["AP10"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws.column_dimensions["K"].width == 2.2
    assert ws.column_dimensions["AP"].width == 2.2
    assert ws.column_dimensions["BC"].width != 2.2

    # Cleanup
    if os.path.exists(output_path):
        os.remove(output_path)
