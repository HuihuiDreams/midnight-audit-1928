Attribute VB_Name = "M_DaemonBridge"
Option Explicit

' ==============================================================================
' The Midnight Audit (1928) - M_DaemonBridge.bas
' HTTP Communication Bridge with FastAPI Daemon + Zero-Dependency Offline Fallback
' ==============================================================================

Private Const DAEMON_URL As String = "http://127.0.0.1:8000/api"
Public gLocalPhase As Long
Public gHijackTriggered As Boolean

''' <summary>
''' Dispatches an event to the local Python daemon or routes to offline fallback.
''' </summary>
Public Sub PostEvent(ByVal eventType As String, Optional ByVal cellCoord As String = "", Optional ByVal cellVal As String = "", Optional ByVal buttonName As String = "")
    On Error GoTo FallbackHandler
    
    Dim jsonPayload As String
    jsonPayload = "{""event_type"":""" & eventType & """,""cell"":""" & cellCoord & """,""value"":""" & Replace(cellVal, """", "\""") & """,""button"":""" & buttonName & """}"
    
    #If Mac Then
        ' Mac curl transport
        Dim cmd As String
        Dim respText As String
        cmd = "curl -s -m 1 -X POST " & DAEMON_URL & "/event -H ""Content-Type: application/json"" -d '" & jsonPayload & "'"
        respText = MacScript("do shell script """ & Replace(cmd, """", "\""") & """")
        If Len(respText) > 0 And InStr(respText, "accepted") > 0 Then
            ProcessDaemonResponse respText, cellCoord
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
        End If
    #End If

FallbackHandler:
    ' Python daemon is not running; seamlessly route to local offline rule engine
    HandleOfflineEvent eventType, cellCoord, cellVal, buttonName
End Sub

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
    Else
        If InStr(1, jsonResp, """current_phase"": 2", vbTextCompare) > 0 Or InStr(1, jsonResp, """current_phase"":2", vbTextCompare) > 0 Then
            gLocalPhase = 2
        ElseIf InStr(1, jsonResp, """current_phase"": 3", vbTextCompare) > 0 Or InStr(1, jsonResp, """current_phase"":3", vbTextCompare) > 0 Then
            gLocalPhase = 3
        ElseIf InStr(1, jsonResp, """current_phase"": 4", vbTextCompare) > 0 Or InStr(1, jsonResp, """current_phase"":4", vbTextCompare) > 0 Then
            gLocalPhase = 4
        End If
    End If
    
    ' Check for FX triggers
    If InStr(1, jsonResp, "THUD_BEEP", vbTextCompare) > 0 Then
        ThudBeep
    End If
    If InStr(1, jsonResp, "SCREEN_TREMOR", vbTextCompare) > 0 Then
        ScreenTremor
    End If
    If InStr(1, jsonResp, "THUNDER_STROBE", vbTextCompare) > 0 Then
        ThunderInvert
    End If
    
    ' Error reaction: spread dried blood scab
    If InStr(1, jsonResp, "SPREAD_BLOOD_SCAB", vbTextCompare) > 0 Then
        If Len(cellCoord) > 0 Then
            SpreadBloodScab ws.Range(cellCoord)
        ElseIf gLocalPhase = 1 Then
            SpreadBloodScab ws.Range("H7")
        ElseIf gLocalPhase = 3 Then
            SpreadBloodScab ws.Range("B18")
        End If
    End If
    
    ' Live Kiro MCP haunt triggers: process all TRIGGER_HAUNT actions
    ' First, parse actions from the "actions" array if present
    Dim posActions As Long
    posActions = InStr(1, jsonResp, """actions""", vbTextCompare)
    If posActions > 0 Then
        Dim posArrStart As Long
        posArrStart = InStr(posActions, jsonResp, "[")
        If posArrStart > 0 Then
            Dim currPos As Long
            currPos = posArrStart + 1
            Do
                Dim objStart As Long
                objStart = InStr(currPos, jsonResp, "{")
                If objStart = 0 Then Exit Do
                
                Dim arrEnd As Long
                arrEnd = InStr(currPos, jsonResp, "]")
                If arrEnd > 0 And objStart > arrEnd Then Exit Do
                
                Dim objEnd As Long
                objEnd = FindMatchingBrace(jsonResp, objStart)
                If objEnd = 0 Then Exit Do
                
                Dim actionChunk As String
                actionChunk = Mid$(jsonResp, objStart, objEnd - objStart + 1)
                
                Dim cmd As String
                cmd = UCase$(Trim$(ExtractJsonField(actionChunk, "command")))
                
                If cmd = "TRIGGER_HAUNT" Or InStr(1, actionChunk, "TRIGGER_HAUNT", vbTextCompare) > 0 Then
                    Dim hType As String, hCell As String, hMsg As String
                    hType = LCase$(Trim$(ExtractJsonField(actionChunk, "haunt_type")))
                    If Len(hType) = 0 Then hType = LCase$(Trim$(ExtractJsonField(actionChunk, "type")))
                    
                    hCell = Trim$(ExtractJsonField(actionChunk, "cell"))
                    If Len(hCell) = 0 Then hCell = Trim$(ExtractJsonField(actionChunk, "target_cell"))
                    
                    hMsg = ExtractJsonField(actionChunk, "message")
                    If Len(hMsg) = 0 Then hMsg = ExtractJsonField(actionChunk, "value")
                    If Len(hMsg) = 0 Then hMsg = ExtractJsonField(actionChunk, "text")
                    
                    ExecuteHauntAction ws, hType, hCell, hMsg, cellCoord
                End If
                
                currPos = objEnd + 1
            Loop
        End If
    End If
    
    ' Also process standalone or flat TRIGGER_HAUNT if not inside actions array
    If posActions = 0 And InStr(1, jsonResp, "TRIGGER_HAUNT", vbTextCompare) > 0 Then
        Dim flatSearchPos As Long
        flatSearchPos = 1
        Do
            Dim fHauntPos As Long
            fHauntPos = InStr(flatSearchPos, jsonResp, "TRIGGER_HAUNT", vbTextCompare)
            If fHauntPos = 0 Then Exit Do
            
            Dim fObjStart As Long, fObjEnd As Long
            fObjStart = InStrRev(jsonResp, "{", fHauntPos)
            If fObjStart > 0 Then
                fObjEnd = FindMatchingBrace(jsonResp, fObjStart)
                If fObjEnd > 0 Then
                    Dim fActionChunk As String
                    fActionChunk = Mid$(jsonResp, fObjStart, fObjEnd - fObjStart + 1)
                    
                    Dim fhType As String, fhCell As String, fhMsg As String
                    fhType = LCase$(Trim$(ExtractJsonField(fActionChunk, "haunt_type")))
                    If Len(fhType) = 0 Then fhType = LCase$(Trim$(ExtractJsonField(fActionChunk, "type")))
                    
                    fhCell = Trim$(ExtractJsonField(fActionChunk, "cell"))
                    If Len(fhCell) = 0 Then fhCell = Trim$(ExtractJsonField(fActionChunk, "target_cell"))
                    
                    fhMsg = ExtractJsonField(fActionChunk, "message")
                    If Len(fhMsg) = 0 Then fhMsg = ExtractJsonField(fActionChunk, "value")
                    If Len(fhMsg) = 0 Then fhMsg = ExtractJsonField(fActionChunk, "text")
                    
                    ExecuteHauntAction ws, fhType, fhCell, fhMsg, cellCoord
                    flatSearchPos = fObjEnd + 1
                Else
                    flatSearchPos = fHauntPos + Len("TRIGGER_HAUNT")
                End If
            Else
                flatSearchPos = fHauntPos + Len("TRIGGER_HAUNT")
            End If
        Loop
    End If

    ' Fallback for direct haunt payloads without TRIGGER_HAUNT command wrapper
    If InStr(1, jsonResp, "TRIGGER_HAUNT", vbTextCompare) = 0 Then
        Dim directType As String
        directType = LCase$(Trim$(ExtractJsonField(jsonResp, "haunt_type")))
        If Len(directType) = 0 Then directType = LCase$(Trim$(ExtractJsonField(jsonResp, "type")))
        
        If Len(directType) > 0 Then
            Dim directCell As String, directMsg As String
            directCell = Trim$(ExtractJsonField(jsonResp, "cell"))
            If Len(directCell) = 0 Then directCell = Trim$(ExtractJsonField(jsonResp, "target_cell"))
            directMsg = ExtractJsonField(jsonResp, "message")
            If Len(directMsg) = 0 Then directMsg = ExtractJsonField(jsonResp, "value")
            ExecuteHauntAction ws, directType, directCell, directMsg, cellCoord
        Else
            ' Standalone keyword checks (case-insensitive)
            If InStr(1, jsonResp, "flicker_lamp", vbTextCompare) > 0 Then FlashKeroseneLamp
            If InStr(1, jsonResp, "thunder_invert", vbTextCompare) > 0 Then ThunderInvert
            If InStr(1, jsonResp, "screen_tremor", vbTextCompare) > 0 Then ScreenTremor
            If InStr(1, jsonResp, "ink_spread", vbTextCompare) > 0 Then
                If Len(cellCoord) > 0 Then
                    SpreadBloodScab ws.Range(cellCoord)
                Else
                    SpreadBloodScab ws.Range("B18")
                End If
            End If
            If InStr(1, jsonResp, "whisper", vbTextCompare) > 0 Then
                Dim directWhisper As String
                directWhisper = ExtractJsonField(jsonResp, "message")
                Application.DisplayStatusBar = True
                If Len(directWhisper) > 0 Then
                    Application.StatusBar = directWhisper
                Else
                    Application.StatusBar = "...the floorboards remember..."
                End If
            End If
            If InStr(1, jsonResp, "cell_text", vbTextCompare) > 0 Then
                Dim ctCell As String, ctMsg As String
                ctCell = Trim$(ExtractJsonField(jsonResp, "cell"))
                If Len(ctCell) = 0 Then ctCell = Trim$(ExtractJsonField(jsonResp, "target_cell"))
                ctMsg = ExtractJsonField(jsonResp, "message")
                If Len(ctMsg) = 0 Then ctMsg = "THE AUDIT WATCHES"
                If Len(ctCell) > 0 Then
                    ws.Range(ctCell).Value = ctMsg
                    ws.Range(ctCell).Font.Color = COLOR_WARNING_RED
                Else
                    Application.DisplayStatusBar = True
                    Application.StatusBar = ctMsg
                End If
            End If
        End If
    End If
    
    ' Check for Row 13 awaken
    If InStr(1, jsonResp, "AWAKEN_ROW_13", vbTextCompare) > 0 Then
        ws.Range("A13").Font.Color = COLOR_WARNING_RED
        ws.Range("A13").Value = "STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"
        ws.Range("A14:I16").Interior.Color = COLOR_DECAYING_PAPER
        ws.Range("A14:I16").Font.Color = COLOR_CARBON
    End If
    
    ' Check for pixel matrix render
    If InStr(1, jsonResp, "RENDER_PIXEL_MATRIX", vbTextCompare) > 0 Then
        RenderPixelFace ws
    End If
    
    ' Check for Cell Value Updates
    If InStr(1, jsonResp, "BALANCED (UNHOLY)", vbTextCompare) > 0 Then
        ws.Range("I7").Value = "BALANCED (UNHOLY)"
        ws.Range("I7").Font.Color = COLOR_WARNING_RED
    End If
    
    ' Check for Hijack Type
    If InStr(1, jsonResp, "YOUR SALARY CANNOT SAVE YOU", vbTextCompare) > 0 Then
        ws.Range("B18").Value = "YOUR SALARY CANNOT SAVE YOU"
        ws.Range("B18").Font.Color = COLOR_DRIED_BLOOD
        ThudBeep
        PlatformSleep 1200
        ws.Range("B18").Value = Empty
        ws.Range("B18").Font.Color = COLOR_CARBON
    End If
    
    ' Check for Phase 3 Code Accepted / Unlock Button
    Dim isAccepted As Boolean
    isAccepted = (LCase$(ExtractJsonField(jsonResp, "accepted")) = "true")
    If InStr(1, jsonResp, "UNLOCK_BUTTON", vbTextCompare) > 0 Or (isAccepted And gLocalPhase = 4) Then
        ws.Range("C18:D18").Interior.Color = COLOR_WARNING_RED
        ws.Range("C18:D18").Font.Color = RGB(255, 255, 255)
        ws.Range("C18").Value = "[ SEAL ARCHIVE ]"
        MsgBox "Override Accepted. The Seal of Armitage is armed. Click [ SEAL ARCHIVE ] to execute Phase 4 Banishment.", vbExclamation, "Vault Protocol"
    End If
    
    ' Check for Phase 4 Banishment
    Dim isBanished As Boolean
    isBanished = (LCase$(ExtractJsonField(jsonResp, "banished")) = "true")
    If InStr(1, jsonResp, "LOCK_SHEET", vbTextCompare) > 0 Or isBanished Then
        StopEyeBlink
        ThunderInvert
        ScreenTremor
        
        ' Apply Final Cold Ash Stamp
        ws.Range("B10:H12").Interior.Color = COLOR_COLD_ASH
        ws.Range("B10:H12").Font.Color = COLOR_WARNING_RED
        ws.Range("B10").Value = "[ ARCHIVE SEALED - OCTOBER 14, 1928 - 00:01 AM ]"
        ws.Range("B11").Value = "ALL BALANCES CANCELLED BY ORDER OF ARMITAGE"
        ws.Range("B12").Value = "REST NOW, AUDITOR. THE VOID BOOKS ARE CLOSED."
        
        MsgBox "ARCHIVE SEALED. The entity has been banished into the floorboards.", vbInformation, "Audit Terminated"
    End If
    
    On Error GoTo 0
End Sub

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
            
            Dim targetAddress As String
            targetAddress = hCell
            If Len(targetAddress) = 0 Then targetAddress = cellCoord
            
            If Len(targetAddress) > 0 Then
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
            inkTarget = hCell
            If Len(inkTarget) = 0 Then inkTarget = cellCoord
            If Len(inkTarget) = 0 Then inkTarget = "B18"
            SpreadBloodScab ws.Range(inkTarget)
            
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
    Dim inStr As Boolean, inEsc As Boolean
    depth = 0
    inStr = False
    inEsc = False
    
    For i = startBracePos To Len(s)
        Dim c As String
        c = Mid$(s, i, 1)
        If inStr Then
            If inEsc Then
                inEsc = False
            ElseIf c = "\" Then
                inEsc = True
            ElseIf c = """" Then
                inStr = False
            End If
        Else
            If c = """" Then
                inStr = True
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
''' Robust zero-dependency JSON field extractor.
''' Scans keys outside string literals, verifies following colon, and parses string/null/unquoted values.
''' </summary>
Public Function ExtractJsonField(ByVal json As String, ByVal key As String) As String
    On Error Resume Next
    Dim i As Long
    Dim inStr As Boolean, inEsc As Boolean
    Dim targetKey As String
    targetKey = LCase$(Trim$(key))
    
    i = 1
    inStr = False
    inEsc = False
    
    Do While i <= Len(json)
        Dim c As String
        c = Mid$(json, i, 1)
        
        If inStr Then
            If inEsc Then
                inEsc = False
            ElseIf c = "\" Then
                inEsc = True
            ElseIf c = """" Then
                inStr = False
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
''' Zero-dependency Offline Rule Fallback: 100% playable even without Python running.
''' </summary>
Public Sub HandleOfflineEvent(ByVal eventType As String, ByVal cellCoord As String, ByVal cellVal As String, ByVal buttonName As String)
    On Error Resume Next
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")
    If ws Is Nothing Then Set ws = ActiveSheet
    If ws Is Nothing Then Exit Sub
    
    If gLocalPhase = 0 Then gLocalPhase = 1
    
    ' Phase 1: Overdue Fee Calculation
    If gLocalPhase = 1 And UCase(cellCoord) = "H7" Then
        Dim cleanVal As Double
        Dim sVal As String
        sVal = Replace(Replace(cellVal, "$", ""), ",", "")
        cleanVal = Val(sVal)
        
        If Abs(cleanVal - 7#) < 0.01 Then
            ws.Range("I7").Value = "BALANCED (UNHOLY)"
            ws.Range("I7").Font.Color = COLOR_WARNING_RED
            ws.Range("A13").Font.Color = COLOR_WARNING_RED
            ws.Range("A13").Value = "STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"
            
            ' Reveal censored rows 14-16
            ws.Range("A14:I16").Interior.Color = COLOR_DECAYING_PAPER
            ws.Range("A14:I16").Font.Color = COLOR_CARBON
            ws.Range("B14").Value = "COORDINATE DISCLOSED: RADAR GRID K20:AN49"
            
            ThudBeep
            ScreenTremor
            gLocalPhase = 2
        Else
            SpreadBloodScab ws.Range("H7")
            ThudBeep
        End If
        Exit Sub
    End If
    
    ' Phase 2: Spray Reagent Button Click
    If gLocalPhase = 2 And (eventType = "reagent_spray" Or buttonName = "SPRAY_REAGENT") Then
        RenderPixelFace ws
        ThudBeep
        gLocalPhase = 3
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
            Exit Sub
        Else
            Dim cleanCode As String
            cleanCode = Trim(UCase(cellVal))
            If cleanCode = "SEAL THE DEEP VAULT" Then
                gLocalPhase = 4
                ws.Range("C18:D18").Interior.Color = COLOR_WARNING_RED
                ws.Range("C18:D18").Font.Color = RGB(255, 255, 255)
                ws.Range("C18").Value = "[ SEAL ARCHIVE ]"
                MsgBox "Override Accepted. The Seal of Armitage is armed. Click [ SEAL ARCHIVE ] to execute Phase 4 Banishment.", vbExclamation, "Vault Protocol"
                Exit Sub
            Else
                SpreadBloodScab ws.Range("B18")
                ThudBeep
            End If
        End If
    End If
    
    ' Phase 4: Banishment Execution
    If (gLocalPhase = 4 Or eventType = "banish") Then
        StopEyeBlink
        ThunderInvert
        ScreenTremor
        
        ' Apply Final Cold Ash Stamp
        ws.Range("B10:H12").Interior.Color = COLOR_COLD_ASH
        ws.Range("B10:H12").Font.Color = COLOR_WARNING_RED
        ws.Range("B10").Value = "[ ARCHIVE SEALED - OCTOBER 14, 1928 - 00:01 AM ]"
        ws.Range("B11").Value = "ALL BALANCES CANCELLED BY ORDER OF ARMITAGE"
        ws.Range("B12").Value = "REST NOW, AUDITOR. THE VOID BOOKS ARE CLOSED."
        
        MsgBox "ARCHIVE SEALED. The entity has been banished into the floorboards.", vbInformation, "Audit Terminated"
    End If
    
    On Error GoTo 0
End Sub

Public Sub TriggerReagentMacro()
    PostEvent "reagent_spray", buttonName:="SPRAY_REAGENT"
End Sub

Public Sub TriggerBanishMacro()
    PostEvent "banish", cellVal:="SEAL THE DEEP VAULT"
End Sub
