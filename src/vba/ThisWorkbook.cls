VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "ThisWorkbook"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit

' ==============================================================================
' The Midnight Audit (1928) - ThisWorkbook.cls
' Lifecycle Hooks: UI Stripping on Open & Clean State Restoration on Close
' ==============================================================================

Private Sub Workbook_Open()
    On Error Resume Next
    InitializeArchiveUI
    ' Drain what piled up while the workbook was closed (a LOCK_SHEET queued by the Agent's ritual) before
    ' the state sync marks the archive sealed, which would stop every later poll and leave the sheet unsealed
    PollPendingHaunts
    SyncDaemonState
    StartHauntPolling
    On Error GoTo 0
End Sub

Private Sub Workbook_BeforeClose(Cancel As Boolean)
    On Error Resume Next
    StopEyeBlink
    StopHauntPolling
    CancelAmbientWhisper
    EmergencyReset True
    On Error GoTo 0
End Sub
