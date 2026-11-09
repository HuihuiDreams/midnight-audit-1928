Attribute VB_Name = "M_HorrorFX"
Option Explicit

' ==============================================================================
' The Midnight Audit (1928) - M_HorrorFX.bas
' Sensory Horror Engine: Tremors, Inversion, Pixel Manifestation & Blood Spreading
' ==============================================================================

Private mEyeBlinkState As Boolean
Private mNextBlinkTime As Double

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
        Dim step As Long
        
        hWnd = GetForegroundWindow()
        If hWnd <> 0 Then
            GetWindowRect hWnd, r
            origX = r.Left
            origY = r.Top
            width = r.Right - r.Left
            height = r.Bottom - r.Top
            
            For step = 1 To 12
                Dim dx As Long, dy As Long
                dx = (step Mod 3 - 1) * 8
                dy = ((step + 1) Mod 3 - 1) * 8
                MoveWindow hWnd, origX + dx, origY + dy, width, height, 1
                PlatformSleep 25
            Next step
            
            ' Restore original position
            MoveWindow hWnd, origX, origY, width, height, 1
        End If
    #End If
    On Error GoTo 0
End Sub

''' <summary>
''' Kerosene lamp breathing/flicker effect: shifts background subtly.
''' </summary>
Public Sub FlashKeroseneLamp()
    On Error Resume Next
    Dim ws As Worksheet
    Set ws = ActiveSheet
    
    Dim c As Range
    Set c = ws.Range("A1:I5")
    
    c.Interior.Color = COLOR_DECAYING_PAPER
    DoEvents
    PlatformSleep 60
    c.Interior.Color = COLOR_BONE_PAPER
    DoEvents
    On Error GoTo 0
End Sub

''' <summary>
''' Thunder Strobe: rapid inversion of background for banishment climax.
''' </summary>
Public Sub ThunderInvert()
    On Error Resume Next
    Dim ws As Worksheet
    Set ws = ActiveSheet
    
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
    Dim cell As Range
    
    ' Pre-clear floorplan
    ws.Range("K20:AN49").Value = Empty
    
    ' Render concentric eldritch skull & central glowing eye (W34:X35 is r=15..16, c=13..14)
    For r = 1 To 30
        For c = 1 To 30
            Set cell = ws.Cells(19 + r, 10 + c)
            
            Dim dr As Long, dc As Long, distSq As Long
            dr = r - 15
            dc = c - 14
            distSq = dr * dr + dc * dc
            
            If (r = 15 Or r = 16) And (c = 13 Or c = 14) Then
                ' Central pupil: exactly W34:X35
                cell.Interior.Color = COLOR_DRIED_BLOOD
            ElseIf r >= 14 And r <= 17 And c >= 12 And c <= 15 Then
                ' Glowing Iris
                cell.Interior.Color = COLOR_PHOSPHOR_GREEN
            ElseIf r >= 13 And r <= 18 And c >= 11 And c <= 16 Then
                ' Eye socket
                cell.Interior.Color = COLOR_CARBON
            ElseIf distSq <= 170 And distSq >= 120 Then
                ' Outer skull boundary
                cell.Interior.Color = COLOR_CARBON
            ElseIf distSq < 120 Then
                ' Decaying bone tissue
                cell.Interior.Color = COLOR_DECAYING_PAPER
            Else
                cell.Interior.Color = COLOR_BONE_PAPER
            End If
            
            ' Horns curving upwards
            If r < 10 And (c = r Or c = (31 - r) Or (Abs(c - 9) <= 1 And r < 8) Or (Abs(c - 22) <= 1 And r < 8)) Then
                cell.Interior.Color = COLOR_CARBON
            End If
        Next c
        DoEvents
        PlatformSleep 12
    Next r
    
    ' Start blinking loop for eye
    StartEyeBlink ws
    On Error GoTo 0
End Sub

''' <summary>
''' Starts background timer for the central eye blinking in the radar.
''' </summary>
Public Sub StartEyeBlink(ByVal ws As Worksheet)
    On Error Resume Next
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
