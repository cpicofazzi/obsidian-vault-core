' ==============================================================================
' Pico Vault - Silent Daily Briefing Runner
' ==============================================================================
' Executes scripts/daily_brief.py silently with zero console window.
' Intended for Windows Task Scheduler daily triggers at 6:00 AM.
' ==============================================================================

Option Explicit

Dim objShell, objFSO, strScriptDir, strBrief, strCommand, strComSpec

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
strBrief = objFSO.BuildPath(strScriptDir, "daily_brief.py")

If Not objFSO.FileExists(strBrief) Then
    WScript.Quit 1
End If

strComSpec = objShell.ExpandEnvironmentStrings("%COMSPEC%")
strCommand = """" & strComSpec & """ /c python """ & strBrief & """"

' Run silently and wait for completion (0 = hidden window, True = wait)
Dim intExit
intExit = objShell.Run(strCommand, 0, True)

Set objShell = Nothing
Set objFSO = Nothing

WScript.Quit intExit
