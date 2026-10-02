<#
.SYNOPSIS
    Autonomous Background Scheduling & Daemon Manager for pico-vault.
.DESCRIPTION
    Manages background automation for pico-vault:
    1. PicoVault-Watcher: Continuous silent background watcher monitoring 00_Inbox for changes.
    2. PicoVault-DailyBriefing: Daily scheduled briefing generator triggered every morning at 6:00 AM.
    3. Process lifecycle controls: start, stop, restart, status, and manual briefing triggers.

.PARAMETER Action
    Action to perform: status (default), start, stop, restart, install, uninstall, brief.

.EXAMPLE
    .\scripts\setup_daemon.ps1 status
    .\scripts\setup_daemon.ps1 start
    .\scripts\setup_daemon.ps1 stop
    .\scripts\setup_daemon.ps1 install
    .\scripts\setup_daemon.ps1 uninstall
    .\scripts\setup_daemon.ps1 brief
#>

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet("status", "start", "stop", "restart", "install", "uninstall", "brief", "help")]
    [string]$Action = "status",

    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Restart,
    [switch]$Status,
    [switch]$Brief,
    [switch]$Force
)

# Handle flag switches overriding positional $Action
if ($Install)       { $Action = "install" }
elseif ($Uninstall) { $Action = "uninstall" }
elseif ($Start)     { $Action = "start" }
elseif ($Stop)      { $Action = "stop" }
elseif ($Restart)   { $Action = "restart" }
elseif ($Status)    { $Action = "status" }
elseif ($Brief)     { $Action = "brief" }

# Paths
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$VaultRoot   = Split-Path -Parent $ScriptDir
$WatcherVbs  = Join-Path $ScriptDir "run_silent_watcher.vbs"
$BriefVbs    = Join-Path $ScriptDir "run_silent_brief.vbs"
$StartupDir  = [Environment]::GetFolderPath('Startup')
$StartupLink = Join-Path $StartupDir "Pico Vault Watcher.lnk"
$InboxFile   = Join-Path $VaultRoot "00_Inbox\Quick Capture.md"
$BriefFile   = Join-Path $VaultRoot "01_Dashboard\Daily Briefing.md"

$TaskNameWatcher = "PicoVault-Watcher"
$TaskNameBrief   = "PicoVault-DailyBriefing"

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-WatcherProcesses {
    return Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -ne 'powershell.exe' -and
        $_.Name -ne 'pwsh.exe' -and
        $_.CommandLine -like "*vault_watcher.py*"
    }
}

