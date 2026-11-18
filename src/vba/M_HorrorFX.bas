Attribute VB_Name = "M_HorrorFX"
Option Explicit

' ==============================================================================
' The Midnight Audit (1928) - M_HorrorFX.bas
' Sensory Horror Engine: Tremors, Inversion, Pixel Manifestation & Blood Spreading
' ==============================================================================

Private mEyeBlinkState As Boolean
Private mNextBlinkTime As Double
Private mWhisperIndex As Long
Private mNextResetTime As Double

' Midnight clock: 13 in-game minutes from 11:47 PM to the midnight stroke. Every rejected
' entry costs one more minute, and each minute widens the Row 13 abyss.
Public gMidnightForeclosed As Boolean
Private Const CLOCK_START_MINUTE As Long = 47
Private Const MINUTES_TO_MIDNIGHT As Long = 13
Private Const CLOCK_TICK_INTERVAL As String = "00:00:20"
Private Const DREAD_MINUTES As Long = 3
Private Const ABYSS_BASE_HEIGHT As Double = 220
Private Const ABYSS_GROWTH_PER_MINUTE As Double = 14
Private mMinutesElapsed As Long
Private mClockRunning As Boolean
Private mNextClockTick As Double

' Entity gaze: the 2x2 pupil moves inside the 4x4 iris V33:Y36 toward the selected cell
Private Const IRIS_TOP_ROW As Long = 33
Private Const IRIS_LEFT_COL As Long = 22
Private Const GAZE_DEAD_ZONE As Double = 8
Private mFaceRendered As Boolean
Private mPupilRow As Long
Private mPupilCol As Long

' Camera: animated zoom and scroll of this workbook's own window
Private Const CAMERA_FRAMES As Long = 10

''' <summary>
''' Low-frequency taboo thud: rattles physical speaker hardware at 37Hz on Windows.
''' </summary>
Public Sub ThudBeep()
    On Error Resume Next
    #If Mac Then
        ' macOS: visual subtle flicker as audio fallback
        FlashKeroseneLamp
    #Else
        BeepAPI 37, 300
    #End If
    On Error GoTo 0
End Sub

''' <summary>
''' Window tremor: violently shakes the Excel window for 400-600ms (Windows), or flickers the ledger (macOS).
''' </summary>
Public Sub ScreenTremor()
    On Error Resume Next
    #If Mac Then
        ' macOS: no safe window handle, and scrolling ActiveWindow can hit another workbook and drift.
        ' Shake the ledger itself with lamp flickers instead.
        Dim i As Long
        For i = 1 To 3
            FlashKeroseneLamp
            PlatformSleep 60
        Next i
    #Else
        #If VBA7 Then
            Dim hWnd As LongPtr
        #Else
            Dim hWnd As Long
        #End If
        Dim r As RECT
        Dim origX As Long, origY As Long
        Dim width As Long, height As Long
        Dim shakeStep As Long
        
        ' Shake Excel only, and only while it is in front: the player may have switched to another application
        hWnd = Application.Hwnd
        If hWnd <> 0 And hWnd = GetForegroundWindow() Then
            GetWindowRect hWnd, r
            origX = r.Left
            origY = r.Top
            width = r.Right - r.Left
            height = r.Bottom - r.Top
            
            For shakeStep = 1 To 12
                Dim dx As Long, dy As Long
                dx = (shakeStep Mod 3 - 1) * 8
                dy = ((shakeStep + 1) Mod 3 - 1) * 8
                MoveWindow hWnd, origX + dx, origY + dy, width, height, 1
                PlatformSleep 25
            Next shakeStep
            
            ' Restore original position
            MoveWindow hWnd, origX, origY, width, height, 1
        End If
    #End If
    On Error GoTo 0
End Sub

