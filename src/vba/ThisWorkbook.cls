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
    On Error GoTo 0
End Sub

Private Sub Workbook_BeforeClose(Cancel As Boolean)
    On Error Resume Next
    StopEyeBlink
    EmergencyReset
    On Error GoTo 0
End Sub
