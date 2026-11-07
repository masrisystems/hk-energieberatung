[CmdletBinding()]
param(
    [switch]$Test,
    [switch]$Post,
    [switch]$Csv,
    [string]$Summary,
    [string]$Date,
    [string]$Begin,
    [string]$End,
    [double]$Hours,
    [string]$Project,
    [string]$Activity,
    [string]$Tags,
    [string]$EnvFile
)

$ErrorActionPreference = 'Stop'

# --- 1. Locate and Load Environment Config ---
if ([string]::IsNullOrWhiteSpace($EnvFile)) {
    $gitRoot = try { (& git rev-parse --show-toplevel 2>$null) } catch { $null }
    $searchList = [System.Collections.Generic.List[string]]::new()
    $searchList.Add((Join-Path (Get-Location).Path '.kimai.env'))
    $searchList.Add((Join-Path (Get-Location).Path 'kimai.env'))
    if ($gitRoot) {
        $searchList.Add((Join-Path $gitRoot '.kimai.env'))
        $searchList.Add((Join-Path $gitRoot 'kimai.env'))
    }
    $searchList.Add("C:\Users\super\.agents\config\kimai.env")

    $searchPaths = $searchList | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -First 1

    if ($searchPaths) {
        $EnvFile = [string]$searchPaths
    } else {
        $EnvFile = "C:\Users\super\.agents\config\kimai.env"
    }
}

$config = @{}
if (Test-Path -LiteralPath $EnvFile) {
    Get-Content -LiteralPath $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith('#') -and $line -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $val = $matches[2].Trim().Trim('"').Trim("'")
            $config[$key] = $val
        }
    }
}

$kimaiUrl = if ($env:KIMAI_URL) { $env:KIMAI_URL } elseif ($config.ContainsKey('KIMAI_URL')) { $config['KIMAI_URL'] } else { '' }
$kimaiUser = if ($env:KIMAI_USER) { $env:KIMAI_USER } elseif ($config.ContainsKey('KIMAI_USER')) { $config['KIMAI_USER'] } else { '' }
$kimaiToken = if ($env:KIMAI_TOKEN) { $env:KIMAI_TOKEN } elseif ($config.ContainsKey('KIMAI_TOKEN')) { $config['KIMAI_TOKEN'] } else { '' }

$defaultProject = if ($config.ContainsKey('KIMAI_DEFAULT_PROJECT')) { $config['KIMAI_DEFAULT_PROJECT'] } else { '' }
$defaultActivity = if ($config.ContainsKey('KIMAI_DEFAULT_ACTIVITY')) { $config['KIMAI_DEFAULT_ACTIVITY'] } else { '' }
$defaultTags = if ($config.ContainsKey('KIMAI_DEFAULT_TAGS')) { $config['KIMAI_DEFAULT_TAGS'] } else { 'development' }
$defaultBegin = if ($config.ContainsKey('KIMAI_DEFAULT_BEGIN')) { $config['KIMAI_DEFAULT_BEGIN'] } else { '08:30' }
$defaultEnd = if ($config.ContainsKey('KIMAI_DEFAULT_END')) { $config['KIMAI_DEFAULT_END'] } else { '17:00' }

# Normalize URL (strip trailing /en/timesheet/ or trailing slashes)
if ($kimaiUrl) {
    if ($kimaiUrl -match '^(https?://[^/]+)(/.*)?$') {
        $baseHost = $matches[1]
        $subPath = $matches[2]
        if ($subPath -and $subPath -match '^/(en|de|fr|es)?/?(timesheet|dashboard|invoice|project|activity|admin|profile)?/?$') {
            $kimaiUrl = $baseHost
        } else {
            $kimaiUrl = $kimaiUrl.TrimEnd('/')
        }
    } else {
        $kimaiUrl = $kimaiUrl.TrimEnd('/')
    }
}

function Get-KimaiHeaders {
    if ([string]::IsNullOrWhiteSpace($kimaiUrl) -or [string]::IsNullOrWhiteSpace($kimaiUser) -or [string]::IsNullOrWhiteSpace($kimaiToken)) {
        Write-Error "Kimai configuration missing or incomplete in '$EnvFile'. Please set KIMAI_URL, KIMAI_USER, and KIMAI_TOKEN."
        exit 1
    }
    return @{
        'X-AUTH-USER' = $kimaiUser
        'X-AUTH-TOKEN' = $kimaiToken
        'Accept'       = 'application/json'
    }
}

