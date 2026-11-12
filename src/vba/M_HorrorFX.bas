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
''' Window tremor: violently shakes the active Excel window for 400-600ms.
''' </summary>
Public Sub ScreenTremor()
    On Error Resume Next
    #If Mac Then
        ' macOS: shift active window slightly or toggle screen updating
        Dim i As Long
        For i = 1 To 6
            ActiveWindow.SmallScroll Down:=1
            PlatformSleep 40
            ActiveWindow.SmallScroll Up:=1
            PlatformSleep 40
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
        
        hWnd = GetForegroundWindow()
        If hWnd <> 0 Then
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
    
    Dim eyeRange As Range
    Set eyeRange = ws.Range("W34:X35")
    
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
    whispers(0) = "OCTOBER 31, 1928 - 11:49 PM | [HEARD: SCRATCHING BENEATH TILES...]"
    whispers(1) = "OCTOBER 31, 1928 - 11:51 PM | [ROOM TEMP DROPPING: UNNATURAL DRAFT]"
    whispers(2) = "OCTOBER 31, 1928 - 11:53 PM | [PRESSURE DROPPING: SMELL OF FORMALDEHYDE]"
    whispers(3) = "OCTOBER 31, 1928 - 11:55 PM | [WARNING: RADAR VOID FLUCTUATING]"
    
    Application.StatusBar = whispers(mWhisperIndex Mod 4)
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
''' Restores default 1928 status bar baseline.
''' </summary>
Public Sub ResetStatusBar()
    On Error Resume Next
    mNextResetTime = 0
    If gArchiveSealed Then
        Application.StatusBar = "OCTOBER 31, 1928 - 00:01 AM | ARCHIVE SEALED | REST NOW, AUDITOR"
    Else
        Application.StatusBar = "OCTOBER 31, 1928 - 11:47 PM | ALL HALLOWS' EVE | ANNEX ARCHIVE DELINQUENCY LEDGER"
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