function Start-WatcherDaemon {
    Write-Host "[*] Starting Pico Vault Watcher daemon..." -ForegroundColor Cyan
    $procs = Get-WatcherProcesses
    if ($procs) {
        $pids = ($procs | ForEach-Object { $_.ProcessId }) -join ", "
        Write-Host "    [!] Watcher daemon is already running (PID: $pids)." -ForegroundColor Yellow
        return
    }

    if (-not (Test-Path $WatcherVbs)) {
        Write-Host "    [-] Missing launcher script: $WatcherVbs" -ForegroundColor Red
        return
    }

    Start-Process "wscript.exe" -ArgumentList "`"$WatcherVbs`"" -WorkingDirectory $VaultRoot
    Start-Sleep -Milliseconds 1200

    $started = Get-WatcherProcesses
    if ($started) {
        $pids = ($started | ForEach-Object { $_.ProcessId }) -join ", "
        Write-Host "    [+] Vault Watcher started silently in background (PID: $pids)." -ForegroundColor Green
    } else {
        Write-Host "    [-] Failed to detect running watcher process." -ForegroundColor Red
    }
}

function Stop-WatcherDaemon {
    Write-Host "[*] Stopping Pico Vault Watcher daemon..." -ForegroundColor Cyan
    $procs = Get-WatcherProcesses
    if (-not $procs) {
        Write-Host "    [i] No running Vault Watcher daemon found." -ForegroundColor DarkGray
        return
    }

    foreach ($p in $procs) {
        try {
            Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
            Write-Host "    Terminated process PID $($p.ProcessId) ($($p.Name))" -ForegroundColor Gray
        } catch {
            Write-Host "    Failed to terminate PID $($p.ProcessId): $($_.Exception.Message)" -ForegroundColor DarkYellow
        }
    }

    Start-Sleep -Milliseconds 500
    $remaining = Get-WatcherProcesses
    if (-not $remaining) {
        Write-Host "    [+] Watcher daemon stopped cleanly." -ForegroundColor Green
    } else {
        Write-Host "    [!] Some processes could not be stopped." -ForegroundColor Red
    }
}

function Create-StartupShortcut {
    try {
        $wsh = New-Object -ComObject WScript.Shell
        $sc = $wsh.CreateShortcut($StartupLink)
        $sc.TargetPath = "wscript.exe"
        $sc.Arguments = "`"$WatcherVbs`""
        $sc.WorkingDirectory = $VaultRoot
        $sc.Description = "Pico Vault Autonomous Watcher Daemon"
        $sc.Save()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($wsh) | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Remove-StartupShortcut {
    if (Test-Path $StartupLink) {
        Remove-Item -Path $StartupLink -Force -ErrorAction SilentlyContinue
    }
}

function Install-Tasks {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Installing Pico Vault Background Tasks & Automation" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan

    $isAdmin = Test-IsAdmin

    # Always ensure user startup shortcut is installed for logon resilience
    $scCreated = Create-StartupShortcut
    if ($scCreated) {
        Write-Host "    [+] Startup folder shortcut configured: $StartupLink" -ForegroundColor Green
    }

    if (-not $isAdmin) {
        Write-Host "`n[!] Administrator privileges required for Windows Task Scheduler registration." -ForegroundColor Yellow
        Write-Host "    Current session is running under standard user credentials." -ForegroundColor Gray
        Write-Host "    Startup logon shortcut is active, but to schedule the 6:00 AM Daily Briefing in Task Scheduler:" -ForegroundColor Gray
        Write-Host "    Run PowerShell as Administrator, then execute:" -ForegroundColor Cyan
        Write-Host "    powershell -ExecutionPolicy Bypass -File `"$PSCommandPath`" install`n" -ForegroundColor White
        
        # If interactive, prompt to elevate
        if ([Environment]::UserInteractive -and -not $Force) {
            Write-Host "    Attempting elevation prompt..." -ForegroundColor Yellow
            try {
                Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" install -Force"
                Write-Host "    Elevated installation process launched." -ForegroundColor Green
                return
            } catch {
                Write-Host "    Elevation request cancelled or unavailable." -ForegroundColor DarkGray
            }
        }
        return
    }

    # 1. PicoVault-Watcher (At Logon)
    try {
        $actionW = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$WatcherVbs`"" -WorkingDirectory $VaultRoot
        $triggerW = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
        $settingsW = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -Priority 5 -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
        $principalW = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

        Register-ScheduledTask -TaskName $TaskNameWatcher -Action $actionW -Trigger $triggerW -Settings $settingsW -Principal $principalW -Description "Pico Vault Autonomous Background Watcher Daemon - Monitors 00_Inbox and triages notes silently." -Force | Out-Null
        Write-Host "    [+] Registered Task Scheduler Task: $TaskNameWatcher (Trigger: User Logon)" -ForegroundColor Green
    } catch {
        Write-Host "    [-] Failed to register $($TaskNameWatcher): $($_.Exception.Message)" -ForegroundColor Red
    }

    # 2. PicoVault-DailyBriefing (Daily at 6:00 AM)
    try {
        $actionB = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$BriefVbs`"" -WorkingDirectory $VaultRoot
        $triggerB = New-ScheduledTaskTrigger -Daily -At "6:00AM"
        $settingsB = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun -StartWhenAvailable -Priority 5
        $principalB = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

        Register-ScheduledTask -TaskName $TaskNameBrief -Action $actionB -Trigger $triggerB -Settings $settingsB -Principal $principalB -Description "Pico Vault Daily AI Briefing & Serendipity Engine - Generates morning dashboard at 6:00 AM." -Force | Out-Null
        Write-Host "    [+] Registered Task Scheduler Task: $TaskNameBrief (Trigger: Daily at 6:00 AM)" -ForegroundColor Green
    } catch {
        Write-Host "    [-] Failed to register $($TaskNameBrief): $($_.Exception.Message)" -ForegroundColor Red
    }

    Write-Host "`nInstallation complete! You can verify status anytime with:" -ForegroundColor Cyan
    Write-Host "    .\scripts\setup_daemon.ps1 status" -ForegroundColor White
}

function Uninstall-Tasks {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Uninstalling Pico Vault Background Tasks & Automation" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan

    Stop-WatcherDaemon
    Remove-StartupShortcut
    Write-Host "    [+] Removed startup shortcut if present." -ForegroundColor Green

    $isAdmin = Test-IsAdmin
    if (-not $isAdmin) {
        Write-Host "`n[!] Administrator privileges required to unregister tasks from Task Scheduler." -ForegroundColor Yellow
        Write-Host "    To unregister scheduled tasks completely, run PowerShell as Administrator:" -ForegroundColor Gray
        Write-Host "    powershell -ExecutionPolicy Bypass -File `"$PSCommandPath`" uninstall`n" -ForegroundColor White
        return
    }

    foreach ($task in @($TaskNameWatcher, $TaskNameBrief)) {
        try {
            $existing = Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
            if ($existing) {
                Unregister-ScheduledTask -TaskName $task -Confirm:$false -ErrorAction Stop
                Write-Host "    [+] Unregistered Task: $task" -ForegroundColor Green
            } else {
                Write-Host "    [i] Task not found: $task" -ForegroundColor DarkGray
            }
        } catch {
            Write-Host "    [-] Error unregistering ${task}: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Write-Host "`nUninstallation complete." -ForegroundColor Cyan
}

function Show-Status {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Pico Vault Autonomous Automation Status" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan

    # 1. Daemon Process Status
    $procs = Get-WatcherProcesses
    if ($procs) {
        $pids = ($procs | ForEach-Object { $_.ProcessId }) -join ", "
        Write-Host "[RUNNING] Watcher Daemon Process: ACTIVE (PID: $pids)" -ForegroundColor Green
    } else {
        Write-Host "[STOPPED] Watcher Daemon Process: INACTIVE" -ForegroundColor DarkGray
    }

    # 2. Startup Shortcut Status
    if (Test-Path $StartupLink) {
        Write-Host "[ENABLED] Windows Logon Shortcut: PRESENT ($StartupLink)" -ForegroundColor Green
    } else {
        Write-Host "[DISABLED] Windows Logon Shortcut: NOT CONFIGURED" -ForegroundColor DarkGray
    }

    # 3. Task Scheduler Tasks
    Write-Host "`nTask Scheduler Jobs:" -ForegroundColor Cyan
    foreach ($taskName in @($TaskNameWatcher, $TaskNameBrief)) {
        try {
            $t = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
            if ($t) {
                $info = Get-ScheduledTaskInfo -TaskName $taskName -ErrorAction SilentlyContinue
                $nextRun = if ($info.NextRunTime) { $info.NextRunTime.ToString("yyyy-MM-dd HH:mm:ss") } else { "N/A" }
                $lastRun = if ($info.LastRunTime -and $info.LastRunTime.Year -gt 1999) { $info.LastRunTime.ToString("yyyy-MM-dd HH:mm:ss") } else { "Never" }
                Write-Host "    [$taskName]" -ForegroundColor Yellow
                Write-Host "        State:        $($t.State)" -ForegroundColor Gray
                Write-Host "        Next Run:     $nextRun" -ForegroundColor Gray
                Write-Host "        Last Run:     $lastRun (Result: $($info.LastTaskResult))" -ForegroundColor Gray
            } else {
                Write-Host "    [$taskName] Not registered in Task Scheduler" -ForegroundColor DarkGray
            }
        } catch {
            Write-Host "    [$taskName] Status check error: $($_.Exception.Message)" -ForegroundColor DarkYellow
        }
    }

    # 4. Vault Health & Files
    Write-Host "`nVault Health & Queues:" -ForegroundColor Cyan
    if (Test-Path $InboxFile) {
        $lines = Get-Content $InboxFile -ErrorAction SilentlyContinue
        $dropzoneIdx = -1
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match "<!-- New raw inputs land below this line -->") {
                $dropzoneIdx = $i
                break
            }
        }
        $pendingCount = 0
        if ($dropzoneIdx -ge 0) {
            $inFooter = $false
            for ($i = $dropzoneIdx + 1; $i -lt $lines.Count; $i++) {
                $l = $lines[$i].Trim()
                if ($l -like "---*" -or $l -like "*Ingestion Instructions*") { $inFooter = $true }
                if (-not $inFooter -and $l -and -not $l.StartsWith("###")) { $pendingCount++ }
            }
        }
        if ($pendingCount -gt 0) {
            Write-Host "    Quick Capture Dropzone: $pendingCount pending item(s) awaiting ingest" -ForegroundColor Yellow
        } else {
            Write-Host "    Quick Capture Dropzone: Clean (0 pending items)" -ForegroundColor Green
        }
    } else {
        Write-Host "    Quick Capture: File missing ($InboxFile)" -ForegroundColor Red
    }

    if (Test-Path $BriefFile) {
        $briefMtime = (Get-Item $BriefFile).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
        Write-Host "    Daily Briefing File:    Last updated $briefMtime" -ForegroundColor Green
    } else {
        Write-Host "    Daily Briefing File:    Not yet generated" -ForegroundColor DarkGray
    }

    Write-Host "`nCommands:" -ForegroundColor DarkCyan
    Write-Host "    .\scripts\setup_daemon.ps1 start      - Start watcher daemon now" -ForegroundColor Gray
    Write-Host "    .\scripts\setup_daemon.ps1 stop       - Stop watcher daemon" -ForegroundColor Gray
    Write-Host "    .\scripts\setup_daemon.ps1 restart    - Restart watcher daemon" -ForegroundColor Gray
    Write-Host "    .\scripts\setup_daemon.ps1 install    - Configure Task Scheduler & Logon auto-start" -ForegroundColor Gray
    Write-Host "    .\scripts\setup_daemon.ps1 uninstall  - Remove scheduled tasks & auto-start" -ForegroundColor Gray
    Write-Host "    .\scripts\setup_daemon.ps1 brief      - Generate morning briefing right now" -ForegroundColor Gray
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Run-DailyBrief {
    Write-Host "[*] Compiling Daily Briefing & Serendipity Engine..." -ForegroundColor Yellow
    python "$VaultRoot\scripts\daily_brief.py"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[+] Morning briefing updated: 01_Dashboard/Daily Briefing.md" -ForegroundColor Green
    } else {
        Write-Host "[-] Daily brief generation encountered an issue." -ForegroundColor Red
    }
}

# Dispatch Action
switch ($Action.ToLower()) {
    "start" {
        Start-WatcherDaemon
    }
    "stop" {
        Stop-WatcherDaemon
    }
    "restart" {
        Stop-WatcherDaemon
        Start-Sleep -Milliseconds 800
        Start-WatcherDaemon
    }
    "install" {
        Install-Tasks
    }
    "uninstall" {
        Uninstall-Tasks
    }
    "brief" {
        Run-DailyBrief
    }
    "status" {
        Show-Status
    }
    default {
        Show-Status
    }
}
