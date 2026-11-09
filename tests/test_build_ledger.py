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

    # Verify Interactive Button Cells & A18/B18 styling
    assert ws["A18"].value == "EMERGENCY OVERRIDE CODE (PHASE 3):"
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
    assert "SANATORIUM KEROSENE LAMP" in ws["W13"].value
    assert "CHARRED CIPHER KEY STRIP" in ws["B21"].value
    assert "CUSTODIAL WAX SEAL" in ws["E18"].value
    assert "OCCULT ALTAR" in ws["W3"].value

    # Verify Pixel-Art Enhancements: 3D Bevels, Ordered Dithering, and Fine-Grid Sprites
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

    # 2. 50% Bayer Ordered Dithering on Drop-Shadow & Charred Ash Strip
    assert ws["V6"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]
    assert ws["V7"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["V17"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]  # Chamfered corner
    assert ws["C26"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["D26"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]

    # 3. Fine-Grid Pixel Art Sprites in True Square-Pixel Grid (W4:AN12)
    # Sprite 1: 1928 Halloween Kerosene Candle in W4:AA12 (Flame core at Y5, terminates above Row 13 Abyss void)
    assert ws["Y5"].fill.start_color.rgb in ["003B533E", "FF3B533E", "3B533E"]
    assert ws["Y4"].fill.start_color.rgb in ["008A1C14", "FF8A1C14", "8A1C14"]
    assert ws["AB8"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]  # Clean desk canvas divider
    assert ws["W13"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]  # Blood fill on dossier card
    # Sprite 2: Occult Memento Mori Skull in AC4:AH12 (Pupils at AE8 & AF8, socket void at AD8)
    assert ws["AE8"].fill.start_color.rgb in ["003B533E", "FF3B533E", "3B533E"]
    assert ws["AF8"].fill.start_color.rgb in ["003B533E", "FF3B533E", "3B533E"]
    assert ws["AD8"].fill.start_color.rgb in ["00000000", "FF000000", "000000"]
    # Sprite 3: Halloween Jack-o'-Lantern Pumpkin in AJ4:AN12 (Stem at AM4, carved cut at AK7, vibrant orange at AL11)
    assert ws["AM4"].fill.start_color.rgb in ["00454F48", "FF454F48", "454F48"]
    assert ws["AK7"].fill.start_color.rgb in ["003B533E", "FF3B533E", "3B533E"]
    assert ws["AL11"].fill.start_color.rgb in ["00D9681A", "FFD9681A", "D9681A"]
    assert ws["AK11"].fill.start_color.rgb in ["008A1C14", "FF8A1C14", "8A1C14"]  # High-contrast crimson outline

    # Verify Clean Margins & Desk Gutter Spacer (Col A, Col J, and Margin Col AO remain clean carbon desk canvas)
    assert ws["A31"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["J31"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["J43"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws["AO10"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]  # Pumpkin contained within AJ..AN
    assert ws["AO11"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]

    # Anchored Lower Desk Artifact Plaque at B50:H50 (Official Coroner Autopsy Evidence)
    assert "AUTOPSY DOSSIER" in ws["B50"].value
    assert ws["B50"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]

    # 4. Verify Radar Grid Integrity (Radar cells in Column K are untouched by sprites)
    glitch_tokens = ["#ROT!", "#REF!", "#N/A", "??", "[VOID]", "#ERR!"]
    assert ws["K27"].value in glitch_tokens
    assert ws["K39"].value in glitch_tokens

    # 5. Verify Radar Ghostly Watermark (cosmic pupil, socket, and occult horns)
    assert ws["W34"].fill.start_color.rgb in ["00000000", "FF000000", "000000"]
    assert ws["W32"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]
    assert ws["L21"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]

    # 6. Verify 16-Bit High-Density Micro-Pixel Art Sanctum (Option B: Rows 51..80, Columns K..BC)
    assert "16-BIT HIGH-DENSITY" in ws["K51"].value
    assert ws["K51"].fill.start_color.rgb in ["002E0F0D", "FF2E0F0D", "2E0F0D"]
    assert "16-BIT FORENSIC ATLAS" in ws["K80"].value
    assert ws["K80"].fill.start_color.rgb in ["00181614", "FF181614", "181614"]
    assert ws.row_dimensions[52].height == 12
    # Verify fine-grid column width across K..BC
    assert ws.column_dimensions["K"].width == 2.2
    assert ws.column_dimensions["BC"].width == 2.2
    # 16-bit candle flame core at P55 (col 16 is P)
    assert ws["P55"].fill.start_color.rgb in ["00E5D982", "FFE5D982", "E5D982"]
    # 16-bit skull glowing phosphor pupil at AA63 (col 27 is AA)
    assert ws["AA63"].fill.start_color.rgb in ["003B533E", "FF3B533E", "3B533E"]
    # 16-bit pumpkin candlelight eye at AP62 (col 42 is AP) and orange rind at AR62 (col 44 is AR)
    assert ws["AP62"].fill.start_color.rgb in ["00E5D982", "FFE5D982", "E5D982"]
    assert ws["AR62"].fill.start_color.rgb in ["00D9681A", "FFD9681A", "D9681A"]

    # Cleanup
    if os.path.exists(output_path):
        os.remove(output_path)
