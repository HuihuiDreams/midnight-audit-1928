Attribute VB_Name = "M_DaemonBridge"
Option Explicit

' ==============================================================================
' The Midnight Audit (1928) - M_DaemonBridge.bas
' HTTP Communication Bridge with FastAPI Daemon + Zero-Dependency Offline Fallback
' ==============================================================================

Private Const DAEMON_URL As String = "http://127.0.0.1:8000/api"
Public gLocalPhase As Long
Public gHijackTriggered As Boolean
Public gArchiveSealed As Boolean
Private Const HAUNT_POLL_INTERVAL As String = "00:00:03"
Private mNextPollTime As Double
Private Const MAX_SHEET_ROW As Long = 1048576
Private Const MAX_SHEET_COLUMN As Long = 16384
Private Const MAX_RANGE_AREA As Long = 900

''' <summary>
''' Dispatches an event to the local Python daemon or routes to offline fallback.
''' </summary>
Public Sub PostEvent(ByVal eventType As String, Optional ByVal cellCoord As String = "", Optional ByVal cellVal As String = "", Optional ByVal buttonName As String = "")
    If gArchiveSealed Then Exit Sub
    On Error GoTo FallbackHandler

    Dim safeVal As String
    safeVal = Replace(cellVal, "\", "\\")
    safeVal = Replace(safeVal, """", "\""")
    safeVal = Replace(safeVal, vbCr, "")
    safeVal = Replace(safeVal, vbLf, "\n")
    safeVal = Replace(safeVal, vbTab, "\t")

    Dim jsonPayload As String
    jsonPayload = "{""event_type"":""" & eventType & """,""cell"":""" & cellCoord & """,""value"":""" & safeVal & """,""button"":""" & buttonName & """}"

    #If Mac Then
        ' Mac safe curl transport via unique temporary file to mitigate /tmp symlink attacks
        Dim tmpFile As String
        Randomize
        tmpFile = "/tmp/ma_payload_" & Format(Now, "hhnnss") & "_" & Int(Rnd * 100000) & ".json"
        On Error Resume Next
        Kill tmpFile
        On Error GoTo FallbackHandler
        Dim fNum As Integer
        fNum = FreeFile
        Open tmpFile For Output As #fNum
        Print #fNum, jsonPayload;
        Close #fNum

        Dim cmd As String
        Dim respText As String
        cmd = "curl -s -m 1 -X POST " & DAEMON_URL & "/event -H ""Content-Type: application/json"" --data-binary @" & tmpFile
        respText = MacScript("do shell script """ & Replace(cmd, """", "\""") & """")

        On Error Resume Next
        Kill tmpFile
        On Error GoTo FallbackHandler

        If Len(respText) > 0 And (InStr(respText, """accepted""") > 0 Or InStr(respText, """banished""") > 0 Or InStr(respText, """actions""") > 0) Then
            ProcessDaemonResponse respText, cellCoord
            Exit Sub
        ElseIf Len(respText) > 0 Then
            ' Server is reachable and responded with non-200 (e.g. 400/422/500).
            ' Do NOT fall back to offline mode, to avoid state divergence.
            ReportDaemonRefusal
            Exit Sub
        End If
    #Else
        ' Windows MSXML2 HTTP transport
        Dim http As Object
        Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
        http.Open "POST", DAEMON_URL & "/event", False
        http.setRequestHeader "Content-Type", "application/json"
        http.setTimeouts 500, 500, 1000, 1000
        http.send jsonPayload

        If http.Status = 200 Then
            ProcessDaemonResponse http.responseText, cellCoord
            Exit Sub
        ElseIf http.Status > 0 Then
            ' Server is reachable and responded with non-200 (e.g. 400/422/500).
            ' Do NOT fall back to offline mode, to avoid state divergence.
            ReportDaemonRefusal
            Exit Sub
        End If
    #End If

FallbackHandler:
    #If Mac Then
        On Error Resume Next
        Kill tmpFile
        On Error GoTo 0
    #End If
    ' Python daemon is not running; seamlessly route to local offline rule engine
    HandleOfflineEvent eventType, cellCoord, cellVal, buttonName
End Sub

''' <summary>
''' Tells the player the daemon refused the entry (for example when it could not save game state),
''' so a silent no-op is not mistaken for a broken workbook.
''' </summary>
Private Sub ReportDaemonRefusal()
    On Error Resume Next
    Application.DisplayStatusBar = True
    Application.StatusBar = "THE LEDGER REFUSES THE ENTRY - NOTHING WAS RECORDED. TRY AGAIN."
    On Error GoTo 0
End Sub

''' <summary>
''' Synchronizes local client state with the Python daemon on workbook open.
''' Queries /api/status to restore gLocalPhase and gArchiveSealed.
''' </summary>
Public Sub SyncDaemonState()
    On Error GoTo OfflineSync
    Dim respText As String

    #If Mac Then
        Dim cmd As String
        cmd = "curl -s -m 1 -X GET " & DAEMON_URL & "/status"
        respText = MacScript("do shell script """ & Replace(cmd, """", "\""") & """")
    #Else
        Dim http As Object
        Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
        http.Open "GET", DAEMON_URL & "/status", False
        http.setRequestHeader "Content-Type", "application/json"
        http.setTimeouts 500, 500, 1000, 1000
        http.send
        If http.Status = 200 Then
            respText = http.responseText
        End If
    #End If

    If Len(respText) > 0 Then
        Dim phaseStr As String
        phaseStr = ExtractJsonField(respText, "phase")
        If Len(phaseStr) = 0 Then phaseStr = ExtractJsonField(respText, "current_phase")
        If Len(phaseStr) > 0 Then
            Dim pVal As Long
            pVal = Val(phaseStr)
            If pVal >= 1 And pVal <= 4 Then gLocalPhase = pVal
        End If

        Dim sealedStr As String
        sealedStr = LCase$(Trim$(ExtractJsonField(respText, "archive_sealed")))
        If sealedStr = "true" Then
            gArchiveSealed = True
        ElseIf sealedStr = "false" Then
            gArchiveSealed = False
        End If
        Exit Sub
    End If

OfflineSync:
    ' Daemon is offline; initialize to phase 1 if not already set
    If gLocalPhase = 0 Then gLocalPhase = 1
End Sub

''' <summary>
''' Starts the background heartbeat that fetches haunts queued by the Kiro Agent (GET /api/pending),
''' so they appear while the player is thinking instead of waiting for the next edit or click.
''' </summary>
Public Sub StartHauntPolling()
    On Error Resume Next
    StopHauntPolling
    If gArchiveSealed Then Exit Sub
    mNextPollTime = Now + TimeValue(HAUNT_POLL_INTERVAL)
    Application.OnTime mNextPollTime, "PollPendingHaunts"
    On Error GoTo 0
End Sub

''' <summary>
''' Cancels the pending poll timer (EmergencyReset, workbook close, archive sealed).
''' </summary>
Public Sub StopHauntPolling()
    On Error Resume Next
    If mNextPollTime <> 0 Then
        Application.OnTime mNextPollTime, "PollPendingHaunts", , False
        mNextPollTime = 0
    End If
    On Error GoTo 0
