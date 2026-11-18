"""
Midnight clock, abyss growth, camera moves and the entity's gaze (VBA client).

VBA cannot run under pytest. These tests pin the source text and check the tuning arithmetic
(deadline length, row height ceiling, iris geometry against the shared face matrix);
the behavior itself still has to be confirmed in Excel (tasks.md).
"""
import os
import re

from src.backend.puzzle_state import ENTITY_FACE_LEGEND, ENTITY_FACE_MATRIX

VBA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "vba")
EXCEL_MAX_ROW_HEIGHT = 409


def _src(name):
    with open(os.path.join(VBA_DIR, name), "r", encoding="utf-8") as f:
        return f.read()


def _proc(source, header):
    start = source.index(header)
    end = re.compile(r"^End (Sub|Function)", re.MULTILINE).search(source, start).start()
    return source[start:end]


def _const(source, name):
    m = re.search(rf"Private Const {name} As \w+ = \"?([\d:.]+)\"?", source)
    assert m, f"constant {name} not found"
    return m.group(1)


# --- Midnight clock ---------------------------------------------------------

def test_clock_runs_thirteen_minutes_from_1147_within_the_3_to_5_minute_play_budget():
    fx = _src("M_HorrorFX.bas")
    start = int(_const(fx, "CLOCK_START_MINUTE"))
    minutes = int(_const(fx, "MINUTES_TO_MIDNIGHT"))
    h, m, s = (int(x) for x in _const(fx, "CLOCK_TICK_INTERVAL").split(":"))
    assert start == 47 and start + minutes == 60   # 11:47 PM -> the midnight stroke
    real_seconds = minutes * (h * 3600 + m * 60 + s)
    assert 180 <= real_seconds <= 300


def test_clock_text_reads_pm_minutes_then_midnight():
    text = _proc(_src("M_HorrorFX.bas"), "Public Function MidnightClockText()")
    assert '"12:00 MIDNIGHT"' in text
    assert '"11:" & Format$(' in text and '" PM"' in text


def test_clock_starts_on_open_after_the_state_sync_and_before_the_hud():
    opened = _proc(_src("ThisWorkbook.cls"), "Private Sub Workbook_Open()")
    assert opened.index("SyncDaemonState") < opened.index("StartMidnightClock") < opened.index("RefreshPhaseGuidance True")
    start = _proc(_src("M_HorrorFX.bas"), "Public Sub StartMidnightClock()")
    assert start.index("StopMidnightClock") < start.index("ScheduleClockTick")   # never two chains
    assert "If gArchiveSealed Then Exit Sub" in start
    assert "ws.Rows(13).RowHeight = ABYSS_BASE_HEIGHT" in start


def test_clock_timer_is_cancelled_everywhere_the_other_timers_are():
    fx = _src("M_HorrorFX.bas")
    stop = _proc(fx, "Public Sub StopMidnightClock()")
    assert 'Application.OnTime mNextClockTick, "MidnightClockTick", , False' in stop
    assert '"MidnightClockTick"' in _proc(fx, "Private Sub ScheduleClockTick()")
    assert "StopMidnightClock" in _proc(_src("ThisWorkbook.cls"), "Private Sub Workbook_BeforeClose")
    assert "StopMidnightClock" in _proc(_src("M_Bootstrap.bas"), "Public Sub EmergencyReset(")


def test_tick_advances_refreshes_the_status_bar_and_reschedules_only_while_running():
    tick = _proc(_src("M_HorrorFX.bas"), "Public Sub MidnightClockTick()")
    assert "If Not mClockRunning Or gArchiveSealed Then Exit Sub" in tick
    assert tick.index("AdvanceMidnightClock 1") < tick.index("ResetStatusBar") < tick.index("ScheduleClockTick")
    # The abyss animation runs DoEvents: Ctrl+Shift+R or a close can stop the clock meanwhile,
    # and a re-armed OnTime would reopen a closed workbook. Re-check the running flag after advancing.
    after_advance = tick[tick.index("AdvanceMidnightClock 1"):tick.index("ResetStatusBar")]
    assert "If Not mClockRunning Or gArchiveSealed Then Exit Sub" in after_advance


def test_status_bar_and_whispers_carry_the_live_clock():
    bas = _src("M_DaemonBridge.bas")
    status = _proc(bas, "Public Function CurrentPhaseStatusText()")
    assert 'MidnightClockText() & " | "' in status
    whisper = _proc(_src("M_HorrorFX.bas"), "Public Sub TriggerAmbientWhisper()")
    assert "MidnightClockText()" in whisper
    assert not re.search(r"11:\d\d PM", whisper)   # no frozen timestamps that contradict the clock


def test_masthead_clock_is_written_without_firing_worksheet_events():
    show = _proc(_src("M_HorrorFX.bas"), "Private Sub ShowMidnightClock(")
    assert show.index("Application.EnableEvents = False") < show.index('ws.Range("G1").Value')
    assert "ChrW(55358) & ChrW(56952)" in show   # the masthead blood drop, built at runtime (ASCII-only sources)
    assert "MidnightClockText()" in show