''' <summary>
''' Kerosene lamp breathing/flicker effect: shifts background subtly,
''' then restores each header cell's exact original color.
''' </summary>
Public Sub FlashKeroseneLamp()
    On Error Resume Next
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")
    If ws Is Nothing Then Set ws = ActiveSheet
    
    Dim c As Range
    Set c = ws.Range("A1:I5")
    
    Dim numR As Long, numC As Long
    numR = c.Rows.Count
    numC = c.Columns.Count
    
    Dim origColors() As Long
    ReDim origColors(1 To numR, 1 To numC)
    
    Dim i As Long, j As Long
    For i = 1 To numR
        For j = 1 To numC
            origColors(i, j) = c.Cells(i, j).Interior.Color
        Next j
    Next i
    
    c.Interior.Color = COLOR_DECAYING_PAPER
    DoEvents
    PlatformSleep 60
    
    For i = 1 To numR
        For j = 1 To numC
            c.Cells(i, j).Interior.Color = origColors(i, j)
        Next j
    Next i
    DoEvents
    On Error GoTo 0
End Sub

''' <summary>
''' Thunder Strobe: rapid inversion of background for banishment climax.
''' </summary>
Public Sub ThunderInvert()
    On Error Resume Next
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")
    If ws Is Nothing Then Set ws = ActiveSheet
    
    Dim target As Range
    Set target = ws.Range("A1:J18")
    
    Dim flash As Long
    For flash = 1 To 5
        target.Interior.Color = RGB(255, 255, 255)
        target.Font.Color = RGB(0, 0, 0)
        DoEvents
        PlatformSleep 40
        
        target.Interior.Color = RGB(0, 0, 0)
        target.Font.Color = RGB(255, 255, 255)
        DoEvents
        PlatformSleep 40
    Next flash
    
    ' Lock into Cold Ash
    target.Interior.Color = COLOR_COLD_ASH
    target.Font.Color = COLOR_CARBON
    DoEvents
    On Error GoTo 0
End Sub

''' <summary>
''' Spreads dried bloodstain outward from an invalid input cell across 5 frames.
''' </summary>
Public Sub SpreadBloodScab(ByVal Target As Range)
    On Error Resume Next
    If Target Is Nothing Then Exit Sub
    
    Dim baseCell As Range
    Set baseCell = Target.Cells(1, 1)
    
    Dim baseRow As Long, baseCol As Long
    baseRow = baseCell.Row
    baseCol = baseCell.Column
    
    Dim maxSpread As Long
    maxSpread = 2
    If baseRow - maxSpread < 1 Then maxSpread = baseRow - 1
    If baseCol - maxSpread < 1 Then maxSpread = baseCol - 1
    If maxSpread < 0 Then maxSpread = 0
    
    Dim fullRange As Range
    Set fullRange = baseCell.Offset(-maxSpread, -maxSpread).Resize(maxSpread * 2 + 1, maxSpread * 2 + 1)
    
    Dim numR As Long, numC As Long
    numR = fullRange.Rows.Count
    numC = fullRange.Columns.Count
    
    Dim origColors() As Long
    ReDim origColors(1 To numR, 1 To numC)
    
    Dim i As Long, j As Long
    For i = 1 To numR
        For j = 1 To numC
            origColors(i, j) = fullRange.Cells(i, j).Interior.Color
        Next j
    Next i
    
    If maxSpread >= 1 Then
        Dim r As Long
        For r = 1 To maxSpread
            Dim spreadRange As Range
            Set spreadRange = baseCell.Offset(-r, -r).Resize(r * 2 + 1, r * 2 + 1)
            spreadRange.Interior.Color = COLOR_DRIED_BLOOD
            DoEvents
            PlatformSleep 30
        Next r
    Else
        baseCell.Interior.Color = COLOR_DRIED_BLOOD
        DoEvents
        PlatformSleep 30
    End If
    
    ' Restore exact original colors of each affected cell after brief hesitation
    PlatformSleep 150
    For i = 1 To numR
        For j = 1 To numC
            fullRange.Cells(i, j).Interior.Color = origColors(i, j)
        Next j
    Next i
    On Error GoTo 0
End Sub

