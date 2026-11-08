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

1. **Font Family**: `Courier New` exclusively across all cells, headers, and dialogue boxes.
   - Headers: `Courier New`, 11pt, Bold, Upper Case.
   - Body Data: `Courier New`, 10pt, Regular.
   - Warning Notes: `Courier New`, 9pt, Italic.
   - Row 13 Abyss: `Courier New`, 14pt, Bold.
2. **Alignment & Formatting**:
   - Dates: `YYYY-MM-DD` (e.g., `1928-10-14`).
   - Monetary Amounts: `$#,##0.00` mechanical ledger format.
   - Text IDs: Left aligned, padded with leading zeroes (`ARK-0013`).
3. **The Stripped UI Protocol**:
   - On opening, standard Excel ribbons, toolbars, headings, formula bar, and default gridlines are suppressed.
   - The document appears floating in a sea of Bone Paper (`#D3CEB9`).

---

## 4. The Row 13 Abyss

- **Row Index**: 13 (A13:I13)
- **Row Height**: `220 pt` (disrupts the neat visual rhythm of the spreadsheet like an open grave).
- **Background**: `#000000` (Pure Black).
- **Hidden Glyph**: Font color is initially `#000000`. Text: `"STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"`.
- **Interaction**:
  - When the user selects Row 13 or clears Phase 1, the cell text color briefly flashes `#D3CEB9` or inverts.
  - Accompanied by a low-frequency rumble.

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
