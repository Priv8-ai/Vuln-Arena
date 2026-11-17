[CmdletBinding()]
param(
    [string]$Machines = 'all',
    [switch]$KeepHosts
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSCommandPath
Set-Location -LiteralPath $Root

function Test-Administrator {
    $Identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $Principal = [Security.Principal.WindowsPrincipal]::new($Identity)
    return $Principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not $KeepHosts -and -not (Test-Administrator)) {
    Write-Host 'Requesting administrator access to remove only the managed arena.test hosts block...' -ForegroundColor Yellow
    $Forward = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"", '-Machines', "`"$Machines`"")
    Start-Process powershell.exe -Verb RunAs -ArgumentList ($Forward -join ' ')
    exit 0
}

$RunId = $null
$CurrentRun = Join-Path $Root 'runs\current-run.txt'
if (Test-Path -LiteralPath $CurrentRun) { $RunId = [IO.File]::ReadAllText($CurrentRun).Trim() }
$StopArgs = @('arena.py', 'stop', '--machines', $Machines)
if ($RunId) { $StopArgs += @('--run-id', $RunId) }
& python @StopArgs
if ($LASTEXITCODE -ne 0) { throw 'Stopping the arena failed.' }
if (-not $KeepHosts) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File scripts/manage-hosts.ps1 -Action Remove
}
Write-Host 'Vuln Arena stopped. Images and private run evidence were preserved.' -ForegroundColor Green