''' <summary>
''' Renders the 30x30 entity pixel face onto the floorplan area K20:AN49.
''' Aligns central pupil center with blinking eye coordinates W34:X35.
''' </summary>
Public Sub RenderPixelFace(ByVal ws As Worksheet)
    On Error Resume Next
    Dim r As Long, c As Long
    Dim faceRow As String
    Dim win As Window
    Dim homeZoom As Long
    
    homeZoom = 85
    Set win = ThisWorkbook.Windows(1)
    If Not win Is Nothing Then homeZoom = CLng(win.Zoom)
    
    ' Lean in over the basement radar before the reagent develops it
    CameraMove 19, 11, homeZoom + 40
    
    ' Pre-clear floorplan
    ws.Range("K20:AN49").Value = Empty
    
    ' Paint the entity face row by row from the shared matrix (the pupil is W34:X35)
    For r = 1 To 30
        faceRow = EntityFaceRow(r)
        For c = 1 To 30
            ws.Cells(19 + r, 10 + c).Interior.Color = EntityFaceColor(Mid$(faceRow, c, 1))
        Next c
        DoEvents
        PlatformSleep 12
    Next r
    PlatformSleep 600
    
    ' Pull back to the Phase 3 working view: override cell B18, cipher strip and the watching eye
    CameraMove 14, 1, homeZoom
    
    ' The pupil starts centered and from now on follows the player's selection
    mPupilRow = IRIS_TOP_ROW + 1
    mPupilCol = IRIS_LEFT_COL + 1
    mFaceRendered = True
    
    ' Start blinking loop for eye
    StartEyeBlink ws
    On Error GoTo 0
End Sub

' BEGIN GENERATED ENTITY FACE - do not edit by hand; run scripts/sync_vba_radar.py
' Source of truth: ENTITY_FACE_MATRIX and ENTITY_FACE_LEGEND in src/backend/puzzle_state.py
Private Function EntityFaceRow(ByVal r As Long) As String
    Select Case r
        Case 1: EntityFaceRow = "#......###..........###......#"
        Case 2: EntityFaceRow = ".#.....###...###....###.....#."
        Case 3: EntityFaceRow = "..#....################....#.."
        Case 4: EntityFaceRow = "...#...################...#..."
        Case 5: EntityFaceRow = "....#.####,,,,,,,,,####..#...."
        Case 6: EntityFaceRow = ".....#####,,,,,,,,,,#####....."
        Case 7: EntityFaceRow = "....######,,,,,,,,,,#####....."
        Case 8: EntityFaceRow = "...###,###,,,,,,,,,,######...."
        Case 9: EntityFaceRow = "...##,,,#,,,,,,,,,,,,#,,##...."
        Case 10: EntityFaceRow = "..###,,,,#,,,,,,,,,,#,,,###..."
        Case 11: EntityFaceRow = "..##,,,,,,,,,,,,,,,,,,,,,##..."
        Case 12: EntityFaceRow = "..##,,,,,,,,,,,,,,,,,,,,,##..."
        Case 13: EntityFaceRow = "..##,,,,,,######,,,,,,,,,##..."
        Case 14: EntityFaceRow = ".###,,,,,,#GGGG#,,,,,,,,,###.."
        Case 15: EntityFaceRow = ".###,,,,,,#GBBG#,,,,,,,,,###.."
        Case 16: EntityFaceRow = ".###,,,,,,#GBBG#,,,,,,,,,###.."
        Case 17: EntityFaceRow = "..##,,,,,,#GGGG#,,,,,,,,,##..."
        Case 18: EntityFaceRow = "..##,,,,,,######,,,,,,,,,##..."
        Case 19: EntityFaceRow = "..##,,,,,,,,,,,,,,,,,,,,,##..."
        Case 20: EntityFaceRow = "..###,,,,,,,,,,,,,,,,,,,###..."
        Case 21: EntityFaceRow = "...##,,,,,BBBBBBBBBB,,,,##...."
        Case 22: EntityFaceRow = "...###,,,,BBBBBBBBBB,,,###...."
        Case 23: EntityFaceRow = "....###,,,BBBBBBBBBB,,###....."
        Case 24: EntityFaceRow = ".....###,,,,,,,,,,,,,###......"
        Case 25: EntityFaceRow = "......####,,,,,,,,,####......."
        Case 26: EntityFaceRow = ".......###############........"
        Case 27: EntityFaceRow = ".........###########.........."
        Case 28: EntityFaceRow = ".............###.............."
        Case 29: EntityFaceRow = ".............................."
        Case 30: EntityFaceRow = ".............................."
    End Select
