[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Summary,
    [string]$ScribeDir,
    [string]$Ticket,
    [switch]$Post,
    [double]$Hours,
    [string]$Begin,
    [string]$End,
    [string]$Project,
    [string]$Activity
)

$ErrorActionPreference = 'Stop'

$dateStr = Get-Date -Format 'yyyy-MM-dd'
$timeStr = Get-Date -Format 'HH:mm'

$branch = (& git rev-parse --abbrev-ref HEAD 2>$null)
if ([string]::IsNullOrWhiteSpace($branch)) { $branch = 'main' }

if ([string]::IsNullOrWhiteSpace($Ticket)) {
    $match = [regex]::Match($branch, '[A-Za-z]+-[0-9]+')
    $Ticket = if ($match.Success) { $match.Value.ToUpper() } else { '' }
}

if ([string]::IsNullOrWhiteSpace($ScribeDir)) {
    if ($env:KIMAI_SCRIBE_DIR) {
        $ScribeDir = $env:KIMAI_SCRIBE_DIR
    } else {
        $root = (& git rev-parse --show-toplevel 2>$null)
        if ([string]::IsNullOrWhiteSpace($root)) { $root = (Get-Location).Path }
        $ScribeDir = Join-Path $root 'private/gemini-scribe'
    }
}

[System.IO.Directory]::CreateDirectory($ScribeDir) | Out-Null
$logFile = Join-Path $ScribeDir "$dateStr-session.md"

$ticketTag = if ($Ticket) { "[$Ticket] " } else { "" }
$entryHeader = if ($Ticket) { "### 🕒 $timeStr — Ticket: $Ticket (Branch: $branch)" } else { "### 🕒 $timeStr — Branch: $branch" }

$entry = @"

$entryHeader
- **Summary:** $Summary
- **Kimai Note:** $ticketTag$Summary
"@

Add-Content -LiteralPath $logFile -Value $entry -Encoding UTF8

Write-Host "OK  Session logged to $logFile" -ForegroundColor Green
Write-Host ""
Write-Host "Kimai Timesheet copy-paste entry:" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------"
Write-Host "$ticketTag$Summary"
Write-Host "--------------------------------------------------------"

# Optional: Directly sync to Kimai REST API if requested
if ($Post) {
    $syncScript = Join-Path $PSScriptRoot 'kimai-sync.ps1'
    if (Test-Path -LiteralPath $syncScript) {
        Write-Host "`nSyncing directly to Kimai API..." -ForegroundColor Cyan
        $syncParams = @{
            Post     = $true
            Summary  = "$ticketTag$Summary"
        }
        if ($Hours -gt 0) { $syncParams['Hours'] = $Hours }
        if ($Begin) { $syncParams['Begin'] = $Begin }
        if ($End) { $syncParams['End'] = $End }
        if ($Project) { $syncParams['Project'] = $Project }
        if ($Activity) { $syncParams['Activity'] = $Activity }

        & $syncScript @syncParams
    }
} else {
    Write-Host "Tip: Add -Post (e.g. -Post -Hours 1.5) to book directly into Kimai!" -ForegroundColor Gray
}
