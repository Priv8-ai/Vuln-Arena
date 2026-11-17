[CmdletBinding()]
param(
    [ValidateSet('Install', 'Remove', 'Status')]
    [string]$Action = 'Status',
    [string]$HostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$BlockPath = Join-Path $Root 'config\hosts.arena.test'
$StartMarker = '# BEGIN VULN ARENA MANAGED HOSTS'
$EndMarker = '# END VULN ARENA MANAGED HOSTS'

function Remove-ArenaBlock([string]$Content) {
    $Pattern = '(?ms)^\s*' + [regex]::Escape($StartMarker) + '.*?' + [regex]::Escape($EndMarker) + '\s*(?:\r?\n)?'
    return [regex]::Replace($Content, $Pattern, '').TrimEnd() + [Environment]::NewLine
}

if (-not (Test-Path -LiteralPath $HostsPath)) {
    throw "Hosts file not found: $HostsPath"
}
$Current = [IO.File]::ReadAllText($HostsPath)
$Installed = $Current.Contains($StartMarker) -and $Current.Contains($EndMarker)

switch ($Action) {
    'Status' {
        if ($Installed) { Write-Host 'Vuln Arena hosts entries are installed.' -ForegroundColor Green }
        else { Write-Host 'Vuln Arena hosts entries are not installed.' -ForegroundColor Yellow }
    }
    'Remove' {
        if ($Installed) {
            [IO.File]::WriteAllText($HostsPath, (Remove-ArenaBlock $Current), [Text.UTF8Encoding]::new($false))
            & ipconfig /flushdns | Out-Null
            Write-Host 'Removed Vuln Arena hosts entries and flushed DNS.' -ForegroundColor Green
        } else {
            Write-Host 'No Vuln Arena hosts block was present.' -ForegroundColor Yellow
        }
    }
    'Install' {
        if (-not (Test-Path -LiteralPath $BlockPath)) { throw "Generated hosts block missing: $BlockPath" }
        $Clean = Remove-ArenaBlock $Current
        $Block = [IO.File]::ReadAllText($BlockPath).Trim()
        $Next = $Clean.TrimEnd() + [Environment]::NewLine + [Environment]::NewLine + $Block + [Environment]::NewLine
        [IO.File]::WriteAllText($HostsPath, $Next, [Text.UTF8Encoding]::new($false))
        & ipconfig /flushdns | Out-Null
        Write-Host 'Installed arena.test entries for the dashboard and all 44 machines.' -ForegroundColor Green
    }
}
