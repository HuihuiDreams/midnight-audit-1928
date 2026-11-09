Attribute VB_Name = "M_Bootstrap"
Option Explicit

' ==============================================================================
' The Midnight Audit (1928) - M_Bootstrap.bas
' Cross-Platform Win32/macOS API Declarations, UI Stripping & Emergency Reset
' ==============================================================================

#If Mac Then
    ' macOS fallback: Win32 API functions are unavailable
#ElseIf VBA7 Then
    ' 64-bit Office on Windows
    Public Declare PtrSafe Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)
    Public Declare PtrSafe Function BeepAPI Lib "kernel32" Alias "Beep" (ByVal dwFreq As Long, ByVal dwDuration As Long) As Long
    Public Declare PtrSafe Function GetForegroundWindow Lib "user32" () As LongPtr
    Public Declare PtrSafe Function MoveWindow Lib "user32" (ByVal hWnd As LongPtr, ByVal x As Long, ByVal y As Long, ByVal nWidth As Long, ByVal nHeight As Long, ByVal bRepaint As Long) As Long
    Public Declare PtrSafe Function GetWindowRect Lib "user32" (ByVal hWnd As LongPtr, lpRect As RECT) As Long
#Else
    ' 32-bit Office on Windows
    Public Declare Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)
    Public Declare Function BeepAPI Lib "kernel32" Alias "Beep" (ByVal dwFreq As Long, ByVal dwDuration As Long) As Long
    Public Declare Function GetForegroundWindow Lib "user32" () As Long
    Public Declare Function MoveWindow Lib "user32" (ByVal hWnd As Long, ByVal x As Long, ByVal y As Long, ByVal nWidth As Long, ByVal nHeight As Long, ByVal bRepaint As Long) As Long
    Public Declare Function GetWindowRect Lib "user32" (ByVal hWnd As Long, lpRect As RECT) As Long
#End If

Public Type RECT
    Left As Long
    Top As Long
    Right As Long
    Bottom As Long
End Type

' Global Palette Constants (RGB)
Public Const COLOR_BONE_PAPER As Long = 12177107    ' RGB(211, 206, 185)
Public Const COLOR_DECAYING_PAPER As Long = 11059141 ' RGB(197, 191, 168)
Public Const COLOR_CARBON As Long = 1316376         ' RGB(24, 22, 20)
Public Const COLOR_HOSPITAL_GREEN As Long = 4738885 ' RGB(69, 79, 72)
Public Const COLOR_DRIED_BLOOD As Long = 855854     ' RGB(46, 15, 13)
Public Const COLOR_WARNING_RED As Long = 1318026     ' RGB(138, 28, 20)
Public Const COLOR_PHOSPHOR_GREEN As Long = 4084539 ' RGB(59, 83, 62)
Public Const COLOR_COLD_ASH As Long = 9407882       ' RGB(138, 141, 143)
Public Const COLOR_ABYSS As Long = 0                ' RGB(0, 0, 0)

''' <summary>
''' Strips default productivity UI to immerse player in the 1928 manuscript aesthetic.
''' Binds Ctrl+Shift+R to EmergencyReset to guarantee safety.
''' </summary>
Public Sub InitializeArchiveUI()
    On Error Resume Next
    
    ' Register Emergency Rescue Shortcuts
    Application.OnKey "^+R", "EmergencyReset"
    Application.OnKey "^+r", "EmergencyReset"
    
    ' Strip Modern Chrome
    Application.Caption = "The Midnight Audit (1928) - Miskatonic University Annex"
    Application.DisplayFormulaBar = False
    Application.DisplayStatusBar = True
    Application.StatusBar = "OCTOBER 31, 1928 - 11:47 PM | ALL HALLOWS' EVE | ANNEX ARCHIVE DELINQUENCY LEDGER"
    
    If Not ActiveWindow Is Nothing Then
        ActiveWindow.DisplayHeadings = False
        ActiveWindow.DisplayGridlines = False
        ActiveWindow.DisplayWorkbookTabs = False
        ActiveWindow.DisplayHorizontalScrollBar = False
        ActiveWindow.DisplayVerticalScrollBar = False
    End If
    
    On Error GoTo 0
End Sub

''' <summary>
''' Emergency Escape Hatch: Restores standard Excel toolbars, headings, and formula bar.
''' </summary>
Public Sub EmergencyReset(Optional ByVal silent As Boolean = False)
    On Error Resume Next
    
    Application.DisplayFormulaBar = True
    Application.DisplayStatusBar = True
    Application.StatusBar = False
    Application.Caption = Empty
    
    If Not ActiveWindow Is Nothing Then
        ActiveWindow.DisplayHeadings = True
        ActiveWindow.DisplayGridlines = True
        ActiveWindow.DisplayWorkbookTabs = True
        ActiveWindow.DisplayHorizontalScrollBar = True
        ActiveWindow.DisplayVerticalScrollBar = True
    End If
    
    ' Clear shortcut bindings
    Application.OnKey "^+R"
    Application.OnKey "^+r"
    
    ' Cancel timers
    StopEyeBlink
    CancelAmbientWhisper
    
    If Not silent Then
        MsgBox "Standard Excel interface restored.", vbInformation, "The Midnight Audit - Emergency Reset"
    End If
    On Error GoTo 0
End Sub

''' <summary>
''' Cross-platform Sleep wrapper
''' </summary>
Public Sub PlatformSleep(ByVal dwMilliseconds As Long)
    #If Mac Then
        Dim durationSec As Double
        durationSec = dwMilliseconds / 1000#
        Dim startT As Double
        startT = Timer
        
        Do
            Dim currentT As Double
            currentT = Timer
            Dim elapsed As Double
            If currentT >= startT Then
                elapsed = currentT - startT
            Else
                ' Midnight crossover (Timer resets to 0 at midnight 00:00:00)
                elapsed = (86400# - startT) + currentT
            End If
            
            If elapsed >= durationSec Then Exit Do
            DoEvents
        Loop
    #Else
        Sleep dwMilliseconds
    #End If
End Sub