# --- Late interest (wrong entries cost a minute) ----------------------------

def test_every_rejected_entry_charges_a_minute_after_the_guidance_is_shown():
    bas = _src("M_DaemonBridge.bas")
    offline = _proc(bas, "Public Sub HandleOfflineEvent(")
    for cell in ("H7", "B18"):
        guidance = offline.index(f'ShowWrongEntryGuidance "{cell}"')
        assert offline.index("ChargeLateInterest", guidance) - guidance < 80
    online = _proc(bas, "Private Sub ProcessDaemonResponse(")
    assert online.index("ShowWrongEntryGuidance cellCoord") < online.index("ChargeLateInterest")


def test_late_interest_is_not_charged_without_a_running_clock():
    charge = _proc(_src("M_HorrorFX.bas"), "Public Sub ChargeLateInterest()")
    assert "If Not mClockRunning Or gArchiveSealed Then Exit Sub" in charge
    assert "AdvanceMidnightClock 1" in charge


# --- The abyss widens -------------------------------------------------------

def test_abyss_growth_stays_under_the_excel_row_height_limit():
    fx = _src("M_HorrorFX.bas")
    base = float(_const(fx, "ABYSS_BASE_HEIGHT"))
    growth = float(_const(fx, "ABYSS_GROWTH_PER_MINUTE"))
    minutes = int(_const(fx, "MINUTES_TO_MIDNIGHT"))
    assert base == 220   # the template height (test_build_ledger) and the closed abyss
    assert base + growth * minutes <= EXCEL_MAX_ROW_HEIGHT


def test_abyss_animation_tracks_its_own_height_so_a_protected_sheet_cannot_loop_forever():
    grow = _proc(_src("M_HorrorFX.bas"), "Private Sub GrowAbyssTo(")
    loop = grow[grow.index("Do While"):]
    assert "ws.Rows(13).RowHeight = h" in loop
    assert "= ws.Rows(13).RowHeight" not in loop   # never re-read inside the loop
    assert "If targetHeight > 409 Then targetHeight = 409" in grow


def test_advancing_the_clock_widens_the_abyss_and_forecloses_at_midnight():
    adv = _proc(_src("M_HorrorFX.bas"), "Private Sub AdvanceMidnightClock(")
    assert "GrowAbyssTo ws, ABYSS_BASE_HEIGHT + ABYSS_GROWTH_PER_MINUTE * mMinutesElapsed" in adv
    assert "If mMinutesElapsed >= MINUTES_TO_MIDNIGHT Then" in adv
    assert "ForecloseLedger ws" in adv


def test_sealing_stops_the_clock_and_closes_the_abyss_before_protecting_the_sheet():
    bas = _src("M_DaemonBridge.bas")
    lock_sheet = bas[bas.index('Case "LOCK_SHEET"'):bas.index('Case "TRIGGER_HAUNT"')]
    offline = _proc(bas, "Public Sub HandleOfflineEvent(")
    offline_seal = offline[offline.index("' Phase 4: Banishment Execution"):]
    for block in (lock_sheet, offline_seal):
        assert "StopMidnightClock" in block
        assert block.index("CloseAbyss ws") < block.index("ws.Protect")


# --- Midnight foreclosure (losing ending) -----------------------------------

def test_foreclosure_freezes_the_ledger_like_a_seal_and_stamps_the_missing_auditor():
    fore = _proc(_src("M_HorrorFX.bas"), "Private Sub ForecloseLedger(")
    for call in ("gMidnightForeclosed = True", "gArchiveSealed = True", "StopMidnightClock",
                 "StopEyeBlink", "StopHauntPolling", "ws.Protect"):
        assert call in fore
    assert "FORECLOSED - OCTOBER 31, 1928 - 12:00 MIDNIGHT" in fore
    assert "NIGHT AUDITOR MISSING SINCE 12:00 MIDNIGHT" in fore   # echoes Ward's disappearance
    assert fore.index("gArchiveSealed = True") < fore.index("RefreshPhaseGuidance False") < fore.index("ws.Protect")
    # The ruined ledger must not be offered for saving on close: mark the workbook clean after the last write
    assert fore.index("ws.Protect") < fore.index("ThisWorkbook.Saved = True") < fore.index("MsgBox")


def test_foreclosed_texts_take_precedence_over_the_sealed_texts():
    bas = _src("M_DaemonBridge.bas")
    status = _proc(bas, "Public Function CurrentPhaseStatusText()")
    assert status.index("If gMidnightForeclosed Then") < status.index("If gArchiveSealed Then")
    assert "LEDGER FORECLOSED" in status
    refresh = _proc(bas, "Public Sub RefreshPhaseGuidance(")
    assert refresh.index("If gMidnightForeclosed Then") < refresh.index("ElseIf gArchiveSealed Then")
    assert "FORECLOSED - 12:00 MIDNIGHT" in refresh
    reset_bar = _proc(_src("M_HorrorFX.bas"), "Public Sub ResetStatusBar()")
    assert "If gArchiveSealed And Not gMidnightForeclosed Then" in reset_bar