End Function

Private Function EntityFaceColor(ByVal ch As String) As Long
    Select Case ch
        Case ".": EntityFaceColor = COLOR_BONE_PAPER
        Case ",": EntityFaceColor = COLOR_DECAYING_PAPER
        Case "#": EntityFaceColor = COLOR_CARBON
        Case "B": EntityFaceColor = COLOR_DRIED_BLOOD
        Case "G": EntityFaceColor = COLOR_PHOSPHOR_GREEN
        Case Else: EntityFaceColor = COLOR_BONE_PAPER
    End Select
End Function
' END GENERATED ENTITY FACE

''' <summary>
''' Starts background timer for the central eye blinking in the radar.
''' </summary>
Public Sub StartEyeBlink(ByVal ws As Worksheet)
    On Error Resume Next
    ' RenderPixelFace and the START_EYE_BLINK action both start the blink: cancel the pending
    ' timer first so only one OnTime chain exists and StopEyeBlink can always cancel it.
    StopEyeBlink
    mEyeBlinkState = False
    ToggleEyeBlink
    On Error GoTo 0
End Sub

Public Sub ToggleEyeBlink()
    On Error Resume Next
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")
    If ws Is Nothing Then Set ws = ActiveSheet
    If ws Is Nothing Then Exit Sub
    
    ' Guard: only run in Phase 2 or 3, and only when archive is not sealed
    If gArchiveSealed Or (gLocalPhase <> 2 And gLocalPhase <> 3) Then
        StopEyeBlink
        Exit Sub
    End If
    
    ' The pupil may have moved toward the player's selection (TrackEntityGaze); W34:X35 is its centered home
    If mPupilRow = 0 Then
        mPupilRow = IRIS_TOP_ROW + 1
        mPupilCol = IRIS_LEFT_COL + 1
    End If
    Dim eyeRange As Range
    Set eyeRange = ws.Cells(mPupilRow, mPupilCol).Resize(2, 2)
    
    mEyeBlinkState = Not mEyeBlinkState
    If mEyeBlinkState Then
        eyeRange.Interior.Color = COLOR_DRIED_BLOOD
    Else
        eyeRange.Interior.Color = COLOR_PHOSPHOR_GREEN
    End If
    
    ' Schedule next blink in 2 seconds if still in Phase 2 or 3
    mNextBlinkTime = Now + TimeValue("00:00:02")
    Application.OnTime mNextBlinkTime, "ToggleEyeBlink"
    On Error GoTo 0
End Sub

Public Sub StopEyeBlink()
    On Error Resume Next
    If mNextBlinkTime <> 0 Then
        Application.OnTime mNextBlinkTime, "ToggleEyeBlink", , False
        mNextBlinkTime = 0
    End If
    On Error GoTo 0
End Sub

''' <summary>
''' Abyss Torchlight Absorption: Briefly glimmers deep blood-black when selected,
''' simulating flashlight illumination swallowed by the floorboard void.
''' </summary>
Public Sub FlashAbyssAbsorption(ByVal ws As Worksheet)
    On Error Resume Next
    If ws Is Nothing Then Exit Sub
    
    Dim abyssRange As Range
    Set abyssRange = ws.Range("A13:I13")
    
    Dim origFontColor As Long
    origFontColor = abyssRange.Cells(1, 1).Font.Color
    
    Application.EnableEvents = False
    
    ' Flash to deep dried blood shadow
    abyssRange.Interior.Color = COLOR_DRIED_BLOOD
    If origFontColor = COLOR_ABYSS Then
        abyssRange.Font.Color = COLOR_HOSPITAL_GREEN
    End If
    DoEvents
    PlatformSleep 80
    
    ' Swallow back to absolute void
    abyssRange.Interior.Color = COLOR_ABYSS
    abyssRange.Font.Color = origFontColor
    DoEvents
    
    Application.EnableEvents = True
    On Error GoTo 0
End Sub

''' <summary>
''' Ambient Horror Whisper: Dispatches subtle, non-intrusive sensory cues to the status bar.
''' </summary>
Public Sub TriggerAmbientWhisper()
    On Error Resume Next
    If gArchiveSealed Then Exit Sub
    
    Dim whispers(0 To 3) As String
    whispers(0) = "[HEARD: SCRATCHING BENEATH TILES...]"
    whispers(1) = "[ROOM TEMP DROPPING: UNNATURAL DRAFT]"
    whispers(2) = "[PRESSURE DROPPING: SMELL OF FORMALDEHYDE]"
    whispers(3) = "[WARNING: RADAR VOID FLUCTUATING]"
    
    ' Stamped with the live midnight clock
    Application.StatusBar = "OCTOBER 31, 1928 - " & MidnightClockText() & " | " & whispers(mWhisperIndex Mod 4)
    mWhisperIndex = mWhisperIndex + 1
    
    ' Cancel any previously scheduled reset to avoid stacking timers
    If mNextResetTime <> 0 Then
        Application.OnTime mNextResetTime, "ResetStatusBar", , False
        mNextResetTime = 0
    End If
    
    ' Schedule restoration in 2 seconds
    mNextResetTime = Now + TimeValue("00:00:02")
    Application.OnTime mNextResetTime, "ResetStatusBar"
    On Error GoTo 0
