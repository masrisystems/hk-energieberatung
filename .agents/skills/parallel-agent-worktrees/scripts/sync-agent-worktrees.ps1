[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Repository,

    [string]$DestinationRoot,

    [string]$Remote = 'origin',

    [string]$MainBranch = 'main',

    [ValidateSet('codex', 'gemini', 'claude')]
    [string[]]$Agents = @('codex', 'gemini', 'claude'),

    [switch]$Apply
)

$ErrorActionPreference = 'Stop'
$failures = [System.Collections.Generic.List[string]]::new()

function Invoke-Git {
    param(
        [Parameter(Mandatory)][string]$Repo,
        [Parameter(Mandatory)][string[]]$Arguments
    )

    $output = & git -C $Repo @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed in ${Repo}:`n$($output -join "`n")"
    }

    return @($output)
}

function Get-FirstGitLine {
    param(
        [Parameter(Mandatory)][string]$Repo,
        [Parameter(Mandatory)][string[]]$Arguments
    )

    $line = [string](Invoke-Git -Repo $Repo -Arguments $Arguments | Where-Object { $_ -notlike 'warning:*' } | Select-Object -First 1)
    return $line.Trim()
}

$repositoryPath = (Resolve-Path -LiteralPath $Repository).Path
$repositoryPath = Get-FirstGitLine -Repo $repositoryPath -Arguments @('rev-parse', '--show-toplevel')
$repositoryPath = [System.IO.Path]::GetFullPath($repositoryPath)
$repositoryName = Split-Path -Leaf $repositoryPath

if (-not $DestinationRoot) {
    $centralRoot = Join-Path $HOME "worktrees\$repositoryName"
    $legacyRoot = Join-Path (Split-Path -Parent $repositoryPath) "$repositoryName-worktrees"
    if (Test-Path -LiteralPath $centralRoot) {
        $DestinationRoot = $centralRoot
    } elseif (Test-Path -LiteralPath (Join-Path $HOME 'worktrees')) {
        $DestinationRoot = $centralRoot
    } elseif (Test-Path -LiteralPath $legacyRoot) {
        $DestinationRoot = $legacyRoot
    } else {
        $DestinationRoot = $centralRoot
    }
}
$destinationRootPath = [System.IO.Path]::GetFullPath($DestinationRoot)
$mainRef = "$Remote/$MainBranch"

$mode = if ($Apply) { 'APPLY' } else { 'PREVIEW' }
Write-Output "Agent worktree freshness: $mode"
Write-Output "Repository: $repositoryPath"
Write-Output "Main ref: $mainRef"
Write-Output "Destination root: $destinationRootPath"

if ($Apply) {
    Write-Output "Fetching $Remote..."
    Invoke-Git -Repo $repositoryPath -Arguments @('fetch', $Remote, '--prune') | Where-Object { $_ -notlike 'warning:*' } | ForEach-Object { Write-Output "  $_" }
} else {
    Write-Output 'Preview uses the current remote-tracking ref and does not fetch.'
}

Invoke-Git -Repo $repositoryPath -Arguments @('rev-parse', '--verify', "$mainRef^{commit}") | Out-Null
$registeredLines = Invoke-Git -Repo $repositoryPath -Arguments @('worktree', 'list', '--porcelain')
$registered = @{}
$registeredByAgent = @{}
$currentWorktreePath = $null
foreach ($line in $registeredLines) {
    if ($line -like 'worktree *') {
        $currentWorktreePath = [System.IO.Path]::GetFullPath($line.Substring(9))
        $registered[$currentWorktreePath.ToLowerInvariant()] = $true
        $leaf = Split-Path -Leaf $currentWorktreePath
        if ($leaf -in $Agents) {
            $registeredByAgent[$leaf.ToLowerInvariant()] = $currentWorktreePath
        }
    } elseif ($line -like 'branch refs/heads/*') {
        $b = $line.Substring(18)
        foreach ($ag in $Agents) {
            if ($b -like "$ag/*" -and $currentWorktreePath) {
                $registeredByAgent[$ag.ToLowerInvariant()] = $currentWorktreePath
            }
        }
    }
}

foreach ($agent in $Agents) {
    $destination = if ($registeredByAgent.ContainsKey($agent.ToLowerInvariant())) {
        $registeredByAgent[$agent.ToLowerInvariant()]
    } else {
        [System.IO.Path]::GetFullPath((Join-Path $destinationRootPath $agent))
    }
    $destinationKey = $destination.ToLowerInvariant()

    if (-not $registered.ContainsKey($destinationKey)) {
        $message = "$agent worktree is not registered at $destination"
        Write-Warning $message
        $failures.Add($message)
        continue
    }

    $branch = Get-FirstGitLine -Repo $destination -Arguments @('branch', '--show-current')
    if (-not $branch -or $branch -notlike "$agent/*") {
        $message = "$agent worktree uses '$branch', expected an '$agent/*' branch"
        Write-Warning $message
        $failures.Add($message)
        continue
    }

    $changes = @(Invoke-Git -Repo $destination -Arguments @('status', '--porcelain') | Where-Object { $_ -notlike 'warning:*' })
    if ($changes.Count -gt 0) {
        $message = "$agent worktree is dirty on $branch; synchronization skipped"
        Write-Warning $message
        $changes | ForEach-Object { Write-Output "  $_" }
        $failures.Add($message)
        continue
    }

    $countsLine = Get-FirstGitLine -Repo $destination -Arguments @('rev-list', '--left-right', '--count', "HEAD...$mainRef")
    $counts = $countsLine -split '\s+'
    $ahead = [int]$counts[0]
    $behind = [int]$counts[1]
    Write-Output "  $agent [$branch]: ahead $ahead, behind $behind"

    if ($behind -eq 0) {
        Write-Output "    CURRENT $mainRef is already integrated"
        continue
    }

    Write-Output "    PLAN merge $mainRef into $branch"
    if (-not $Apply) {
        continue
    }

    $mergeOutput = & git -C $destination merge --no-edit --no-ff $mainRef 2>&1
    if ($LASTEXITCODE -ne 0) {
        $abortOutput = & git -C $destination merge --abort 2>&1
        $message = "$agent merge conflicted or failed and was aborted: $($mergeOutput -join ' ')"
        if ($LASTEXITCODE -ne 0) {
            $message += " Abort also failed: $($abortOutput -join ' ')"
        }
        Write-Warning $message
        $failures.Add($message)
        continue
    }

    $mergeOutput | Where-Object { $_ -notlike 'warning:*' } | ForEach-Object { Write-Output "    $_" }
}

if (-not $Apply) {
    Write-Output 'No changes made. Re-run with -Apply to fetch and merge the planned updates.'
}

if ($failures.Count -gt 0) {
    Write-Warning "$($failures.Count) worktree(s) need attention."
    exit 2
}