# --- 2. Action: Test Connection ---
if ($Test) {
    if (-not (Test-Path -LiteralPath $EnvFile)) {
        Write-Host "Config file not found: $EnvFile" -ForegroundColor Red
        Write-Host "Create one from the template:" -ForegroundColor Yellow
        Write-Host "  Copy-Item 'C:\Users\super\.agents\config\kimai.env.example' '$EnvFile'"
        exit 1
    }

    Write-Host "Testing connection to $kimaiUrl for user '$kimaiUser'..." -ForegroundColor Cyan
    $headers = Get-KimaiHeaders

    try {
        $ping = Invoke-RestMethod -Uri "$kimaiUrl/api/ping" -Headers $headers -Method Get
        Write-Host "OK  Connection established! ($($ping.message))" -ForegroundColor Green
    } catch {
        Write-Host "Failed to connect to Kimai: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }

    try {
        $userMe = Invoke-RestMethod -Uri "$kimaiUrl/api/users/me" -Headers $headers -Method Get
        Write-Host "Logged in as: $($userMe.username) ($($userMe.alias))" -ForegroundColor Green
    } catch {}

    Write-Host "`n--- Available Projects ---" -ForegroundColor Cyan
    try {
        $projects = Invoke-RestMethod -Uri "$kimaiUrl/api/projects" -Headers $headers -Method Get
        $projects | Select-Object @{N='ID';E={$_.id}}, @{N='Project Name';E={$_.name}}, @{N='Customer ID';E={$_.customer}} | Format-Table -AutoSize
    } catch {
        Write-Host "Could not retrieve projects: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Write-Host "--- Available Activities ---" -ForegroundColor Cyan
    try {
        $activities = Invoke-RestMethod -Uri "$kimaiUrl/api/activities" -Headers $headers -Method Get
        $activities | Select-Object @{N='ID';E={$_.id}}, @{N='Activity Name';E={$_.name}}, @{N='Project ID';E={$_.project}} | Format-Table -AutoSize
    } catch {
        Write-Host "Could not retrieve activities: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Write-Host "Config file: $EnvFile" -ForegroundColor Gray
    exit 0
}

# --- 3. Resolve Times and Dates ---
$targetDate = if ($Date) { $Date } else { (Get-Date -Format 'yyyy-MM-dd') }
$beginTime = if ($Begin) { $Begin } else { $defaultBegin }

if ($Hours -gt 0) {
    try {
        $dtStart = [DateTime]::ParseExact("$targetDate $beginTime", 'yyyy-MM-dd HH:mm', $null)
        $endTime = $dtStart.AddHours($Hours).ToString('HH:mm')
    } catch {
        $endTime = $defaultEnd
    }
} elseif ($End) {
    $endTime = $End
} else {
    $endTime = $defaultEnd
}

# --- 4. Resolve Context & Summary ---
$branch = try { (& git rev-parse --abbrev-ref HEAD 2>$null) } catch { 'main' }
if ([string]::IsNullOrWhiteSpace($branch)) { $branch = 'main' }
$ticketMatch = [regex]::Match($branch, '[A-Za-z]+-[0-9]+')
$ticket = if ($ticketMatch.Success) { $ticketMatch.Value.ToUpper() } else { '' }

# Detect project name from directory
$currentDir = (Get-Location).Path
$gitRoot = try { (& git rev-parse --show-toplevel 2>$null) } catch { $null }
$repoFolder = if ($gitRoot) { Split-Path -Leaf $gitRoot } else { Split-Path -Leaf $currentDir }

if ([string]::IsNullOrWhiteSpace($Summary)) {
    # Attempt to read last Kimai Note from today's scribe log
    $scribeDir = if ($env:KIMAI_SCRIBE_DIR) { $env:KIMAI_SCRIBE_DIR } elseif ($gitRoot) { Join-Path $gitRoot 'private/gemini-scribe' } else { Join-Path $currentDir 'private/gemini-scribe' }
    $todayLog = Join-Path $scribeDir "$targetDate-session.md"
    if (Test-Path -LiteralPath $todayLog) {
        $notes = Get-Content -LiteralPath $todayLog | Where-Object { $_ -match '^\- \*\*Kimai Note:\*\*\s*(.+)$' }
        if ($notes.Count -gt 0) {
            $Summary = $matches[1]
        }
    }
    if ([string]::IsNullOrWhiteSpace($Summary)) {
        $Summary = if ($ticket) { "[$ticket] Development in $repoFolder" } else { "Development in $repoFolder" }
    }
}

# Format Description with ticket if available and not already present
if ($ticket -and -not $Summary.Contains("[$ticket]")) {
    $Summary = "[$ticket] $Summary"
}

# Resolve Tags
$combinedTags = if ($Tags) { $Tags } else { $defaultTags }
if ($repoFolder -and -not $combinedTags.Contains($repoFolder)) {
    $combinedTags = "$combinedTags,$repoFolder"
}

# --- 5. Resolve Project and Activity IDs ---
$headers = $null
function Resolve-Ids {
    param([ref]$projId, [ref]$actId)
    $script:headers = Get-KimaiHeaders

    # Resolve Project
    if ($projId.Value -match '^\d+$') {
        $projId.Value = [int]$projId.Value
    } else {
        $searchName = if ($projId.Value) { $projId.Value } elseif ($defaultProject) { $defaultProject } else { $repoFolder }
        if ($searchName -match '^\d+$') {
            $projId.Value = [int]$searchName
        } else {
            try {
                $allProjects = Invoke-RestMethod -Uri "$kimaiUrl/api/projects" -Headers $script:headers -Method Get
                $match = $allProjects | Where-Object { $_.name -like "*$searchName*" } | Select-Object -First 1
                if ($match) {
                    $projId.Value = [int]$match.id
                } elseif ($allProjects.Count -gt 0) {
                    $projId.Value = [int]$allProjects[0].id
                }
            } catch {
                Write-Error "Failed to fetch projects from Kimai: $($_.Exception.Message)"
                exit 1
            }
        }
    }

    # Resolve Activity
    if ($actId.Value -match '^\d+$') {
        $actId.Value = [int]$actId.Value
    } else {
        $searchAct = if ($actId.Value) { $actId.Value } elseif ($defaultActivity) { $defaultActivity } else { 'Programmierung' }
        if ($searchAct -match '^\d+$') {
            $actId.Value = [int]$searchAct
        } else {
            try {
                $allActivities = Invoke-RestMethod -Uri "$kimaiUrl/api/activities" -Headers $script:headers -Method Get
                $match = $allActivities | Where-Object { $_.name -like "*$searchAct*" } | Select-Object -First 1
                if (-not $match) {
                    $match = $allActivities | Where-Object { $_.name -like "*Dev*" -or $_.name -like "*Entwicklung*" } | Select-Object -First 1
                }
                if ($match) {
                    $actId.Value = [int]$match.id
                } elseif ($allActivities.Count -gt 0) {
                    $actId.Value = [int]$allActivities[0].id
                }
            } catch {
                Write-Error "Failed to fetch activities from Kimai: $($_.Exception.Message)"
                exit 1
            }
        }
    }
}

# --- 6. Execute Actions ---

if ($Post) {
    $resolvedProject = $Project
    $resolvedActivity = $Activity
    Resolve-Ids ([ref]$resolvedProject) ([ref]$resolvedActivity)

    $isoBegin = "${targetDate}T${beginTime}:00"
    $isoEnd = "${targetDate}T${endTime}:00"

    $payload = @{
        begin       = $isoBegin
        end         = $isoEnd
        project     = [int]$resolvedProject
        activity    = [int]$resolvedActivity
        description = $Summary
        tags        = $combinedTags
    } | ConvertTo-Json

    Write-Host "Posting timesheet entry to Kimai ($kimaiUrl)..." -ForegroundColor Cyan
    Write-Host "  Date:     $targetDate ($beginTime - $endTime)"
    Write-Host "  Project:  ID $resolvedProject | Activity: ID $resolvedActivity"
    Write-Host "  Tags:     $combinedTags"
    Write-Host "  Summary:  $Summary"

    try {
        $response = Invoke-RestMethod -Uri "$kimaiUrl/api/timesheets" -Headers $headers -Method Post -Body $payload -ContentType 'application/json'
        Write-Host "OK  Successfully booked into Kimai! (Timesheet Entry ID: $($response.id))" -ForegroundColor Green
        exit 0
    } catch {
        Write-Host "API booking failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Creating fallback CSV import file..." -ForegroundColor Yellow
        $Csv = $true
    }
}

if ($Csv) {
    $csvDir = if ($gitRoot) { Join-Path $gitRoot 'private/gemini-scribe' } else { Join-Path $currentDir 'private/gemini-scribe' }
    [System.IO.Directory]::CreateDirectory($csvDir) | Out-Null
    $csvFile = Join-Path $csvDir "kimai-import-$targetDate.csv"

    $csvContent = @"
"date","begin","end","project","activity","description","tags"
"$targetDate","$beginTime","$endTime","$Project","$Activity","$Summary","$combinedTags"
"@
    Set-Content -LiteralPath $csvFile -Value $csvContent -Encoding UTF8
    Write-Host "OK  CSV Import file created: $csvFile" -ForegroundColor Green
    Write-Host "In Kimai UI: Timesheets -> Import -> Upload this CSV file." -ForegroundColor Cyan
    exit 0
}

# Default display mode (Copy-Paste snippet)
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "   KIMAI TIMESHEET HELPER" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Date:     $targetDate ($beginTime - $endTime)"
Write-Host "Project:  $repoFolder $(if ($Project) { "(ID $Project)" })"
Write-Host "Tags:     $combinedTags"
Write-Host ""
Write-Host "Kimai Entry Note (Copy & Paste):" -ForegroundColor Green
Write-Host "--------------------------------------------------------------------------------"
Write-Host "$Summary"
Write-Host "--------------------------------------------------------------------------------"
Write-Host ""
Write-Host "One-Click REST API Actions:" -ForegroundColor Yellow
Write-Host "  Book now:     pwsh -File C:\Users\super\.agents\skills\session-logger\scripts\kimai-sync.ps1 -Post"
Write-Host "  Custom hours: pwsh -File C:\Users\super\.agents\skills\session-logger\scripts\kimai-sync.ps1 -Post -Hours 2 -Summary 'Fixed issue'"
Write-Host "  Test setup:   pwsh -File C:\Users\super\.agents\skills\session-logger\scripts\kimai-sync.ps1 -Test"
Write-Host "================================================================================" -ForegroundColor Cyan
