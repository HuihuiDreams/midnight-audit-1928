VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "Sheet1_Archive"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit

' ==============================================================================
' The Midnight Audit (1928) - Sheet1_Archive.cls
' Worksheet Event Hooks: Intercept User Inputs, Censored Text Inversion & Clicks
' ==============================================================================

Private mPrevSelectedCensored As Boolean
Private mSelectionCounter As Long

Private Sub Worksheet_Change(ByVal Target As Range)
    On Error GoTo CleanExit
    If Target Is Nothing Then Exit Sub
    If gArchiveSealed Then Exit Sub
    
    ' Check for Late Fee input in H7
    If Not Intersect(Target, Me.Range("H7")) Is Nothing Then
        ' A cleared cell is not an attempt
        If Len(Trim$(CStr(Me.Range("H7").Value))) = 0 Then Exit Sub
        Dim rawFee As String
        rawFee = Trim$(CStr(Me.Range("H7").Value))
        If UCase$(rawFee) = "[ TYPE FEE ]" Then Exit Sub
        If gLocalPhase > 1 Then
            Application.EnableEvents = False
            Me.Range("H7").NumberFormat = "$#,##0.00"
            Me.Range("H7").Value = 7#
            Me.Range("H7").Font.Color = COLOR_CARBON
            Me.Range("H7").Font.Italic = False
            Me.Range("H7").Font.Bold = True
            ShowPhaseBlockedHint "H7"
            Application.EnableEvents = True
            Exit Sub
        End If
        rawFee = StripPlaceholderPrefix(rawFee, "[ TYPE FEE ]")
        If Len(Trim$(rawFee)) = 0 Then Exit Sub
        Application.EnableEvents = False
        Me.Range("H7").Font.Color = COLOR_CARBON
        Me.Range("H7").Font.Italic = False
        Me.Range("H7").Font.Bold = True
        Me.Range("H7").HorizontalAlignment = xlRight
        PostEvent "cell_change", "H7", rawFee
        Application.EnableEvents = True
        Exit Sub
    End If
    
    ' Check for Override Code input in B18
    If Not Intersect(Target, Me.Range("B18")) Is Nothing Then
        ' A cleared cell is not an attempt
        If Len(Trim$(CStr(Me.Range("B18").Value))) = 0 Then Exit Sub
        Dim rawCode As String
        rawCode = Trim$(CStr(Me.Range("B18").Value))
        If UCase$(rawCode) = "[ LOCKED ]" Or UCase$(rawCode) = "[ TYPE PHRASE ]" Then Exit Sub
        If gLocalPhase < 3 Then
            Application.EnableEvents = False
            Me.Range("B18").Value = "[ LOCKED ]"
            Me.Range("B18").Font.Color = COLOR_HOSPITAL_GREEN
            Me.Range("B18").Font.Italic = True
            ShowLockedControlHint "OVERRIDE_B18"
            Application.EnableEvents = True
            Exit Sub
        End If
        If gLocalPhase >= 4 Then
            Application.EnableEvents = False
            Me.Range("B18").Value = "SEAL THE DEEP VAULT"
            Me.Range("B18").Font.Color = COLOR_CARBON
            Me.Range("B18").Font.Italic = False
            ShowPhaseBlockedHint "B18"
            Application.EnableEvents = True
            Exit Sub
        End If
        rawCode = StripPlaceholderPrefix(rawCode, "[ TYPE PHRASE ]")
        If Len(Trim$(rawCode)) = 0 Then Exit Sub
        Application.EnableEvents = False
        Me.Range("B18").Font.Color = COLOR_CARBON
        Me.Range("B18").Font.Italic = False
        Me.Range("B18").Font.Bold = True
        PostEvent "cell_change", "B18", rawCode
        Application.EnableEvents = True
        Exit Sub
    End If
    
CleanExit:
    Application.EnableEvents = True
End Sub

Private Sub Worksheet_SelectionChange(ByVal Target As Range)
    On Error Resume Next
    If Target Is Nothing Then Exit Sub
    If gArchiveSealed Then Exit Sub
    
    ' Once the radar is developed, the entity's pupil follows every selection
    TrackEntityGaze Target
    
    ' Check for Click on [ SPRAY REAGENT ] Button (K18:AN18)
    If Not Intersect(Target, Me.Range("K18:AN18")) Is Nothing Then
        If gLocalPhase = 2 Then
            TriggerReagentMacro
        Else
            ShowLockedControlHint "SPRAY_REAGENT"
        End If
        Exit Sub
    End If
    
    ' Check for Click on [ SEAL ARCHIVE ] Button (C18:D18)
    If Not Intersect(Target, Me.Range("C18:D18")) Is Nothing Then
        If gLocalPhase >= 4 Then
            If Not gArchiveSealed Then
                TriggerBanishMacro
            End If
        Else
            ShowLockedControlHint "SEAL_ARCHIVE"
        End If
        Exit Sub
    End If

    ' Provide live guidance if player selects locked B18 early
    If Not Intersect(Target, Me.Range("B18")) Is Nothing Then
        If gLocalPhase < 3 Then
            ShowLockedControlHint "OVERRIDE_B18"
            Exit Sub
        End If
    End If
    
    ' Intersecting Row 13 Abyss
    If Not Intersect(Target, Me.Range("A13:I13")) Is Nothing Then
        ThudBeep
        FlashAbyssAbsorption Me
    End If
    
    ' Intersecting Censored Rows 14-16: Invert colors to read redacted borrower slips
    Dim isCensored As Boolean
    isCensored = Not Intersect(Target, Me.Range("A14:I16")) Is Nothing
    
    If isCensored And Not mPrevSelectedCensored Then
        ' Hover/Select active: Invert to readable Bone Paper
        Me.Range("A14:I16").Interior.Color = COLOR_DECAYING_PAPER
        Me.Range("A14:I16").Font.Color = COLOR_CARBON
        mPrevSelectedCensored = True
    ElseIf Not isCensored And mPrevSelectedCensored Then
        ' Deselected: If not awakened yet, return to Abyss black
        If gLocalPhase < 2 Then
            Me.Range("A14:I16").Interior.Color = COLOR_ABYSS
            Me.Range("A14:I16").Font.Color = COLOR_ABYSS
        End If
        mPrevSelectedCensored = False
    End If
    
    ' Ambient horror whisper sampling (every 12 selections)
    mSelectionCounter = mSelectionCounter + 1
    If mSelectionCounter >= 12 Then
        mSelectionCounter = 0
        TriggerAmbientWhisper
    End If
    
    On Error GoTo 0
End Sub
