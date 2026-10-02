' ==============================================================================
' Pico Vault - Silent Background Watcher Launcher
' ==============================================================================
' Spawns scripts/vault_watcher.py completely invisibly with zero console window.
' Intended for Windows Startup, Task Scheduler, or manual background launch.
' ==============================================================================

Option Explicit

Dim objShell, objFSO, strScriptDir, strWatcher, strCommand

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Resolve paths relative to this script
strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
strWatcher = objFSO.BuildPath(strScriptDir, "vault_watcher.py")

If Not objFSO.FileExists(strWatcher) Then
    MsgBox "Error: Could not locate vault_watcher.py at: " & vbCrLf & strWatcher, vbCritical, "Pico Vault Watcher"
    WScript.Quit 1
End If

' Check if an instance of vault_watcher.py is already running to avoid duplicates
Dim objWMIService, colProcesses
On Error Resume Next
Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")
If Err.Number = 0 Then
    Set colProcesses = objWMIService.ExecQuery("Select ProcessId from Win32_Process Where (Name Like 'python%' Or Name = 'cmd.exe') And CommandLine Like '%vault_watcher.py%'")
    If Err.Number = 0 Then
        If colProcesses.Count > 0 Then
            ' Process already running, nothing to do
            WScript.Quit 0
        End If
    End If
End If
On Error GoTo 0

' Forward any command line arguments passed to this VBS launcher
Dim strArgs, i
strArgs = ""
For i = 0 To WScript.Arguments.Count - 1
    strArgs = strArgs & " " & WScript.Arguments(i)
Next

' Use %COMSPEC% /c python to resolve WindowsApps execution aliases cleanly
' Window style 0 ensures that neither cmd nor python displays a console window.
Dim strComSpec
strComSpec = objShell.ExpandEnvironmentStrings("%COMSPEC%")
strCommand = """" & strComSpec & """ /c python """ & strWatcher & """" & strArgs

' Run silently: 0 = hidden window, False = don't wait for completion
objShell.Run strCommand, 0, False

Set objShell = Nothing
Set objFSO = Nothing
