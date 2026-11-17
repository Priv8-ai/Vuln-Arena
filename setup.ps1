[CmdletBinding()]
param(
    [string]$Machines = 'all',
    [string]$RunId,
    [switch]$SkipHosts,
    [switch]$SkipBuild,
    [switch]$SkipFullVerification,
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSCommandPath
Set-Location -LiteralPath $Root

function Write-Stage([string]$Message) {
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Test-Administrator {
    $Identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $Principal = [Security.Principal.WindowsPrincipal]::new($Identity)
    return $Principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not $SkipHosts -and -not (Test-Administrator)) {
    Write-Host 'Administrator access is needed only to install arena.test hostnames. Requesting elevation...' -ForegroundColor Yellow
    $Forward = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"", '-Machines', "`"$Machines`"")
    if ($RunId) { $Forward += @('-RunId', "`"$RunId`"") }
    if ($SkipBuild) { $Forward += '-SkipBuild' }
    if ($SkipFullVerification) { $Forward += '-SkipFullVerification' }
    if ($NoBrowser) { $Forward += '-NoBrowser' }
    Start-Process powershell.exe -Verb RunAs -ArgumentList ($Forward -join ' ')
    exit 0
}

Write-Stage 'Checking prerequisites'
foreach ($Command in @('docker', 'python')) {
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) { throw "$Command is required but was not found in PATH." }
}
& docker info --format '{{.ServerVersion}}' | ForEach-Object { Write-Host "Docker Engine $_" }
if ($LASTEXITCODE -ne 0) { throw 'Docker Engine is not running. Start Docker Desktop and run setup again.' }

Write-Stage 'Generating benchmark manifests and domain assets'
& python scripts/build_findings_baseline.py
if ($LASTEXITCODE -ne 0) { throw 'Finding baseline generation failed.' }
& python scripts/build_machine_manifest.py
if ($LASTEXITCODE -ne 0) { throw 'Machine manifest generation failed.' }
& python scripts/build_router_assets.py
if ($LASTEXITCODE -ne 0) { throw 'Router asset generation failed.' }

if (-not $SkipHosts) {
    Write-Stage 'Installing friendly arena.test hostnames'
    & powershell -NoProfile -ExecutionPolicy Bypass -File scripts/manage-hosts.ps1 -Action Install
}

Write-Stage 'Running preflight checks'
& python arena.py doctor
if ($LASTEXITCODE -ne 0) { throw 'Preflight failed. Review the messages above.' }

if (-not $RunId) { $RunId = 'local-' + (Get-Date -Format 'yyyyMMdd-HHmmss') }
Write-Stage "Starting $Machines as run $RunId"
$StartArgs = @('arena.py', 'start', '--machines', $Machines, '--run-id', $RunId, '--wait-seconds', '120')
if ($SkipBuild) { $StartArgs += '--no-build' }
& python @StartArgs
if ($LASTEXITCODE -ne 0) { throw 'Arena startup failed.' }

Write-Stage 'Verifying direct ports and local domains'
& python scripts/verify_domains.py --json-out "runs/$RunId/domains.json"
if ($LASTEXITCODE -ne 0) { throw 'Domain routing verification failed.' }
if (-not $SkipFullVerification) {
    & python arena.py verify --machines $Machines --mode full --run-id $RunId --out-dir "runs/$RunId/verification"
    if ($LASTEXITCODE -ne 0) { throw 'Full benchmark verification failed.' }
}

[IO.File]::WriteAllText((Join-Path $Root 'runs\current-run.txt'), $RunId + [Environment]::NewLine)
$DashboardUrl = if ($SkipHosts) { 'http://arena.localhost:18080' } else { 'http://arena.test:18080' }
Write-Host "`nVuln Arena is ready." -ForegroundColor Green
Write-Host "Dashboard:       $DashboardUrl"
Write-Host 'Zero-config URL: http://arena.localhost:18080'
Write-Host "Agent pack:      runs\$RunId\agent-pack.json"
Write-Host "Private run:     runs\$RunId (do not share private.env)"

if (-not $NoBrowser) { Start-Process $DashboardUrl }
