[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$SkipClaudeLinks,
    [switch]$SkipCodexLinks,
    [switch]$SkipRules,
    [switch]$MigrateLegacyRules
)

$ErrorActionPreference = 'Stop'

$userProfilePath = [Environment]::GetFolderPath('UserProfile')
$sharedRoot = Join-Path $userProfilePath '.agents'
$sharedSkillsRoot = Join-Path $sharedRoot 'skills'
$instructionsRoot = Join-Path $sharedRoot 'instructions'
$backupRoot = Join-Path $sharedRoot ('backups\' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$beginMarker = '<!-- BEGIN SHARED-AGENT-CONFIG -->'
$endMarker = '<!-- END SHARED-AGENT-CONFIG -->'
$changes = [System.Collections.Generic.List[string]]::new()
$conflicts = [System.Collections.Generic.List[string]]::new()
$verified = [System.Collections.Generic.List[string]]::new()

function Read-Utf8Text {
    param([Parameter(Mandatory)][string]$Path)

    return [System.IO.File]::ReadAllText($Path)
}

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content
    )

    $parentPath = Split-Path -Parent $Path
    [System.IO.Directory]::CreateDirectory($parentPath) | Out-Null
    [System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))
}

function Backup-RuleFile {
    param(
        [Parameter(Mandatory)][string]$Agent,
        [Parameter(Mandatory)][string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    $agentBackupRoot = Join-Path $backupRoot $Agent
    [System.IO.Directory]::CreateDirectory($agentBackupRoot) | Out-Null
    Copy-Item -LiteralPath $Path -Destination (Join-Path $agentBackupRoot (Split-Path -Leaf $Path)) -Force
}

function Get-ManagedBlock {
    param([Parameter(Mandatory)][ValidateSet('codex', 'claude', 'gemini')][string]$Agent)

    $globalPath = Join-Path $instructionsRoot 'global.md'
    $adapterPath = Join-Path $instructionsRoot "adapters\$Agent.md"

    $body = (Read-Utf8Text -Path $globalPath).TrimEnd() + "`r`n`r`n" + (Read-Utf8Text -Path $adapterPath).TrimEnd()

    return "$beginMarker`r`n$body`r`n$endMarker"
}

function Sync-RuleFile {
    param(
        [Parameter(Mandatory)][ValidateSet('codex', 'claude', 'gemini')][string]$Agent,
        [Parameter(Mandatory)][string]$Path
    )

    $managedBlock = Get-ManagedBlock -Agent $Agent
    $existingContent = if (Test-Path -LiteralPath $Path) { Read-Utf8Text -Path $Path } else { '' }

    if ($MigrateLegacyRules) {
        $preservedContent = ''
        if ($Agent -eq 'gemini' -and $existingContent -match '(?s)<claude-mem-context>.*?</claude-mem-context>') {
            $preservedContent = $matches[0].Trim() + "`r`n`r`n"
        }
        $nextContent = $preservedContent + $managedBlock + "`r`n"
    } elseif ($existingContent.Contains($beginMarker) -and $existingContent.Contains($endMarker)) {
        $pattern = [regex]::Escape($beginMarker) + '.*?' + [regex]::Escape($endMarker)
        $nextContent = [regex]::Replace($existingContent, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $managedBlock }, [System.Text.RegularExpressions.RegexOptions]::Singleline)
    } else {
        $nextContent = $managedBlock + "`r`n`r`n" + $existingContent.TrimStart()
    }

    if ($nextContent -eq $existingContent) {
        $verified.Add("rules:$Agent")
        return
    }

    $changes.Add("rules:$Agent -> $Path")
    if ($Apply) {
        Backup-RuleFile -Agent $Agent -Path $Path
        Write-Utf8NoBom -Path $Path -Content $nextContent
    }
}

function Sync-SkillLinks {
    param(
        [Parameter(Mandatory)][ValidateSet('claude', 'codex')][string]$Agent,
        [Parameter(Mandatory)][string]$SkillsRoot
    )

    [System.IO.Directory]::CreateDirectory($SkillsRoot) | Out-Null

    foreach ($skillDirectory in Get-ChildItem -LiteralPath $sharedSkillsRoot -Directory -Force | Where-Object { $_.Name -notin @('synced', '.staging') -and -not $_.Name.StartsWith('.') } | Sort-Object Name) {
        $skillFile = Join-Path $skillDirectory.FullName 'SKILL.md'
        if (-not (Test-Path -LiteralPath $skillFile)) {
            $conflicts.Add("invalid-shared-skill:$($skillDirectory.Name) has no SKILL.md")
            continue
        }

        $destinationPath = Join-Path $SkillsRoot $skillDirectory.Name
        if (-not (Test-Path -LiteralPath $destinationPath)) {
            $changes.Add("$Agent-link:$($skillDirectory.Name)")
            if ($Apply) {
                New-Item -ItemType Junction -Path $destinationPath -Target $skillDirectory.FullName | Out-Null
            }
            continue
        }

        $destinationItem = Get-Item -LiteralPath $destinationPath -Force
        $targets = @()
        if ($destinationItem.LinkType -and $destinationItem.Target) {
            $targets = @($destinationItem.Target | Where-Object { $_ } | ForEach-Object { [System.IO.Path]::GetFullPath($_) })
        }
        $expectedTarget = [System.IO.Path]::GetFullPath($skillDirectory.FullName)
        if ($destinationItem.LinkType -and $targets -contains $expectedTarget) {
            $verified.Add("$Agent-link:$($skillDirectory.Name)")
        } else {
            $kind = if ($destinationItem.LinkType) { $destinationItem.LinkType } else { 'physical' }
            $conflicts.Add("$Agent-link:$($skillDirectory.Name) destination is $kind; preserved")
        }
    }
}

if (-not (Test-Path -LiteralPath $sharedSkillsRoot)) {
    throw "Shared skills root does not exist: $sharedSkillsRoot"
}

if (-not $SkipClaudeLinks) {
    Sync-SkillLinks -Agent 'claude' -SkillsRoot (Join-Path $userProfilePath '.claude\skills')
}

if (-not $SkipCodexLinks) {
    Sync-SkillLinks -Agent 'codex' -SkillsRoot (Join-Path $userProfilePath '.codex\skills')
}

if (-not $SkipRules) {
    Sync-RuleFile -Agent 'codex' -Path (Join-Path $userProfilePath '.codex\AGENTS.md')
    Sync-RuleFile -Agent 'claude' -Path (Join-Path $userProfilePath '.claude\CLAUDE.md')
    Sync-RuleFile -Agent 'gemini' -Path (Join-Path $userProfilePath '.gemini\GEMINI.md')
}

$mode = if ($Apply) { 'APPLY' } else { 'DRY-RUN' }
Write-Output "Shared agent synchronization: $mode"
Write-Output "Changes: $($changes.Count)"
$changes | ForEach-Object { Write-Output "  CHANGE $_" }
Write-Output "Verified: $($verified.Count)"
$verified | ForEach-Object { Write-Output "  OK $_" }
Write-Output "Conflicts: $($conflicts.Count)"
$conflicts | ForEach-Object { Write-Output "  CONFLICT $_" }

if ($conflicts.Count -gt 0) {
    exit 2
}

exit 0