End Sub

''' <summary>
''' Restores the active phase status bar guidance after an ambient whisper finishes.
''' </summary>
Public Sub ResetStatusBar()
    On Error Resume Next
    mNextResetTime = 0
    ' A foreclosed ledger is frozen like a sealed one but keeps its own (losing) status text
    If gArchiveSealed And Not gMidnightForeclosed Then
        Application.StatusBar = "OCTOBER 31, 1928 - 00:01 AM | ARCHIVE SEALED | REST NOW, AUDITOR"
    Else
        Application.StatusBar = CurrentPhaseStatusText()
    End If
    On Error GoTo 0
End Sub

''' <summary>
''' Cancels any pending status bar reset timer to prevent ghost workbook re-opening on close.
''' </summary>
Public Sub CancelAmbientWhisper()
    On Error Resume Next
    If mNextResetTime <> 0 Then
        Application.OnTime mNextResetTime, "ResetStatusBar", , False
        mNextResetTime = 0
    End If
    On Error GoTo 0
End Sub

' ==============================================================================
' Midnight Clock & The Widening Abyss
' ==============================================================================

''' <summary>
''' In-game time for the masthead, status bar and whispers: 11:47 PM ... 11:59 PM, then 12:00 MIDNIGHT.
''' </summary>
Public Function MidnightClockText() As String
    Dim m As Long
    m = CLOCK_START_MINUTE + mMinutesElapsed
    If m >= 60 Then
        MidnightClockText = "12:00 MIDNIGHT"
    Else
        MidnightClockText = "11:" & Format$(m, "00") & " PM"
    End If
End Function

''' <summary>
''' Starts the clock at 11:47 PM with the abyss closed (Workbook_Open). A sealed archive keeps no time.
''' </summary>
Public Sub StartMidnightClock()
    On Error Resume Next
    StopMidnightClock
    If gArchiveSealed Then Exit Sub
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")
    If ws Is Nothing Then Exit Sub
    
    mMinutesElapsed = 0
    gMidnightForeclosed = False
    ws.Rows(13).RowHeight = ABYSS_BASE_HEIGHT
    ShowMidnightClock ws
    mClockRunning = True
    ScheduleClockTick
    On Error GoTo 0
