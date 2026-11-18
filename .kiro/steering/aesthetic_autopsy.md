# Aesthetic Autopsy: Morbid Archive Visual & Sensory Specifications

## 1. Aesthetic Vision: The 1928 University Archives Autopsy

The spreadsheet is not an office productivity tool — it is a decaying historical manuscript preserved in formaldehyde and carbon dust. Every visual and sensory cue evokes the quiet dread of late-night archival work at Miskatonic University in October 1928.

---

## 2. Color Palette & RGB Definitions

| Semantic Role | Hex Code | RGB Values | Usage Notes |
| :--- | :--- | :--- | :--- |
| **Moldy Bone Paper** | `#D3CEB9` | `RGB(211, 206, 185)` | Base background for all unlocked archive cells. |
| **Decaying Paper (Shade)** | `#C5BFA8` | `RGB(197, 191, 168)` | Alternating rows and low-frequency breathing cycle. |
| **Typewriter Carbon** | `#181614` | `RGB(24, 22, 20)` | All standard text glyphs. Never use digital `#000000` for readable text. |
| **Hospital Green Grid** | `#454F48` | `RGB(69, 79, 72)` | Hairline thin cell borders (`xlThin`). Sanitized yet claustrophobic. |
| **Dried Blood Scab** | `#2E0F0D` | `RGB(46, 15, 13)` | Error states, ink-spread animations, corrupted data markings. |
| **The Void / Abyss** | `#000000` | `RGB(0, 0, 0)` | Row 13 fill, redacted rows, and deep space entities. |
| **Yellow Post-It Note** | `#E5D982` | `RGB(229, 217, 130)` | Handover notes from the previous missing night auditor. |
| **Warning Red Ink** | `#8A1C14` | `RGB(138, 28, 20)` | Highlighted overdue penalties and urgent warnings. |
| **Phosphor Green Radar** | `#3B533E` | `RGB(59, 83, 62)` | Chemical developer reveal on the 30x30 floorplan radar. |

---

## 3. Typography & Cell Styling

1. **1928 Retro Horror Typography Hierarchy**:
   - **Engraved Mastheads, Stamps, Table Headers & Plaques (`Copperplate`)**: `Copperplate`, 8.5pt–14pt, Bold, Upper Case (used for archive mastheads `A2`, `K2`, `K3`, `K19`, table headers `Row 5`, emergency override label `A18`, action buttons `C18`, `K18`, wax seals `G1`, `E18`, and Row 50 plaques `B50`, `K50`).
   - **Archival Subtitles & Bound Folio Edges (`Baskerville`)**: `Baskerville`, 9.5pt–10pt, Bold / Italic (used for 1928 book-plate subtitles `A3`, protocol strip `A17`, and desk folio binding `A19`).
   - **Frantic Handwritten Handover Note (`Bradley Hand`)**: `Bradley Hand`, 9.5pt, Bold (used for former auditor Ward's organic ink-pen handwritten Yellow Handover Note `K4:AN12`).
   - **Diegetic Typed Memos (`American Typewriter`)**: `American Typewriter`, 9pt–9.5pt, Regular (used for Special Collections Protocol Card `K13:AN16` and Dr. Armitage's Memorandum `B30:H48`).
   - **Tabular Ledger Data, Row 13 Abyss & Cipher Strip (`Courier New`)**: `Courier New`, 9pt–14pt (strict monospace for borrower rows `A6:I12`, Row 13 Abyss `A13` at 14pt Bold, censored rows `A14:I16`, ROT-3 cipher strip `B21:H28`, and radar telemetry tokens).
2. **Alignment & Formatting**:
   - Dates: `YYYY-MM-DD` (e.g., `1928-10-14`).
   - Monetary Amounts: `$#,##0.00` mechanical ledger format (with `#454F48` italic `[ TYPE FEE ]` placeholder on `H7` before entry).
   - Text IDs: Left aligned, padded with leading zeroes (`ARK-0013`).
   - Control Affordances & Live Phase HUD: Dormant controls (`K18:AN18`, `C18:D18`, and locked `B18`) render flat in Carbon Ink (`#181614`) / Decayed Vellum (`#C5BFA8`) with `#8A8D8F` Cold Ash text; active buttons lift with `#D3CEB9` text on a Phosphor Green (`#3B533E`) fill for `[ SPRAY REAGENT ]` and a crimson (`#8A1C14`) fill for `[ SEAL ARCHIVE ]`; `E18:I18` renders a continuous live 1/4–4/4 Custodial Wax Seal banner synchronized with `Application.StatusBar`.
3. **The Stripped UI Protocol**:
   - On opening, standard Excel ribbons, toolbars, headings, formula bar, and default gridlines are suppressed.
   - The document appears floating in a sea of Bone Paper (`#D3CEB9`).
   - To keep zero-context play legible without headings, onboarding relies on in-cell placeholders, automatic Phase 1 cursor focus (`H7`), label-relative clues (no raw cell coordinates or answer spoilers), and dynamic status-bar guidance.

---

## 4. The Row 13 Abyss

- **Row Index**: 13 (A13:I13)
- **Row Height**: `220 pt` (disrupts the neat visual rhythm of the spreadsheet like an open grave). At runtime the grave widens by `14 pt` per in-game minute of the midnight clock (at most `402 pt`, under Excel's `409 pt` limit) and closes back to `220 pt` when the archive is sealed. Row heights are shared by both wings, so the Row 50 baseline stays flush.
- **Background**: `#000000` (Pure Black).
- **Hidden Glyph**: Font color is initially `#000000`. Text: `"STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"`.
- **Interaction**:
  - When the user selects Row 13 or clears Phase 1, the cell text color briefly flashes `#D3CEB9` or inverts.
  - Accompanied by a low-frequency rumble.
- **Midnight Clock**: The `G1` masthead stamp keeps live time from `11:47 PM` in Warning Red on Decaying Paper. In the last 3 minutes the `G1:I1` stamp bleeds to Dried Blood with Bone Paper text. A foreclosed ledger is stamped in Dried Blood with Bone Paper text across `B10:H12`.
- **Camera**: Zoom and scroll moves ease `ThisWorkbook.Windows(1)` over 10 frames (smoothstep). There is a dolly into Row 13 when Phase 1 clears and a lean over the radar during the reagent reveal, which settles on scroll row 14 with `B18`, the cipher strip and the eye in frame.
- **The Gaze**: After the reveal, the 2x2 Dried Blood pupil moves one cell inside the 4x4 Phosphor Green iris `V33:Y36` toward each selected cell. It never leaves the 30x30 canvas or paints over the face outline.

---

## 5. Acoustic Discipline

Silence is the primary instrument of terror:
1. **Default State**: Complete, absolute silence. No background loop, no cheerful chimes.
2. **The Taboo Thud**:
   - Triggered on selecting the forbidden Row 13 or entering invalid ritual phrases.
   - Windows: Win32 `Beep(37, 300)` — a 37 Hz low-frequency vibration that rattles the speaker hardware.
   - macOS: Fallback to silent visual red border flash (`#2E0F0D` outline) and subtle screen tremor.
3. **Thunder Inversion**:
   - On banishing the entity in Phase 4: Full-sheet inverted strobe (5 rapid flashes between white and black) before freezing into cold ash gray.
