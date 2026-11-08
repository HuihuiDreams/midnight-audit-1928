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
            ProcessDaemonResponse respText
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
            ProcessDaemonResponse http.responseText
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
Private Sub ProcessDaemonResponse(ByVal jsonResp As String)
    On Error Resume Next
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")
    
    ' Check for FX triggers
    If InStr(jsonResp, "THUD_BEEP") > 0 Then
        ThudBeep
    End If
    If InStr(jsonResp, "SCREEN_TREMOR") > 0 Then
        ScreenTremor
    End If
    If InStr(jsonResp, "THUNDER_STROBE") > 0 Then
        ThunderInvert
    End If
    
    ' Check for Row 13 awaken
    If InStr(jsonResp, "AWAKEN_ROW_13") > 0 Then
        ws.Range("A13").Font.Color = COLOR_WARNING_RED
        ws.Range("A13").Value = "STOP AUDITING ROW 13 - HE SLEEPS BENEATH THE FLOORBOARDS"
        ws.Range("A14:I16").Interior.Color = COLOR_DECAYING_PAPER
        ws.Range("A14:I16").Font.Color = COLOR_CARBON
    End If
    
    ' Check for pixel matrix render
    If InStr(jsonResp, "RENDER_PIXEL_MATRIX") > 0 Then
        RenderPixelFace ws
    End If
    
    ' Check for Cell Value Updates
    If InStr(jsonResp, "BALANCED (UNHOLY)") > 0 Then
        ws.Range("I7").Value = "BALANCED (UNHOLY)"
        ws.Range("I7").Font.Color = COLOR_WARNING_RED
    End If
    
    ' Check for Hijack Type
    If InStr(jsonResp, "YOUR SALARY CANNOT SAVE YOU") > 0 Then
        ws.Range("B18").Value = "YOUR SALARY CANNOT SAVE YOU"
        ws.Range("B18").Font.Color = COLOR_DRIED_BLOOD
        ThudBeep
        PlatformSleep 1200
        ws.Range("B18").Value = Empty
        ws.Range("B18").Font.Color = COLOR_CARBON
    End If
    
    On Error GoTo 0
End Sub

''' <summary>
''' Zero-dependency Offline Rule Fallback: 100% playable even without Python running.
''' </summary>
Public Sub HandleOfflineEvent(ByVal eventType As String, ByVal cellCoord As String, ByVal cellVal As String, ByVal buttonName As String)
    On Error Resume Next
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Audit_Ledger_1928")
    
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
                MsgBox "Override Accepted. The Seal of Armitage is armed. Proceed to Phase 4 Banishment.", vbExclamation, "Vault Protocol"
                Exit Sub
            Else
                SpreadBloodScab ws.Range("B18")
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
    PostEvent "banish"
End Sub