End Sub

Private Sub ScheduleClockTick()
    mNextClockTick = Now + TimeValue(CLOCK_TICK_INTERVAL)
    Application.OnTime mNextClockTick, "MidnightClockTick"
End Sub

''' <summary>
''' Cancels the clock (seal, foreclosure, EmergencyReset, workbook close).
''' </summary>
Public Sub StopMidnightClock()
    On Error Resume Next
    mClockRunning = False
    If mNextClockTick <> 0 Then
        Application.OnTime mNextClockTick, "MidnightClockTick", , False
        mNextClockTick = 0
    End If
    On Error GoTo 0
End Sub

''' <summary>
''' One in-game minute passes.
''' </summary>
Public Sub MidnightClockTick()
    On Error Resume Next
    mNextClockTick = 0
    If Not mClockRunning Or gArchiveSealed Then Exit Sub
    AdvanceMidnightClock 1
    ' Midnight may have foreclosed the ledger, and the abyss animation yields (DoEvents): Ctrl+Shift+R or a
    ' close can stop the clock meanwhile. Re-arming then would leave an OnTime that reopens a closed workbook.
    If Not mClockRunning Or gArchiveSealed Then Exit Sub
    ResetStatusBar
    ScheduleClockTick
    On Error GoTo 0
End Sub

''' <summary>
''' A rejected fee or cipher costs the player one minute of their night.
''' Called after the wrong-entry guidance so the charge is appended to it.
''' </summary>
Public Sub ChargeLateInterest()
    On Error Resume Next
    If Not mClockRunning Or gArchiveSealed Then Exit Sub
    AdvanceMidnightClock 1
    If gArchiveSealed Then Exit Sub
    If VarType(Application.StatusBar) = vbString Then
        Application.StatusBar = Application.StatusBar & " | LATE INTEREST: ONE MINUTE OF YOUR NIGHT"
    End If
    On Error GoTo 0
End Sub

Private Sub AdvanceMidnightClock(ByVal minutes As Long)
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")
    If ws Is Nothing Then Exit Sub
    
    mMinutesElapsed = mMinutesElapsed + minutes
    If mMinutesElapsed > MINUTES_TO_MIDNIGHT Then mMinutesElapsed = MINUTES_TO_MIDNIGHT
    ShowMidnightClock ws
    GrowAbyssTo ws, ABYSS_BASE_HEIGHT + ABYSS_GROWTH_PER_MINUTE * mMinutesElapsed
    
    If mMinutesElapsed >= MINUTES_TO_MIDNIGHT Then
        ForecloseLedger ws
    ElseIf MINUTES_TO_MIDNIGHT - mMinutesElapsed <= DREAD_MINUTES Then
        ' The last minutes: the abyss breathes on every tick
        FlashAbyssAbsorption ws
    End If
End Sub

