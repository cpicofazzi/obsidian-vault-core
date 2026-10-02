<#
.SYNOPSIS
    Pico Vault CLI Shortcuts for PowerShell
.DESCRIPTION
    Loads quick aliases and functions to interact with pico-vault from any PowerShell terminal.
    
    Commands:
        inspo <url/text>    - Instantly capture inspiration media or repo
        task <text>         - Instantly log a task (supports due:YYYY-MM-DD, !high)
        idea <text>         - Instantly capture an idea
        research <topic>    - Instantly scaffold deep research
        watch-vault         - Start the autonomous background watcher daemon
        brief-vault         - Generate today's morning briefing
.EXAMPLE
    . .\scripts\vault_cli.ps1
    inspo "https://github.com/microsoft/autogen Multi-agent conversation framework"
    task "Submit amended tax documents due:2026-09-25 !high"
#>

$VaultRoot = Split-Path -Parent $PSScriptRoot

function inspo {
    param([Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)][string[]]$Text)
    $inputStr = "Inspo: " + ($Text -join " ")
    python "$VaultRoot\scripts\vault_ingest.py" --input "$inputStr"
}

function task {
    param([Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)][string[]]$Text)
    $inputStr = "Task: " + ($Text -join " ")
    python "$VaultRoot\scripts\vault_ingest.py" --input "$inputStr"
}

function idea {
    param([Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)][string[]]$Text)
    $inputStr = "Idea: " + ($Text -join " ")
    python "$VaultRoot\scripts\vault_ingest.py" --input "$inputStr"
}

function research {
    param([Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)][string[]]$Text)
    $inputStr = "Research: " + ($Text -join " ")
    python "$VaultRoot\scripts\vault_ingest.py" --input "$inputStr"
}

function watch-vault {
    Write-Host "🤖 Starting Autonomous Vault Watcher Daemon..." -ForegroundColor Cyan
    python "$VaultRoot\scripts\vault_watcher.py"
}

function brief-vault {
    Write-Host "🌅 Generating Daily Briefing..." -ForegroundColor Yellow
    python "$VaultRoot\scripts\daily_brief.py"
}

function serve-intake {
    param([int]$Port = 8765, [string]$Token)
    Write-Host "📱 Starting Mobile Intake Webhook Server on port $Port..." -ForegroundColor Cyan
    if ($Token) {
        python "$VaultRoot\scripts\mobile_intake.py" --port $Port --token $Token
    } else {
        python "$VaultRoot\scripts\mobile_intake.py" --port $Port
    }
}

function daemon-status {
    powershell -ExecutionPolicy Bypass -File "$VaultRoot\scripts\setup_daemon.ps1" status
}

function daemon-start {
    powershell -ExecutionPolicy Bypass -File "$VaultRoot\scripts\setup_daemon.ps1" start
}

function daemon-stop {
    powershell -ExecutionPolicy Bypass -File "$VaultRoot\scripts\setup_daemon.ps1" stop
}

Write-Host "✨ Pico Vault CLI loaded!" -ForegroundColor Green
Write-Host "   Capture:  inspo, task, idea, research" -ForegroundColor Gray
Write-Host "   Daemons:  daemon-status, daemon-start, daemon-stop, serve-intake, watch-vault, brief-vault" -ForegroundColor Gray
