from enum import Enum
import re
from typing import Dict, Any, List, Optional

PALETTE = {
    "BONE_PAPER": "#D3CEB9",
    "DECAYING_PAPER": "#C5BFA8",
    "CARBON": "#181614",
    "HOSPITAL_GREEN": "#454F48",
    "DRIED_BLOOD": "#2E0F0D",
    "ABYSS_BLACK": "#000000",
    "YELLOW_NOTE": "#E5D982",
    "WARNING_RED": "#8A1C14",
    "PHOSPHOR_GREEN": "#3B533E",
    "COLD_ASH": "#8A8D8F",
}

class PhaseEnum(str, Enum):
    THE_AUDIT_DISCREPANCY = "THE_AUDIT_DISCREPANCY"
    THE_UNSEEN_INTRUDER = "THE_UNSEEN_INTRUDER"
    HIJACKED_CIPHER = "HIJACKED_CIPHER"
    MIDNIGHT_SETTLEMENT = "MIDNIGHT_SETTLEMENT"

class PuzzleEngine:
    def __init__(self):
        self.current_phase: PhaseEnum = PhaseEnum.THE_AUDIT_DISCREPANCY
        self.row13_awakened: bool = False
        self.intruder_revealed: bool = False
        self.archive_sealed: bool = False
        self.hijack_triggered: bool = False
        self.pending_effects: List[Dict[str, Any]] = []

        # Ledger records: row index -> dict
        self.ledger_data = {
            6: {"id": "ARK-001", "borrower": "Henry Armitage", "tome": "Cultes des Goules", "overdue": 12, "fee": 0.60, "status": "CLEARED"},
            7: {"id": "ARK-007", "borrower": "Wilbur Whateley", "tome": "Necronomicon (Dee Trans.)", "overdue": 140, "fee": None, "status": "FLAGGED"},
            8: {"id": "ARK-012", "borrower": "Francis Morgan", "tome": "Book of Eibon", "overdue": 35, "fee": 1.75, "status": "CLEARED"},
            9: {"id": "ARK-019", "borrower": "Warren Rice", "tome": "De Vermis Mysteriis", "overdue": 80, "fee": 4.00, "status": "CLEARED"},
            10: {"id": "ARK-023", "borrower": "Asenath Waite", "tome": "Unaussprechlichen Kulten", "overdue": 15, "fee": 0.75, "status": "CLEARED"},
            11: {"id": "ARK-031", "borrower": "Pickman, R.U.", "tome": "Ars Magna Lucis et Umbrae", "overdue": 95, "fee": 4.75, "status": "CLEARED"},
            12: {"id": "ARK-040", "borrower": "Edward Derby", "tome": "Liber Ivonis", "overdue": 5, "fee": 0.25, "status": "CLEARED"},
        }

    @property
    def phase_number(self) -> int:
        if self.current_phase == PhaseEnum.THE_AUDIT_DISCREPANCY:
            return 1
        elif self.current_phase == PhaseEnum.THE_UNSEEN_INTRUDER:
            return 2
        elif self.current_phase == PhaseEnum.HIJACKED_CIPHER:
            return 3
        else:
            return 4

    def get_state(self) -> Dict[str, Any]:
        return {
            "phase": self.phase_number,
            "phase_name": self.current_phase.value,
            "row13_awakened": self.row13_awakened,
            "intruder_revealed": self.intruder_revealed,
            "archive_sealed": self.archive_sealed,
            "pending_effects": list(self.pending_effects),
            "records_count": len(self.ledger_data)
        }

    def handle_cell_change(self, cell: str, value: Any) -> Dict[str, Any]:
        cell = str(cell).strip().upper()
        str_val = str(value).strip()

        if self.current_phase == PhaseEnum.THE_AUDIT_DISCREPANCY:
            if cell == "H7":
                # Clean currency symbols while preserving negative sign
                clean_num = re.sub(r"[^\d.-]", "", str_val)
                try:
                    num_val = float(clean_num)
                    expected = 140 * 0.05  # 7.00
                    if abs(num_val - expected) < 0.01:
                        self.ledger_data[7]["fee"] = 7.00
                        self.ledger_data[7]["status"] = "BALANCED (UNHOLY)"
                        self.current_phase = PhaseEnum.THE_UNSEEN_INTRUDER
                        self.row13_awakened = True
                        return {
                            "accepted": True,
                            "current_phase": self.phase_number,
                            "message": "Overdue balance settled. The floorboards moan.",
                            "actions": [
                                {
                                    "command": "SET_VALUE",
                                    "cell": "I7",
                                    "value": "BALANCED (UNHOLY)"
                                },
                                {
                                    "command": "AWAKEN_ROW_13",
                                    "cell": "A13",
                                    "text": "STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"
                                },
                                {
                                    "command": "TRIGGER_FX",
                                    "effect": "THUD_BEEP"
                                },
                                {
                                    "command": "UNLOCK_CENSORED_ROWS",
                                    "rows": [14, 15, 16],
                                    "reveal_text": "ARCHIVE COORDINATE: RADAR GRID K20:AN49"
                                }
                            ]
                        }
                    else:
                        return {
                            "accepted": False,
                            "current_phase": self.phase_number,
                            "message": f"Incorrect fee calculation. Expected 140 days * $0.05 ($7.00), got {str_val}."
                        }
                except ValueError:
                    return {
                        "accepted": False,
                        "current_phase": self.phase_number,
                        "message": "Invalid numeric input in fee column."
                    }

        elif self.current_phase == PhaseEnum.HIJACKED_CIPHER:
            if cell == "B18":
                if not self.hijack_triggered:
                    self.hijack_triggered = True
                    return {
                        "accepted": False,
                        "hijacked": True,
                        "ghost_text": "YOUR SALARY CANNOT SAVE YOU",
                        "actions": [
                            {
                                "command": "HIJACK_TYPE",
                                "cell": "B18",
                                "text": "YOUR SALARY CANNOT SAVE YOU",
                                "duration_ms": 1200
                            },
                            {
                                "command": "TRIGGER_FX",
                                "effect": "THUD_BEEP"
                            }
                        ]
                    }
                else:
                    norm = re.sub(r"\s+", " ", str_val.upper())
                    if norm == "SEAL THE DEEP VAULT":
                        self.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT
                        return {
                            "accepted": True,
                            "hijacked": False,
                            "current_phase": self.phase_number,
                            "message": "Override code accepted. Emergency vault protocol unlocked.",
                            "actions": [
                                {
                                    "command": "UNLOCK_BUTTON",
                                    "button": "SEAL_ARCHIVE",
                                    "color": PALETTE["WARNING_RED"]
                                }
                            ]
                        }
                    else:
                        return {
                            "accepted": False,
                            "hijacked": False,
                            "current_phase": self.phase_number,
                            "message": "Decryption failed. The cipher remains locked."
                        }

        return {
            "accepted": False,
            "current_phase": self.phase_number,
            "message": f"No active trigger for cell {cell} in Phase {self.phase_number}."
        }

    def handle_reagent_spray(self) -> Dict[str, Any]:
        if self.current_phase == PhaseEnum.THE_UNSEEN_INTRUDER:
            self.intruder_revealed = True
            self.current_phase = PhaseEnum.HIJACKED_CIPHER
            return {
                "accepted": True,
                "current_phase": self.phase_number,
                "message": "Reagent sprayed onto Annex Basement floorplan. The anomaly manifests.",
                "actions": [
                    {
                        "command": "RENDER_PIXEL_MATRIX",
                        "target_range": "K20:AN49"
                    },
                    {
                        "command": "START_EYE_BLINK",
                        "cells": ["W34", "X34", "W35", "X35"]
                    },
                    {
                        "command": "TRIGGER_FX",
                        "effect": "THUD_BEEP"
                    }
                ]
            }
        return {
            "accepted": False,
            "current_phase": self.phase_number,
            "message": "Reagent cannot be applied in this phase."
        }

    def get_pixel_radar(self) -> Dict[str, Any]:
        """
        Generates a 30x30 color matrix for K20:AN49.
        Depicts an eldritch face with horns and a glowing central cosmic eye.
        """
        rows, cols = 30, 30
        grid: List[List[str]] = [[PALETTE["BONE_PAPER"] for _ in range(cols)] for _ in range(rows)]

        # Procedurally paint the cosmic demon/eye face
        # Outline and horns (CARBON)
        for r in range(rows):
            for c in range(cols):
                # Center is around r=14, c=14
                dr = r - 14
                dc = c - 14
                dist_sq = dr * dr + dc * dc

                # Outer skull / oval
                if 120 <= dist_sq <= 170:
                    grid[r][c] = PALETTE["CARBON"]
                elif dist_sq < 120:
                    grid[r][c] = PALETTE["DECAYING_PAPER"]

                # Horns curving up from r=6, c=6 and r=6, c=22
                if (r < 10) and ((c == r or c == (29 - r)) or (abs(c - 8) <= 1 and r < 8) or (abs(c - 21) <= 1 and r < 8)):
                    grid[r][c] = PALETTE["CARBON"]

                # Eldritch Mouth (DRIED_BLOOD)
                if 20 <= r <= 22 and 10 <= c <= 19:
                    grid[r][c] = PALETTE["DRIED_BLOOD"]

                # Eye socket (CARBON)
                if 12 <= r <= 17 and 11 <= c <= 18:
                    grid[r][c] = PALETTE["CARBON"]

                # Iris (PHOSPHOR_GREEN)
                if 13 <= r <= 16 and 12 <= c <= 17:
                    grid[r][c] = PALETTE["PHOSPHOR_GREEN"]

                # Pupil (DRIED_BLOOD / VOID)
                if 14 <= r <= 15 and 13 <= c <= 16:
                    grid[r][c] = PALETTE["DRIED_BLOOD"]

        # Blinking eye coordinates in Excel range K20:AN49
        # Center is r=14, 15 -> Row 20 + 14 = Row 34, Row 35
        # Column K is 11. Col 11 + 12 = 23 (W), 24 (X)
        blinking_cells = ["W34", "X34", "W35", "X35"]

        return {
            "rows": rows,
            "cols": cols,
            "start_cell": "K20",
            "end_cell": "AN49",
            "grid": grid,
            "blinking_cells": blinking_cells
        }

    def judge_ritual(self, phrase: str) -> Dict[str, Any]:
        phrase_clean = re.sub(r"\s+", " ", str(phrase).strip().upper())
        valid_phrases = ["SEAL THE DEEP VAULT", "BANISH WILBUR", "BANISH", "MEMENTO MORI", "PH'NGLUI MGLW'NAFH"]

        if phrase_clean in valid_phrases or "SEAL" in phrase_clean:
            self.archive_sealed = True
            self.current_phase = PhaseEnum.MIDNIGHT_SETTLEMENT
            return {
                "banished": True,
                "stamp": "[ ARCHIVE SEALED - OCTOBER 14, 1928 - 00:01 AM ]",
                "message": "THE ENTRY IS BALANCED. CLOCK OUT AND NEVER RETURN.",
                "actions": [
                    {
                        "command": "TRIGGER_FX",
                        "effect": "THUNDER_STROBE"
                    },
                    {
                        "command": "TRIGGER_FX",
                        "effect": "SCREEN_TREMOR"
                    },
                    {
                        "command": "LOCK_SHEET",
                        "color": PALETTE["COLD_ASH"],
                        "stamp_range": "B10:H12"
                    }
                ]
            }
        else:
            return {
                "banished": False,
                "message": "MISMATCHED DEBIT. YOUR RITUAL VOID ACCRUES BLOOD DEBT.",
                "actions": [
                    {
                        "command": "TRIGGER_FX",
                        "effect": "THUD_BEEP"
                    }
                ]
            }

    def queue_haunt(self, haunt_type: str, target_cell: Optional[str] = None, message: Optional[str] = None):
        self.pending_effects.append({
            "type": haunt_type,
            "target_cell": target_cell,
            "message": message
        })

    def pop_pending_effects(self) -> List[Dict[str, Any]]:
        effects = list(self.pending_effects)
        self.pending_effects.clear()
        return effects