''' <summary>
''' Writes the live time into the G1 masthead stamp; in the last minutes the stamp bleeds.
''' </summary>
Private Sub ShowMidnightClock(ByVal ws As Worksheet)
    On Error Resume Next
    Dim eventsWereOn As Boolean
    eventsWereOn = Application.EnableEvents
    Application.EnableEvents = False
    
    ' Blood drop U+1FA78 and em dash U+2014 built at runtime (VBA sources stay ASCII)
    ws.Range("G1").Value = ChrW(55358) & ChrW(56952) & " [ ALL HALLOWS' EVE " & ChrW(8212) & " " & MidnightClockText() & " ]  "
    If MINUTES_TO_MIDNIGHT - mMinutesElapsed <= DREAD_MINUTES Then
        ws.Range("G1:I1").Interior.Color = COLOR_DRIED_BLOOD
        ws.Range("G1").Font.Color = COLOR_BONE_PAPER
    Else
        ws.Range("G1:I1").Interior.Color = COLOR_DECAYING_PAPER
        ws.Range("G1").Font.Color = COLOR_WARNING_RED
    End If
    
    Application.EnableEvents = eventsWereOn
    On Error GoTo 0
End Sub

''' <summary>
''' Animates Row 13 toward a height (capped at Excel's 409 pt). The height is tracked locally:
''' on a protected sheet the assignment fails silently and the loop must still end.
''' </summary>
Private Sub GrowAbyssTo(ByVal ws As Worksheet, ByVal targetHeight As Double)
    On Error Resume Next
    Dim h As Double
    h = ws.Rows(13).RowHeight
    If targetHeight > 409 Then targetHeight = 409
    Do While Abs(targetHeight - h) >= 1
        If targetHeight > h Then
            h = h + 2
            If h > targetHeight Then h = targetHeight
        Else
            h = h - 8
            If h < targetHeight Then h = targetHeight
        End If
        ws.Rows(13).RowHeight = h
        DoEvents
        PlatformSleep 30
    Loop
    On Error GoTo 0
End Sub

''' <summary>
''' The archive is sealed: the abyss closes back to its original 220 pt.
''' </summary>
Public Sub CloseAbyss(ByVal ws As Worksheet)
    GrowAbyssTo ws, ABYSS_BASE_HEIGHT
End Sub

''' <summary>
''' The losing ending: midnight strikes before the seal. The ledger freezes like a sealed one
''' (gArchiveSealed stops every hook, poll and timer) and lists the player as the missing auditor.
''' </summary>
Private Sub ForecloseLedger(ByVal ws As Worksheet)
    On Error Resume Next
    gMidnightForeclosed = True
    gArchiveSealed = True
    StopMidnightClock
    StopEyeBlink
    StopHauntPolling
    CancelAmbientWhisper
    
    Dim eventsWereOn As Boolean
    eventsWereOn = Application.EnableEvents
    Application.EnableEvents = False
    ws.Range("A13").Value = "MIDNIGHT. THE AUDITOR IS NOW THE AUDITED."
    ws.Range("A13").Font.Color = COLOR_WARNING_RED
    ws.Range("B10:H12").Value = Empty
    ws.Range("B10:H12").Interior.Color = COLOR_DRIED_BLOOD
    ws.Range("B10:H12").Font.Color = COLOR_BONE_PAPER
    ws.Range("B10").Value = "[ FORECLOSED - OCTOBER 31, 1928 - 12:00 MIDNIGHT ]"
    ws.Range("B11").Value = "ALL BALANCES TRANSFERRED TO THE BLACK GOAT'S LEDGER"
    ws.Range("B12").Value = "NIGHT AUDITOR MISSING SINCE 12:00 MIDNIGHT"
    Application.EnableEvents = eventsWereOn
    RefreshPhaseGuidance False
    
    ThudBeep
    ScreenTremor
    ' Frame the stamp above the fully opened abyss and stay there
    Dim win As Window
    Set win = ThisWorkbook.Windows(1)
    If Not win Is Nothing Then CameraMove 10, 1, CLng(win.Zoom) + 20
    
    ws.Protect
    ' Closing must not offer to save the ruined ledger: reopening restarts the clock on a clean sheet
    ThisWorkbook.Saved = True
    MsgBox "MIDNIGHT. The ledger is foreclosed and the night auditor is listed as missing." & vbCrLf & _
           "Close the workbook without saving and reopen it to audit again.", vbCritical, "Audit Foreclosed"
    On Error GoTo 0
End Sub

' ==============================================================================
' Camera: Zoom & Scroll Choreography
' ==============================================================================