# --- Camera -----------------------------------------------------------------

def test_camera_only_moves_this_workbooks_own_window_and_clamps_zoom():
    fx = _src("M_HorrorFX.bas")
    for header in ("Private Sub CameraMove(", "Public Sub CameraDollyToAbyss()", "Public Sub RenderPixelFace("):
        body = _proc(fx, header)
        code = "\n".join(line for line in body.splitlines() if not line.strip().startswith("'"))
        assert "ActiveWindow" not in code   # ActiveWindow can belong to another workbook
    move = _proc(fx, "Private Sub CameraMove(")
    assert "Set win = ThisWorkbook.Windows(1)" in move
    assert "If toZoom > 400 Then toZoom = 400" in move
    assert "If toZoom < 10 Then toZoom = 10" in move


def test_dolly_into_row_13_returns_the_camera_home():
    dolly = _proc(_src("M_HorrorFX.bas"), "Public Sub CameraDollyToAbyss()")
    assert dolly.index("homeZoom = CLng(win.Zoom)") < dolly.index("CameraMove 12, 1")
    assert "CameraMove homeRow, homeCol, homeZoom" in dolly


def test_phase_1_clear_dollies_into_the_abyss_in_both_modes():
    bas = _src("M_DaemonBridge.bas")
    offline = _proc(bas, "Public Sub HandleOfflineEvent(")
    phase1 = offline[:offline.index("' Phase 2: Spray Reagent Button Click")]
    assert phase1.index("CameraDollyToAbyss") < phase1.index("gLocalPhase = 2")
    awaken = bas[bas.index('Case "AWAKEN_ROW_13"'):bas.index('Case "UNLOCK_CENSORED_ROWS"')]
    assert awaken.index("CameraDollyToAbyss") < awaken.index("RefreshPhaseGuidance False")


def test_reagent_reveal_leans_over_the_radar_then_settles_on_the_phase_3_working_view():
    render = _proc(_src("M_HorrorFX.bas"), "Public Sub RenderPixelFace(")
    paint = render.index("For r = 1 To 30")
    assert render.index("CameraMove 19, 11") < paint   # radar close-up (K20:AN49)
    # Rows 14+ keep the override cell B18, the cipher strip B21:H28 and the eye in one frame
    assert render.index("CameraMove 14, 1, homeZoom") > paint


# --- The entity's gaze ------------------------------------------------------

def test_iris_box_is_fully_iris_or_pupil_in_the_shared_face_matrix():
    fx = _src("M_HorrorFX.bas")
    top = int(_const(fx, "IRIS_TOP_ROW"))
    left = int(_const(fx, "IRIS_LEFT_COL"))
    assert (top, left) == (33, 22)   # V33:Y36
    for r in range(top, top + 4):
        for c in range(left, left + 4):
            ch = ENTITY_FACE_MATRIX[r - 20][c - 11]   # K20 is matrix [0][0]
            assert ENTITY_FACE_LEGEND[ch] in ("PHOSPHOR_GREEN", "DRIED_BLOOD")
    # The centered pupil is the default blinking eye W34:X35
    assert ENTITY_FACE_LEGEND[ENTITY_FACE_MATRIX[34 - 20][23 - 11]] == "DRIED_BLOOD"


def test_gaze_moves_the_pupil_at_most_one_cell_inside_the_iris():
    gaze = _proc(_src("M_HorrorFX.bas"), "Public Sub TrackEntityGaze(")
    assert "If Not mFaceRendered Or gArchiveSealed Then Exit Sub" in gaze
    assert "newRow = IRIS_TOP_ROW + 1 + stepY" in gaze
    assert "newCol = IRIS_LEFT_COL + 1 + stepX" in gaze
    assert "stepX = Sgn(dx)" in gaze and "stepY = Sgn(dy)" in gaze
    assert "If newRow = mPupilRow And newCol = mPupilCol Then Exit Sub" in gaze   # repaint only on change
    assert "iris.Interior.Color = COLOR_PHOSPHOR_GREEN" in gaze


def test_blink_follows_the_moved_pupil():
    blink = _proc(_src("M_HorrorFX.bas"), "Public Sub ToggleEyeBlink()")
    assert "Set eyeRange = ws.Cells(mPupilRow, mPupilCol).Resize(2, 2)" in blink
    assert 'ws.Range("W34:X35")' not in blink
    render = _proc(_src("M_HorrorFX.bas"), "Public Sub RenderPixelFace(")
    assert "mFaceRendered = True" in render
    assert render.index("mPupilRow = IRIS_TOP_ROW + 1") < render.index("StartEyeBlink ws")


def test_every_selection_feeds_the_gaze_before_button_clicks_exit_early():
    sel = _proc(_src("Sheet1_Archive.cls"), "Private Sub Worksheet_SelectionChange(")
    assert sel.index("If gArchiveSealed Then Exit Sub") < sel.index("TrackEntityGaze Target")
    assert sel.index("TrackEntityGaze Target") < sel.index('Me.Range("K18:AN18")')