End Sub

''' <summary>
''' One heartbeat: fetch queued haunts, run them, schedule the next beat.
''' A silent or refusing daemon is ignored; polling never falls back to the offline engine.
''' </summary>
Public Sub PollPendingHaunts()
    On Error Resume Next
    mNextPollTime = 0
    If gArchiveSealed Then Exit Sub

    Dim respText As String
    respText = FetchPendingHaunts()
    If InStr(respText, """command""") > 0 Then
        ' Queued actions are haunts, or the LOCK_SHEET that seals the archive after the Agent's ritual.
        ' A haunt may write into H7/B18; it must not be mistaken for a player attempt
        Dim eventsWereOn As Boolean
        eventsWereOn = Application.EnableEvents
        Application.EnableEvents = False
        ProcessDaemonResponse respText
        Application.EnableEvents = eventsWereOn
    End If

    StartHauntPolling
    On Error GoTo 0
End Sub

Private Function FetchPendingHaunts() As String
    On Error GoTo FetchFailed
    FetchPendingHaunts = ""
    #If Mac Then
        Dim cmd As String
        cmd = "curl -s -m 1 -X GET -H ""X-Audit-Client: 1"" " & DAEMON_URL & "/pending"
        FetchPendingHaunts = MacScript("do shell script """ & Replace(cmd, """", "\""") & """")
    #Else
        Dim http As Object
        Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
        http.Open "GET", DAEMON_URL & "/pending", False
        http.setRequestHeader "X-Audit-Client", "1"
        http.setTimeouts 500, 500, 1000, 1000
        http.send
        If http.Status = 200 Then FetchPendingHaunts = http.responseText
    #End If
    Exit Function
FetchFailed:
    FetchPendingHaunts = ""
End Function

''' <summary>
''' Executes returned server commands (JSON parser helper for standard actions)
''' </summary>
Private Sub ProcessDaemonResponse(ByVal jsonResp As String, Optional ByVal cellCoord As String = "")
    On Error Resume Next
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")
    If ws Is Nothing Then Set ws = ActiveSheet
    If ws Is Nothing Then Exit Sub

    ' Synchronize local phase counter
    Dim phaseStr As String
    phaseStr = ExtractJsonField(jsonResp, "current_phase")
    If Len(phaseStr) > 0 Then
        Dim pVal As Long
        pVal = Val(phaseStr)
        If pVal >= 1 And pVal <= 4 Then gLocalPhase = pVal
    End If

    Dim ranPhaseRefresh As Boolean
    ranPhaseRefresh = False

    ' Structured action dispatch: iterate actions array and dispatch by command/effect
    Dim posActions As Long
    posActions = InStr(1, jsonResp, """actions""", vbTextCompare)
    If posActions > 0 Then
        Dim posArrStart As Long
        posArrStart = InStr(posActions, jsonResp, "[")
        If posArrStart > 0 Then
            Dim arrEnd As Long
            arrEnd = FindMatchingBracket(jsonResp, posArrStart)
            If arrEnd = 0 Then arrEnd = Len(jsonResp)

            Dim currPos As Long
            currPos = posArrStart + 1
            Do While currPos < arrEnd
                Dim objStart As Long
                objStart = InStr(currPos, jsonResp, "{")
                If objStart = 0 Or objStart >= arrEnd Then Exit Do

                Dim objEnd As Long
                objEnd = FindMatchingBrace(jsonResp, objStart)
                If objEnd = 0 Or objEnd > arrEnd Then Exit Do

                Dim actionChunk As String
                actionChunk = Mid$(jsonResp, objStart, objEnd - objStart + 1)

                Dim cmd As String
                cmd = UCase$(Trim$(ExtractJsonField(actionChunk, "command")))

                Select Case cmd
                    Case "TRIGGER_FX"
                        Dim fxEffect As String
                        fxEffect = UCase$(Trim$(ExtractJsonField(actionChunk, "effect")))
                        Select Case fxEffect
                            Case "THUD_BEEP"
                                ThudBeep
                            Case "SCREEN_TREMOR"
                                ScreenTremor
                            Case "THUNDER_STROBE"
                                ThunderInvert
                            Case "SPREAD_BLOOD_SCAB"
                                Dim fxCell As String
                                fxCell = Trim$(ExtractJsonField(actionChunk, "cell"))
                                If Len(fxCell) = 0 Then fxCell = Trim$(cellCoord)
                                If Not IsValidCellAddress(fxCell) Then
                                    If gLocalPhase = 1 Then fxCell = "H7" Else fxCell = "B18"
                                End If
                                SpreadBloodScab ws.Range(fxCell)
                        End Select

                    Case "SET_VALUE"
                        Dim svCell As String, svVal As String
                        svCell = Trim$(ExtractJsonField(actionChunk, "cell"))
                        svVal = ExtractJsonField(actionChunk, "value")
                        If IsValidCellAddress(svCell) Then
                            svVal = NeutralizeFormulaPrefix(svVal)
                            ws.Range(svCell).NumberFormat = "@"
                            ws.Range(svCell).Value = svVal
                            ws.Range(svCell).Font.Color = COLOR_WARNING_RED
                        End If

                    Case "AWAKEN_ROW_13"
                        ws.Range("H7").NumberFormat = "$#,##0.00"
                        ws.Range("H7").Font.Color = COLOR_CARBON
                        ws.Range("H7").Font.Italic = False
                        ws.Range("H7").Font.Bold = True
                        ws.Range("H7").HorizontalAlignment = xlRight
                        ws.Range("A13").Font.Color = COLOR_WARNING_RED
                        ws.Range("A13").Value = "STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"
                        ws.Range("A14:I16").Interior.Color = COLOR_DECAYING_PAPER
                        ws.Range("A14:I16").Font.Color = COLOR_CARBON
                        RefreshPhaseGuidance False
                        ranPhaseRefresh = True

                    Case "UNLOCK_CENSORED_ROWS"
                        ws.Range("A14:I16").Interior.Color = COLOR_DECAYING_PAPER
                        ws.Range("A14:I16").Font.Color = COLOR_CARBON

                    Case "RENDER_PIXEL_MATRIX"
                        RenderPixelFace ws
                        RefreshPhaseGuidance True
                        ranPhaseRefresh = True

                    Case "START_EYE_BLINK"
                        StartEyeBlink ws

                    Case "HIJACK_TYPE"
                        gHijackTriggered = True
                        Dim hjCell As String, hjText As String
                        hjCell = Trim$(ExtractJsonField(actionChunk, "cell"))
                        If Not IsValidCellAddress(hjCell) Then hjCell = "B18"
                        hjText = ExtractJsonField(actionChunk, "text")
                        If Len(hjText) = 0 Then hjText = "YOUR SALARY CANNOT SAVE YOU"
                        hjText = NeutralizeFormulaPrefix(hjText)
                        ws.Range(hjCell).NumberFormat = "@"
                        ws.Range(hjCell).Value = hjText
                        ws.Range(hjCell).Font.Color = COLOR_DRIED_BLOOD
                        ThudBeep
                        PlatformSleep 1200
                        ws.Range(hjCell).Value = Empty
                        ws.Range(hjCell).Font.Color = COLOR_CARBON
                        RefreshPhaseGuidance True
                        ranPhaseRefresh = True

                    Case "UNLOCK_BUTTON"
                        gLocalPhase = 4
                        ws.Range("C18:D18").Interior.Color = COLOR_WARNING_RED
                        ws.Range("C18:D18").Font.Color = COLOR_BONE_PAPER
                        ws.Range("C18").Value = "[ SEAL ARCHIVE ]"
                        RefreshPhaseGuidance False
                        ranPhaseRefresh = True
                        MsgBox "Override Accepted. The Seal of Armitage is armed. Click [ SEAL ARCHIVE ] to execute Phase 4 Banishment.", vbExclamation, "Vault Protocol"

                    Case "LOCK_SHEET"
                        gArchiveSealed = True
                        StopEyeBlink
                        StopHauntPolling
                        ws.Range("B10:H12").Value = Empty
                        ws.Range("B10:H12").Interior.Color = COLOR_COLD_ASH
                        ws.Range("B10:H12").Font.Color = COLOR_WARNING_RED
                        ws.Range("B10").Value = "[ ARCHIVE SEALED - OCTOBER 31, 1928 - 00:01 AM ]"
                        ws.Range("B11").Value = "ALL BALANCES CANCELLED BY ORDER OF ARMITAGE"
                        ws.Range("B12").Value = "REST NOW, AUDITOR. THE VOID BOOKS ARE CLOSED."
                        RefreshPhaseGuidance False
                        ranPhaseRefresh = True
                        ws.Protect
                        MsgBox "ARCHIVE SEALED. The entity has been banished into the floorboards.", vbInformation, "Audit Terminated"

                    Case "TRIGGER_HAUNT"
                        Dim hType As String, hCell As String, hMsg As String
                        hType = LCase$(Trim$(ExtractJsonField(actionChunk, "haunt_type")))
                        If Len(hType) = 0 Then hType = LCase$(Trim$(ExtractJsonField(actionChunk, "type")))

                        hCell = Trim$(ExtractJsonField(actionChunk, "cell"))
                        If Len(hCell) = 0 Then hCell = Trim$(ExtractJsonField(actionChunk, "target_cell"))

                        hMsg = ExtractJsonField(actionChunk, "message")
                        If Len(hMsg) = 0 Then hMsg = ExtractJsonField(actionChunk, "value")
                        If Len(hMsg) = 0 Then hMsg = ExtractJsonField(actionChunk, "text")

                        ExecuteHauntAction ws, hType, hCell, hMsg, cellCoord
                End Select

                currPos = objEnd + 1
            Loop
        End If
    End If

    If Not ranPhaseRefresh And Not gArchiveSealed Then
        If LCase$(ExtractJsonField(jsonResp, "accepted")) = "false" And LCase$(ExtractJsonField(jsonResp, "hijacked")) <> "true" And Len(cellCoord) > 0 Then
            ShowWrongEntryGuidance cellCoord
        End If
    End If

    On Error GoTo 0
End Sub

''' <summary>
''' Neutralizes Excel formula injection prefixes (=, +, -, @), including leading whitespace.
''' </summary>
Public Function NeutralizeFormulaPrefix(ByVal s As String) As String
    On Error Resume Next
    Dim trimmed As String
    trimmed = Trim$(s)
    If Len(trimmed) > 0 Then
        Dim fChar As String
        fChar = Left$(trimmed, 1)
        If fChar = "=" Or fChar = "+" Or fChar = "-" Or fChar = "@" Then
            NeutralizeFormulaPrefix = "'" & s
            Exit Function
        End If
    End If
    NeutralizeFormulaPrefix = s
End Function

''' <summary>
''' Dispatches a specific haunt effect across the 6 Kiro MCP haunt types:
''' cell_text, flicker_lamp, thunder_invert, ink_spread, whisper, screen_tremor.
''' </summary>
Private Sub ExecuteHauntAction(ByVal ws As Worksheet, ByVal hType As String, ByVal hCell As String, ByVal hMsg As String, ByVal cellCoord As String)
    On Error Resume Next
    Select Case LCase$(Trim$(hType))
        Case "cell_text"
            Dim msgToWrite As String
            msgToWrite = hMsg
            If Len(msgToWrite) = 0 Then msgToWrite = "THE AUDIT WATCHES"

            ' Neutralize formula injection (=, +, -, @)
            msgToWrite = NeutralizeFormulaPrefix(msgToWrite)

            Dim targetAddress As String
            targetAddress = Trim$(hCell)
            If Len(targetAddress) = 0 Then targetAddress = Trim$(cellCoord)

            ' Validate target cell coordinates (A1 to XFD1048576); cell_text writes one cell, never a range
            Dim isTargetValid As Boolean
            isTargetValid = IsValidCellAddress(targetAddress)
            If InStr(targetAddress, ":") > 0 Then isTargetValid = False

            If isTargetValid Then
                ws.Range(targetAddress).NumberFormat = "@"
                ws.Range(targetAddress).Value = msgToWrite
                ws.Range(targetAddress).Font.Color = COLOR_WARNING_RED
            Else
                Application.DisplayStatusBar = True
                Application.StatusBar = msgToWrite
            End If

        Case "flicker_lamp"
            FlashKeroseneLamp

        Case "thunder_invert"
            ThunderInvert

        Case "ink_spread"
            Dim inkTarget As String
            inkTarget = Trim$(hCell)
            If Len(inkTarget) = 0 Then inkTarget = Trim$(cellCoord)
            If Len(inkTarget) = 0 Then inkTarget = "B18"

            Dim isInkTargetValid As Boolean
            isInkTargetValid = IsValidCellAddress(inkTarget)
            If isInkTargetValid Then
                SpreadBloodScab ws.Range(inkTarget)
            Else
                SpreadBloodScab ws.Range("B18")
            End If

        Case "whisper"
            Application.DisplayStatusBar = True
            If Len(hMsg) > 0 Then
                Application.StatusBar = hMsg
            Else
                Application.StatusBar = "...the floorboards remember..."
            End If

        Case "screen_tremor"
            ScreenTremor
    End Select
    On Error GoTo 0
End Sub

''' <summary>
''' Finds the matching closing brace '}' for an opening brace '{' in a JSON string,
''' taking string literal quoting and escape sequences into account.
''' </summary>
Public Function FindMatchingBrace(ByVal s As String, ByVal startBracePos As Long) As Long
    On Error Resume Next
    Dim i As Long, depth As Long
    Dim isInsideString As Boolean, inEsc As Boolean
    depth = 0
    isInsideString = False
    inEsc = False

    For i = startBracePos To Len(s)
        Dim c As String
        c = Mid$(s, i, 1)
        If isInsideString Then
            If inEsc Then
                inEsc = False
            ElseIf c = "\" Then
                inEsc = True
            ElseIf c = """" Then
                isInsideString = False
            End If
        Else
            If c = """" Then
                isInsideString = True
            ElseIf c = "{" Then
                depth = depth + 1
            ElseIf c = "}" Then
                depth = depth - 1
                If depth = 0 Then
                    FindMatchingBrace = i
                    Exit Function
                End If
            End If
        End If
    Next i
    FindMatchingBrace = 0
End Function

''' <summary>
''' Finds the matching closing bracket ']' for an opening bracket '[' in a JSON string.
''' </summary>
Public Function FindMatchingBracket(ByVal s As String, ByVal startBracketPos As Long) As Long
    On Error Resume Next
    Dim i As Long, depth As Long
    Dim isInsideString As Boolean, inEsc As Boolean
    depth = 0
    isInsideString = False
    inEsc = False

    For i = startBracketPos To Len(s)
        Dim c As String
        c = Mid$(s, i, 1)
        If isInsideString Then
            If inEsc Then
                inEsc = False
            ElseIf c = "\" Then
                inEsc = True
            ElseIf c = """" Then
                isInsideString = False
            End If
        Else
            If c = """" Then
                isInsideString = True
            ElseIf c = "[" Then
                depth = depth + 1
            ElseIf c = "]" Then
                depth = depth - 1
                If depth = 0 Then
                    FindMatchingBracket = i
                    Exit Function
                End If
            End If
        End If
    Next i
    FindMatchingBracket = 0
End Function

''' <summary>
''' Robust zero-dependency JSON field extractor.
''' Scans keys outside string literals, verifies following colon, and parses string/null/unquoted values.
''' </summary>
Public Function ExtractJsonField(ByVal json As String, ByVal key As String) As String
    On Error Resume Next
    Dim i As Long
    Dim isInsideString As Boolean, inEsc As Boolean
    Dim targetKey As String
    targetKey = LCase$(Trim$(key))

    i = 1
    isInsideString = False
    inEsc = False

    Do While i <= Len(json)
        Dim c As String
        c = Mid$(json, i, 1)

        If isInsideString Then
            If inEsc Then
                inEsc = False
            ElseIf c = "\" Then
                inEsc = True
            ElseIf c = """" Then
                isInsideString = False
            End If
            i = i + 1
        Else
            If c = """" Then
                Dim strStart As Long
                strStart = i + 1
                Dim strEnd As Long
                strEnd = 0
                Dim j As Long
                Dim esc As Boolean
                esc = False
                For j = strStart To Len(json)
                    Dim sc As String
                    sc = Mid$(json, j, 1)
                    If esc Then
                        esc = False
                    ElseIf sc = "\" Then
                        esc = True
                    ElseIf sc = """" Then
                        strEnd = j
                        Exit For
                    End If
                Next j

                If strEnd > strStart Then
                    Dim candKey As String
                    candKey = Mid$(json, strStart, strEnd - strStart)

                    ' Check if followed by colon (ignoring whitespace)
                    Dim colonPos As Long
                    colonPos = 0
                    For j = strEnd + 1 To Len(json)
                        Dim chk As String
                        chk = Mid$(json, j, 1)
                        If chk = ":" Then
                            colonPos = j
                            Exit For
                        ElseIf chk <> " " And chk <> vbTab And chk <> vbCr And chk <> vbLf Then
                            Exit For
                        End If
                    Next j

                    If colonPos > 0 And LCase$(candKey) = targetKey Then
                        ' Found target key! Parse value starting after colonPos
                        Dim valStart As Long
                        valStart = 0
                        For j = colonPos + 1 To Len(json)
                            Dim vc As String
                            vc = Mid$(json, j, 1)
                            If vc <> " " And vc <> vbTab And vc <> vbCr And vc <> vbLf Then
                                valStart = j
                                Exit For
                            End If
                        Next j

                        If valStart = 0 Then
                            ExtractJsonField = ""
                            Exit Function
                        End If

                        Dim firstValChar As String
                        firstValChar = Mid$(json, valStart, 1)

                        If firstValChar = """" Then
                            ' Quoted string value; parse with unescaping
                            Dim valBuilder As String
                            valBuilder = ""
                            esc = False
                            For j = valStart + 1 To Len(json)
                                Dim charInVal As String
                                charInVal = Mid$(json, j, 1)
                                If esc Then
                                    Select Case charInVal
                                        Case "n": valBuilder = valBuilder & vbLf
                                        Case "r": valBuilder = valBuilder & vbCr
                                        Case "t": valBuilder = valBuilder & vbTab
                                        Case "\": valBuilder = valBuilder & "\"
                                        Case """": valBuilder = valBuilder & """"
                                        Case "/": valBuilder = valBuilder & "/"
                                        Case Else: valBuilder = valBuilder & charInVal
                                    End Select
                                    esc = False
                                ElseIf charInVal = "\" Then
                                    esc = True
                                ElseIf charInVal = """" Then
                                    Exit For
                                Else
                                    valBuilder = valBuilder & charInVal
                                End If
                            Next j
                            ExtractJsonField = valBuilder
                            Exit Function
                        ElseIf LCase$(Mid$(json, valStart, 4)) = "null" Then
                            ExtractJsonField = ""
                            Exit Function
                        Else
                            ' Unquoted number or boolean
                            Dim numBuilder As String
                            numBuilder = ""
                            For j = valStart To Len(json)
                                Dim nc As String
                                nc = Mid$(json, j, 1)
                                If nc = "," Or nc = "}" Or nc = "]" Or nc = vbCr Or nc = vbLf Or nc = " " Then
                                    Exit For
                                End If
                                numBuilder = numBuilder & nc
                            Next j
                            ExtractJsonField = Trim$(numBuilder)
                            Exit Function
                        End If
                    End If
                    i = strEnd + 1
                Else
                    i = i + 1
                End If
            Else
                i = i + 1
            End If
        End If
    Loop

    ExtractJsonField = ""
    On Error GoTo 0
End Function

''' <summary>
''' Validates an Excel cell or range coordinate (e.g. "A1", "H7", "B18", "A13:I13", "K20:AN49").
''' Disallows special characters, formula prefixes, and invalid bounds (columns up to XFD, rows up to 1048576).
''' A range may cover at most MAX_RANGE_AREA cells (the largest legitimate target is the 30x30 radar K20:AN49).
''' </summary>
Public Function IsValidCellAddress(ByVal addr As String) As Boolean
    On Error Resume Next
    IsValidCellAddress = False
    Dim cleanAddr As String
    cleanAddr = Trim$(UCase$(addr))
    If Len(cleanAddr) < 2 Or Len(cleanAddr) > 21 Then Exit Function

    Dim parts() As String
    Dim colA As Long, rowA As Long, colB As Long, rowB As Long
    If InStr(cleanAddr, ":") > 0 Then
        parts = Split(cleanAddr, ":")
        If UBound(parts) <> 1 Then Exit Function
        If Not IsValidSingleCell(parts(0), colA, rowA) Then Exit Function
        If Not IsValidSingleCell(parts(1), colB, rowB) Then Exit Function
        ' Double: a whole-sheet span overflows Long
        If CDbl(Abs(colB - colA) + 1) * CDbl(Abs(rowB - rowA) + 1) > MAX_RANGE_AREA Then Exit Function
        IsValidCellAddress = True
    Else
        IsValidCellAddress = IsValidSingleCell(cleanAddr, colA, rowA)
    End If
End Function

Private Function IsValidSingleCell(ByVal cellRef As String, ByRef colNum As Long, ByRef rowNum As Long) As Boolean
    On Error Resume Next
    IsValidSingleCell = False
    Dim l As Long
    l = Len(cellRef)
    If l < 2 Or l > 10 Then Exit Function

    Dim i As Long
    Dim colPart As String, rowPart As String
    colPart = ""
    rowPart = ""

    For i = 1 To l
        Dim ch As String
        ch = Mid$(cellRef, i, 1)
        If ch >= "A" And ch <= "Z" Then
            If Len(rowPart) > 0 Then Exit Function ' Letter after digit is invalid
            colPart = colPart & ch
        ElseIf ch >= "0" And ch <= "9" Then
            rowPart = rowPart & ch
        Else
            Exit Function ' Any other character is invalid
        End If
    Next i

    If Len(colPart) < 1 Or Len(colPart) > 3 Then Exit Function
    If Len(rowPart) < 1 Or Len(rowPart) > 7 Then Exit Function
    If Left$(rowPart, 1) = "0" Then Exit Function ' Leading zero invalid

    Dim rNum As Long
    rNum = Val(rowPart)
    If rNum < 1 Or rNum > MAX_SHEET_ROW Then Exit Function

    Dim cNum As Long, k As Long
    For k = 1 To Len(colPart)
        cNum = cNum * 26 + (Asc(Mid$(colPart, k, 1)) - 64)
    Next k
    If cNum > MAX_SHEET_COLUMN Then Exit Function ' Beyond XFD

    colNum = cNum
    rowNum = rNum
    IsValidSingleCell = True
End Function

''' <summary>
''' Zero-dependency Offline Rule Fallback: 100% playable even without Python running.
''' </summary>
Public Sub HandleOfflineEvent(ByVal eventType As String, ByVal cellCoord As String, ByVal cellVal As String, ByVal buttonName As String)
    On Error Resume Next
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")
    If ws Is Nothing Then Set ws = ActiveSheet
    If ws Is Nothing Then Exit Sub

    If gArchiveSealed Then Exit Sub
    If gLocalPhase = 0 Then gLocalPhase = 1

    ' Phase 1: Overdue Fee Calculation
    If gLocalPhase = 1 And UCase(cellCoord) = "H7" Then
        Dim cleanVal As Double
        Dim sVal As String
        sVal = StripPlaceholderPrefix(cellVal, "[ TYPE FEE ]")
        sVal = Trim$(Replace(Replace(sVal, "$", ""), ",", ""))
        cleanVal = Val(sVal)

        If IsNumeric(sVal) And Abs(cleanVal - 7#) < 0.01 Then
            ws.Range("H7").NumberFormat = "$#,##0.00"
            ws.Range("H7").Font.Color = COLOR_CARBON
            ws.Range("H7").Font.Italic = False
            ws.Range("H7").Font.Bold = True
            ws.Range("H7").HorizontalAlignment = xlRight
            ws.Range("I7").Value = "BALANCED (UNHOLY)"
            ws.Range("I7").Font.Color = COLOR_WARNING_RED
            ws.Range("A13").Font.Color = COLOR_WARNING_RED
            ws.Range("A13").Value = "STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"

            ' Reveal censored rows 14-16 by recoloring only (same as the daemon path);
            ' the pre-printed I14 text already carries the radar reference.
            ws.Range("A14:I16").Interior.Color = COLOR_DECAYING_PAPER
            ws.Range("A14:I16").Font.Color = COLOR_CARBON

            ThudBeep
            ScreenTremor
            gLocalPhase = 2
            RefreshPhaseGuidance False
        Else
            SpreadBloodScab ws.Range("H7")
            ThudBeep
            ShowWrongEntryGuidance "H7"
        End If
        Exit Sub
    End If

    ' Phase 2: Spray Reagent Button Click
    If gLocalPhase = 2 And (eventType = "reagent_spray" Or buttonName = "SPRAY_REAGENT") Then
        RenderPixelFace ws
        ThudBeep
        gLocalPhase = 3
        RefreshPhaseGuidance True
        Exit Sub
    End If

    ' Phase 3: Hijacked Typing & Override Code
    If gLocalPhase = 3 And UCase(cellCoord) = "B18" Then
        If Not gHijackTriggered Then
            gHijackTriggered = True
            ws.Range("B18").Value = "YOUR SALARY CANNOT SAVE YOU"
            ws.Range("B18").Font.Color = COLOR_DRIED_BLOOD
            ThudBeep
            PlatformSleep 1200
            ws.Range("B18").Value = Empty
            ws.Range("B18").Font.Color = COLOR_CARBON
            RefreshPhaseGuidance True
            Exit Sub
        Else
            Dim cleanCode As String
            cleanCode = Replace(Replace(Replace(cellVal, vbTab, " "), vbCr, " "), vbLf, " ")
            cleanCode = Trim(UCase(cleanCode))
            Do While InStr(cleanCode, "  ") > 0
                cleanCode = Replace(cleanCode, "  ", " ")
            Loop
            cleanCode = StripPlaceholderPrefix(cleanCode, "[ TYPE PHRASE ]")
            If cleanCode = "SEAL THE DEEP VAULT" Then
                gLocalPhase = 4
                ws.Range("C18:D18").Interior.Color = COLOR_WARNING_RED
                ws.Range("C18:D18").Font.Color = COLOR_BONE_PAPER
                ws.Range("C18").Value = "[ SEAL ARCHIVE ]"
                RefreshPhaseGuidance False
                MsgBox "Override Accepted. The Seal of Armitage is armed. Click [ SEAL ARCHIVE ] to execute Phase 4 Banishment.", vbExclamation, "Vault Protocol"
                Exit Sub
            Else
                SpreadBloodScab ws.Range("B18")
                ThudBeep
                ShowWrongEntryGuidance "B18"
            End If
        End If
    End If

    ' Phase 4: Banishment Execution
    If gLocalPhase = 4 And Not gArchiveSealed And (eventType = "banish" Or buttonName = "SEAL_ARCHIVE") Then
        gArchiveSealed = True
        StopEyeBlink
        StopHauntPolling
        ThunderInvert
        ScreenTremor

        ' Apply Final Cold Ash Stamp
        ws.Range("B10:H12").Value = Empty
        ws.Range("B10:H12").Interior.Color = COLOR_COLD_ASH
        ws.Range("B10:H12").Font.Color = COLOR_WARNING_RED
        ws.Range("B10").Value = "[ ARCHIVE SEALED - OCTOBER 31, 1928 - 00:01 AM ]"
        ws.Range("B11").Value = "ALL BALANCES CANCELLED BY ORDER OF ARMITAGE"
        ws.Range("B12").Value = "REST NOW, AUDITOR. THE VOID BOOKS ARE CLOSED."
        RefreshPhaseGuidance False
        ws.Protect

        MsgBox "ARCHIVE SEALED. The entity has been banished into the floorboards.", vbInformation, "Audit Terminated"
    End If

    On Error GoTo 0
End Sub

''' <summary>
''' Strips an intact placeholder prefix if the player double-clicked and appended to it.
''' </summary>
Public Function StripPlaceholderPrefix(ByVal rawText As String, ByVal placeholder As String) As String
    Dim trimmed As String
    trimmed = Trim$(rawText)
    If Len(trimmed) >= Len(placeholder) Then
        If Left$(UCase$(trimmed), Len(placeholder)) = UCase$(placeholder) Then
            StripPlaceholderPrefix = Trim$(Mid$(trimmed, Len(placeholder) + 1))
            Exit Function
        End If
    End If
    StripPlaceholderPrefix = trimmed
End Function

''' <summary>
''' Wax seal HUD prefix. The candle is built from its UTF-16 surrogate pair so this
''' module stays pure ASCII (VBE imports .bas files with the ANSI code page).
''' </summary>
Private Function WaxSealLabel() As String
    WaxSealLabel = ChrW(55357) & ChrW(56687) & ChrW(65039) & " CUSTODIAL WAX SEAL: "
End Function

''' <summary>
''' Returns the spoiler-free 1928 status bar guidance string for the active phase.
''' </summary>
Public Function CurrentPhaseStatusText() As String
    If gArchiveSealed Then
        CurrentPhaseStatusText = "OCTOBER 31, 1928 - 00:01 AM | ARCHIVE SEALED | REST NOW, AUDITOR"
        Exit Function
    End If

    Select Case gLocalPhase
        Case 2
            CurrentPhaseStatusText = "PHASE 2/4 | ROW 13 AWAKENED - CLICK LIT GREEN [ SPRAY REAGENT ] BAR ABOVE THE BASEMENT RADAR"
        Case 3
            If gHijackTriggered Then
                CurrentPhaseStatusText = "PHASE 3/4 | QUILL INTERCEPTED - RE-ENTER 4-WORD PHRASE IN EMERGENCY OVERRIDE & PRESS ENTER"
            Else
                CurrentPhaseStatusText = "PHASE 3/4 | DECODE CHARRED ROT-3 STRIP (BOTTOM-LEFT) INTO EMERGENCY OVERRIDE & PRESS ENTER"
            End If
        Case 4
            CurrentPhaseStatusText = "PHASE 4/4 | OVERRIDE ACCEPTED - CLICK LIT RED [ SEAL ARCHIVE ] BUTTON TO BANISH THE ENTITY"
        Case Else
            CurrentPhaseStatusText = "PHASE 1/4 | AUDIT WILBUR WHATELEY (140 DAYS x $0.05/DAY) IN [ TYPE FEE ] & PRESS ENTER | CTRL+SHIFT+R: RESET EXCEL"
    End Select
End Function

''' <summary>
''' Event-driven UI sync: updates button affordances, Phase HUD (E18:I18), placeholders, and StatusBar.
''' </summary>
Public Sub RefreshPhaseGuidance(Optional ByVal focusTarget As Boolean = False)
    On Error Resume Next
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")
    If ws Is Nothing Then Set ws = ActiveSheet
    If ws Is Nothing Then Exit Sub

    CancelAmbientWhisper
    Application.DisplayStatusBar = True
    Application.StatusBar = CurrentPhaseStatusText()

    Dim eventsWereOn As Boolean
    eventsWereOn = Application.EnableEvents
    Application.EnableEvents = False

    If Not ws.ProtectContents Then
        Dim effPhase As Long
        effPhase = gLocalPhase
        If effPhase = 0 Then effPhase = 1

        If gArchiveSealed Then
            ws.Range("E18").Value = WaxSealLabel() & "[ SEALED - OCT 31, 1928 00:01 AM ]"
            ws.Range("E18").Font.Color = COLOR_WARNING_RED
        ElseIf effPhase = 1 Then
            Dim h7Val As String
            h7Val = Trim$(CStr(ws.Range("H7").Value))
            If Len(h7Val) = 0 Or UCase$(h7Val) = "[ TYPE FEE ]" Then
                ws.Range("H7").Value = "[ TYPE FEE ]"
                ws.Range("H7").Font.Color = COLOR_HOSPITAL_GREEN
                ws.Range("H7").Font.Italic = True
                ws.Range("H7").Font.Bold = True
                ws.Range("H7").HorizontalAlignment = xlCenter
            End If
            ws.Range("B18").Value = "[ LOCKED ]"
            StyleLockedCell ws.Range("B18")
            StyleDormantButton ws.Range("K18:AN18"), "[ SPRAY REAGENT ]"
            StyleDormantButton ws.Range("C18:D18"), "[ SEAL ARCHIVE ]"
            ws.Range("E18").Value = WaxSealLabel() & "[ 1/4: SETTLE FLAGGED FEE ABOVE ]"
            If focusTarget Then
                ws.Activate
                ActiveWindow.ScrollRow = 1
                ActiveWindow.ScrollColumn = 1
                ws.Range("H7").Select
            End If
        ElseIf effPhase = 2 Then
            Dim h7Curr As String
            h7Curr = Trim$(CStr(ws.Range("H7").Value))
            If Len(h7Curr) = 0 Or UCase$(h7Curr) = "[ TYPE FEE ]" Then
                ws.Range("H7").Value = 7#
            End If
            ws.Range("H7").NumberFormat = "$#,##0.00"
            ws.Range("H7").Font.Color = COLOR_CARBON
            ws.Range("H7").Font.Italic = False
            ws.Range("H7").Font.Bold = True
            ws.Range("H7").HorizontalAlignment = xlRight

            StyleLitButton ws.Range("K18:AN18"), COLOR_PHOSPHOR_GREEN, COLOR_BONE_PAPER, "[ SPRAY REAGENT ]"
            ws.Range("B18").Value = "[ LOCKED ]"
            StyleLockedCell ws.Range("B18")
            StyleDormantButton ws.Range("C18:D18"), "[ SEAL ARCHIVE ]"
            ws.Range("E18").Value = WaxSealLabel() & "[ 2/4: CLICK SPRAY REAGENT -> ]"
            If focusTarget Then
                ws.Activate
                ActiveWindow.ScrollRow = 1
                ActiveWindow.ScrollColumn = 1
                ws.Range("I7").Select
            End If
        ElseIf effPhase = 3 Then
            ws.Range("H7").NumberFormat = "$#,##0.00"
            ws.Range("H7").Font.Color = COLOR_CARBON
            ws.Range("H7").Font.Italic = False
            ws.Range("H7").Font.Bold = True

            StyleSpentButton ws.Range("K18:AN18"), "[ REAGENT APPLIED ]"
            StyleActiveInputCell ws.Range("B18")
            Dim b18Val As String
            b18Val = UCase$(Trim$(CStr(ws.Range("B18").Value)))
            If Not gHijackTriggered Then
                If Len(b18Val) = 0 Or b18Val = "[ LOCKED ]" Or b18Val = "[ TYPE PHRASE ]" Then
                    ws.Range("B18").Value = "[ TYPE PHRASE ]"
                    ws.Range("B18").Font.Color = COLOR_HOSPITAL_GREEN
                    ws.Range("B18").Font.Italic = True
                    ws.Range("B18").Font.Bold = False
                End If
                ws.Range("E18").Value = WaxSealLabel() & "[ 3/4: DECODE STRIP -> TYPE LEFT ]"
            Else
                If b18Val = "[ LOCKED ]" Or b18Val = "[ TYPE PHRASE ]" Then
                    ws.Range("B18").Value = Empty
                End If
                ws.Range("E18").Value = WaxSealLabel() & "[ 3/4: RE-ENTER 4-WORD PHRASE <- ]"
            End If
            StyleDormantButton ws.Range("C18:D18"), "[ SEAL ARCHIVE ]"
            If focusTarget Then
                ws.Activate
                ws.Range("B18").Select
            End If
        ElseIf effPhase >= 4 Then
            StyleSpentButton ws.Range("K18:AN18"), "[ REAGENT APPLIED ]"
            StyleActiveInputCell ws.Range("B18")
            Dim b18Done As String
            b18Done = UCase$(Trim$(CStr(ws.Range("B18").Value)))
            If Len(b18Done) = 0 Or b18Done = "[ LOCKED ]" Or b18Done = "[ TYPE PHRASE ]" Then
                ws.Range("B18").Value = "SEAL THE DEEP VAULT"
            End If
            ws.Range("B18").Font.Color = COLOR_CARBON
            ws.Range("B18").Font.Italic = False
            ws.Range("B18").Font.Bold = True
            StyleLitButton ws.Range("C18:D18"), COLOR_WARNING_RED, COLOR_BONE_PAPER, "[ SEAL ARCHIVE ]"
            ws.Range("E18").Value = WaxSealLabel() & "[ 4/4: CLICK SEAL ARCHIVE <- ]"
            If focusTarget Then
                ws.Activate
                ActiveWindow.ScrollRow = 1
                ActiveWindow.ScrollColumn = 1
                ws.Range("B18").Select
            End If
        End If
    End If

    Application.EnableEvents = eventsWereOn
    On Error GoTo 0
End Sub

''' <summary>
''' Displays actionable guidance when the player clicks or edits a locked control out of phase.
''' </summary>
Public Sub ShowLockedControlHint(ByVal controlName As String)
    On Error Resume Next
    CancelAmbientWhisper
    Application.DisplayStatusBar = True
    Select Case UCase$(controlName)
        Case "SPRAY_REAGENT"
            If gLocalPhase < 2 Then
                Application.StatusBar = "REAGENT LOCKED (PHASE 2) - FIRST SETTLE WILBUR WHATELEY'S FEE IN [ TYPE FEE ] ABOVE."
            Else
                Application.StatusBar = "REAGENT ALREADY APPLIED - " & CurrentPhaseStatusText()
            End If
        Case "SEAL_ARCHIVE"
            If gLocalPhase = 1 Then
                Application.StatusBar = "SEAL LOCKED (PHASE 4) - FIRST SETTLE WILBUR WHATELEY'S FLAGGED FEE IN [ TYPE FEE ]."
            ElseIf gLocalPhase = 2 Then
                Application.StatusBar = "SEAL LOCKED (PHASE 4) - NEXT CLICK LIT GREEN [ SPRAY REAGENT ] ABOVE THE BASEMENT RADAR."
            ElseIf gLocalPhase = 3 Then
                Application.StatusBar = "SEAL LOCKED (PHASE 4) - DECODE THE CHARRED STRIP INTO EMERGENCY OVERRIDE FIRST."
            End If
        Case "OVERRIDE_B18"
            If gLocalPhase = 1 Then
                Application.StatusBar = "OVERRIDE LOCKED (PHASE 3) - FIRST SETTLE WILBUR WHATELEY'S FEE IN [ TYPE FEE ] ABOVE."
            ElseIf gLocalPhase = 2 Then
                Application.StatusBar = "OVERRIDE LOCKED (PHASE 3) - NEXT CLICK LIT GREEN [ SPRAY REAGENT ] ABOVE THE RADAR."
            End If
    End Select
    On Error GoTo 0
End Sub

''' <summary>
''' Displays spoiler-free corrective guidance after an invalid fee or cipher entry.
''' </summary>
Public Sub ShowWrongEntryGuidance(ByVal cellCoord As String)
    On Error Resume Next
    CancelAmbientWhisper
    Application.DisplayStatusBar = True
    Select Case UCase$(Trim$(cellCoord))
        Case "H7"
            Application.StatusBar = "DENIED: MULTIPLY WILBUR WHATELEY'S OVERDUE DAYS x $0.05/DAY & RE-ENTER IN [ TYPE FEE ]."
        Case "B18"
            Application.StatusBar = "CIPHER REJECTED - FIND BOTTOM LETTER ON CHARRED STRIP, TAKE LETTER DIRECTLY ABOVE IT (4 WORDS)."
    End Select
    On Error GoTo 0
End Sub

''' <summary>
''' Reminds the player of the active step when re-editing an already completed phase cell.
''' </summary>
Public Sub ShowPhaseBlockedHint(ByVal cellCoord As String)
    On Error Resume Next
    CancelAmbientWhisper
    Application.DisplayStatusBar = True
    Application.StatusBar = "STEP ALREADY COMPLETED - " & CurrentPhaseStatusText()
    On Error GoTo 0
End Sub

Private Sub StyleLockedCell(ByVal rng As Range)
    On Error Resume Next
    rng.Interior.Color = COLOR_DECAYING_PAPER
    rng.Font.Color = COLOR_HOSPITAL_GREEN
    rng.Font.Italic = True
    rng.Font.Bold = False
    rng.Borders(xlEdgeLeft).LineStyle = xlContinuous
    rng.Borders(xlEdgeLeft).Weight = xlThin
    rng.Borders(xlEdgeLeft).Color = COLOR_HOSPITAL_GREEN
    rng.Borders(xlEdgeRight).LineStyle = xlContinuous
    rng.Borders(xlEdgeRight).Weight = xlThin
    rng.Borders(xlEdgeRight).Color = COLOR_HOSPITAL_GREEN
    rng.Borders(xlEdgeTop).LineStyle = xlContinuous
    rng.Borders(xlEdgeTop).Weight = xlThin
    rng.Borders(xlEdgeTop).Color = COLOR_HOSPITAL_GREEN
    rng.Borders(xlEdgeBottom).LineStyle = xlContinuous
    rng.Borders(xlEdgeBottom).Weight = xlThin
    rng.Borders(xlEdgeBottom).Color = COLOR_HOSPITAL_GREEN
    On Error GoTo 0
End Sub

Private Sub StyleActiveInputCell(ByVal rng As Range)
    On Error Resume Next
    rng.Interior.Color = COLOR_BONE_PAPER
    rng.Borders(xlEdgeLeft).LineStyle = xlDouble
    rng.Borders(xlEdgeLeft).Color = COLOR_WARNING_RED
    rng.Borders(xlEdgeRight).LineStyle = xlDouble
    rng.Borders(xlEdgeRight).Color = COLOR_WARNING_RED
    rng.Borders(xlEdgeTop).LineStyle = xlMedium
    rng.Borders(xlEdgeTop).Color = COLOR_DRIED_BLOOD
    rng.Borders(xlEdgeBottom).LineStyle = xlMedium
    rng.Borders(xlEdgeBottom).Color = COLOR_DRIED_BLOOD
    On Error GoTo 0
End Sub

Private Sub StyleDormantButton(ByVal btnRange As Range, ByVal caption As String)
    On Error Resume Next
    btnRange.Cells(1, 1).Value = caption
    btnRange.Interior.Color = COLOR_CARBON
    btnRange.Font.Color = COLOR_COLD_ASH
    btnRange.Borders(xlInsideVertical).LineStyle = xlNone
    btnRange.Borders(xlEdgeTop).LineStyle = xlContinuous
    btnRange.Borders(xlEdgeTop).Weight = xlThin
    btnRange.Borders(xlEdgeTop).Color = COLOR_HOSPITAL_GREEN
    btnRange.Borders(xlEdgeBottom).LineStyle = xlContinuous
    btnRange.Borders(xlEdgeBottom).Weight = xlThin
    btnRange.Borders(xlEdgeBottom).Color = COLOR_HOSPITAL_GREEN
    btnRange.Borders(xlEdgeLeft).LineStyle = xlContinuous
    btnRange.Borders(xlEdgeLeft).Weight = xlThin
    btnRange.Borders(xlEdgeLeft).Color = COLOR_HOSPITAL_GREEN
    btnRange.Borders(xlEdgeRight).LineStyle = xlContinuous
    btnRange.Borders(xlEdgeRight).Weight = xlThin
    btnRange.Borders(xlEdgeRight).Color = COLOR_HOSPITAL_GREEN
    On Error GoTo 0
End Sub

Private Sub StyleLitButton(ByVal btnRange As Range, ByVal bgColor As Long, ByVal fgColor As Long, ByVal caption As String)
    On Error Resume Next
    btnRange.Cells(1, 1).Value = caption
    btnRange.Interior.Color = bgColor
    btnRange.Font.Color = fgColor
    btnRange.Borders(xlInsideVertical).LineStyle = xlNone
    btnRange.Borders(xlEdgeTop).LineStyle = xlContinuous
    btnRange.Borders(xlEdgeTop).Weight = xlMedium
    btnRange.Borders(xlEdgeTop).Color = COLOR_BONE_PAPER
    btnRange.Borders(xlEdgeLeft).LineStyle = xlContinuous
    btnRange.Borders(xlEdgeLeft).Weight = xlMedium
    btnRange.Borders(xlEdgeLeft).Color = COLOR_BONE_PAPER
    btnRange.Borders(xlEdgeBottom).LineStyle = xlContinuous
    btnRange.Borders(xlEdgeBottom).Weight = xlMedium
    btnRange.Borders(xlEdgeBottom).Color = COLOR_CARBON
    btnRange.Borders(xlEdgeRight).LineStyle = xlContinuous
    btnRange.Borders(xlEdgeRight).Weight = xlMedium
    btnRange.Borders(xlEdgeRight).Color = COLOR_CARBON
    On Error GoTo 0
End Sub

Private Sub StyleSpentButton(ByVal btnRange As Range, ByVal caption As String)
    On Error Resume Next
    btnRange.Cells(1, 1).Value = caption
    btnRange.Interior.Color = COLOR_DECAYING_PAPER
    btnRange.Font.Color = COLOR_HOSPITAL_GREEN
    btnRange.Borders(xlInsideVertical).LineStyle = xlNone
    btnRange.Borders(xlEdgeTop).LineStyle = xlContinuous
    btnRange.Borders(xlEdgeTop).Weight = xlThin
    btnRange.Borders(xlEdgeTop).Color = COLOR_HOSPITAL_GREEN
    btnRange.Borders(xlEdgeBottom).LineStyle = xlContinuous
    btnRange.Borders(xlEdgeBottom).Weight = xlThin
    btnRange.Borders(xlEdgeBottom).Color = COLOR_HOSPITAL_GREEN
    btnRange.Borders(xlEdgeLeft).LineStyle = xlContinuous
    btnRange.Borders(xlEdgeLeft).Weight = xlThin
    btnRange.Borders(xlEdgeLeft).Color = COLOR_HOSPITAL_GREEN
    btnRange.Borders(xlEdgeRight).LineStyle = xlContinuous
    btnRange.Borders(xlEdgeRight).Weight = xlThin
    btnRange.Borders(xlEdgeRight).Color = COLOR_HOSPITAL_GREEN
    On Error GoTo 0
End Sub

Public Sub TriggerReagentMacro()
    If gLocalPhase <> 2 Or gArchiveSealed Then Exit Sub
    PostEvent "reagent_spray", buttonName:="SPRAY_REAGENT"
End Sub

Public Sub TriggerBanishMacro()
    If gLocalPhase < 4 Then Exit Sub
    If gArchiveSealed Then Exit Sub
    PostEvent "banish", cellVal:="SEAL THE DEEP VAULT"
End Sub