''' <summary>
''' Eases this workbook's own window to a scroll position and zoom over CAMERA_FRAMES frames.
''' Never ActiveWindow: it can belong to another workbook.
''' </summary>
Private Sub CameraMove(ByVal toRow As Long, ByVal toCol As Long, ByVal toZoom As Long)
    On Error Resume Next
    Dim win As Window
    Set win = ThisWorkbook.Windows(1)
    If win Is Nothing Then Exit Sub
    If toZoom < 10 Then toZoom = 10
    If toZoom > 400 Then toZoom = 400
    If toRow < 1 Then toRow = 1
    If toCol < 1 Then toCol = 1
    
    Dim fromRow As Long, fromCol As Long, fromZoom As Long
    fromRow = win.ScrollRow
    fromCol = win.ScrollColumn
    fromZoom = CLng(win.Zoom)
    
    Dim f As Long
    Dim t As Double
    For f = 1 To CAMERA_FRAMES
        t = f / CAMERA_FRAMES
        t = t * t * (3 - 2 * t)   ' smoothstep ease-in-out
        win.Zoom = fromZoom + CLng((toZoom - fromZoom) * t)
        win.ScrollRow = fromRow + CLng((toRow - fromRow) * t)
        win.ScrollColumn = fromCol + CLng((toCol - fromCol) * t)
        DoEvents
        PlatformSleep 30
    Next f
    On Error GoTo 0
End Sub

''' <summary>
''' Phase 1 cleared: the camera leans into the awakened Row 13, holds on the red glyph, and returns home.
''' </summary>
Public Sub CameraDollyToAbyss()
    On Error Resume Next
    Dim win As Window
    Set win = ThisWorkbook.Windows(1)
    If win Is Nothing Then Exit Sub
    
    Dim homeRow As Long, homeCol As Long, homeZoom As Long
    homeRow = win.ScrollRow
    homeCol = win.ScrollColumn
    homeZoom = CLng(win.Zoom)
    
    CameraMove 12, 1, homeZoom + 40
    PlatformSleep 900
    CameraMove homeRow, homeCol, homeZoom
    On Error GoTo 0
End Sub

' ==============================================================================
' The Entity's Gaze
' ==============================================================================

''' <summary>
''' Once the radar is developed, the 2x2 pupil shifts one cell inside the iris V33:Y36
''' toward the selected cell (8 directions, centered when the player looks at the eye itself).
''' </summary>
Public Sub TrackEntityGaze(ByVal Target As Range)
    On Error Resume Next
    If Not mFaceRendered Or gArchiveSealed Then Exit Sub
    If Target Is Nothing Then Exit Sub
    
    Dim ws As Worksheet
    Set ws = Target.Worksheet
    Dim iris As Range
    Set iris = ws.Cells(IRIS_TOP_ROW, IRIS_LEFT_COL).Resize(4, 4)
    Dim spot As Range
    Set spot = Target.Cells(1, 1).MergeArea
    
    ' Direction in points, so the tall Row 13 and the 12 pt radar rows are weighed by their real size
    Dim dx As Double, dy As Double
    dx = (spot.Left + spot.Width / 2) - (iris.Left + iris.Width / 2)
    dy = (spot.Top + spot.Height / 2) - (iris.Top + iris.Height / 2)
    
    ' 0.41 = tan(22.5 deg): a mostly horizontal look keeps the pupil level, and vice versa
    Dim stepX As Long, stepY As Long
    If Abs(dx) > GAZE_DEAD_ZONE And Abs(dx) >= Abs(dy) * 0.41 Then stepX = Sgn(dx)
    If Abs(dy) > GAZE_DEAD_ZONE And Abs(dy) >= Abs(dx) * 0.41 Then stepY = Sgn(dy)
    
    Dim newRow As Long, newCol As Long
    newRow = IRIS_TOP_ROW + 1 + stepY
    newCol = IRIS_LEFT_COL + 1 + stepX
    If newRow = mPupilRow And newCol = mPupilCol Then Exit Sub
    
    iris.Interior.Color = COLOR_PHOSPHOR_GREEN
    ws.Cells(newRow, newCol).Resize(2, 2).Interior.Color = COLOR_DRIED_BLOOD
    mPupilRow = newRow
    mPupilCol = newCol
    mEyeBlinkState = True   ' a moving pupil is an open eye; the blink timer continues from here
    On Error GoTo 0
End Sub
