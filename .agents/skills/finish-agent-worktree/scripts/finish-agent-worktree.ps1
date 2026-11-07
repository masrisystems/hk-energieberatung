[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Repository,

    [string]$IntegrationWorktree,

    [string]$Remote = 'origin',

    [string]$MainBranch = 'main',

    [switch]$Apply
)

$ErrorActionPreference = 'Stop'

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

function Get-GitLine {
    param(
        [Parameter(Mandatory)][string]$Repo,
        [Parameter(Mandatory)][string[]]$Arguments
    )

    $line = [string](Invoke-Git -Repo $Repo -Arguments $Arguments | Where-Object { $_ -notlike 'warning:*' } | Select-Object -First 1)
    return $line.Trim()
}

function Get-CleanStatus {
    param([Parameter(Mandatory)][string]$Repo)

    return @(Invoke-Git -Repo $Repo -Arguments @('status', '--porcelain') | Where-Object { $_ -notlike 'warning:*' })
}

function Invoke-SafeMerge {
    param(
        [Parameter(Mandatory)][string]$Repo,
        [Parameter(Mandatory)][string]$Ref,
        [Parameter(Mandatory)][string]$Label,
        [switch]$AllowFastForward
    )

    $arguments = @('merge', '--no-edit')
    if (-not $AllowFastForward) {
        $arguments += '--no-ff'
    }
    $arguments += $Ref

    $output = & git -C $Repo @arguments 2>&1
    if ($LASTEXITCODE -eq 0) {
        $output | Where-Object { $_ -notlike 'warning:*' } | ForEach-Object { Write-Output "    $_" }
        return
    }

    $mergeHead = & git -C $Repo rev-parse -q --verify MERGE_HEAD 2>$null
    if ($LASTEXITCODE -eq 0 -and $mergeHead) {
        $abortOutput = & git -C $Repo merge --abort 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "$Label failed, and merge abort also failed:`n$($abortOutput -join "`n")"
        }
    }
    throw "$Label failed and was aborted when necessary:`n$($output -join "`n")"
}

$sourcePath = (Resolve-Path -LiteralPath $Repository).Path
$sourcePath = [System.IO.Path]::GetFullPath((Get-GitLine -Repo $sourcePath -Arguments @('rev-parse', '--show-toplevel')))
$sourceBranch = Get-GitLine -Repo $sourcePath -Arguments @('branch', '--show-current')
if (-not $sourceBranch) {
    throw 'The source worktree is in detached HEAD state.'
}
if ($sourceBranch -eq $MainBranch) {
    throw "The source worktree is already on '$MainBranch'; provide the completed agent feature worktree instead."
}

$worktreeLines = Invoke-Git -Repo $sourcePath -Arguments @('worktree', 'list', '--porcelain')
if (-not $IntegrationWorktree) {
    $candidatePath = $null
    foreach ($line in $worktreeLines) {
        if ($line -like 'worktree *') {
            $candidatePath = $line.Substring(9)
            continue
        }
        if ($line -eq "branch refs/heads/$MainBranch" -and $candidatePath) {
            $IntegrationWorktree = $candidatePath
            break
        }
    }
}
if (-not $IntegrationWorktree) {
    throw "No registered worktree for '$MainBranch' was found. Pass -IntegrationWorktree explicitly."
}
$integrationPath = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $IntegrationWorktree).Path)
$integrationBranch = Get-GitLine -Repo $integrationPath -Arguments @('branch', '--show-current')
if ($integrationBranch -ne $MainBranch) {
    throw "Integration worktree $integrationPath uses '$integrationBranch', expected '$MainBranch'."
}
if ($integrationPath -eq $sourcePath) {
    throw 'Source and integration worktrees must be different directories.'
}

$sourceChanges = Get-CleanStatus -Repo $sourcePath
$integrationChanges = Get-CleanStatus -Repo $integrationPath
$remoteMain = "$Remote/$MainBranch"

$mode = if ($Apply) { 'APPLY' } else { 'PREVIEW' }
Write-Output "Finish agent worktree: $mode"
Write-Output "Source: $sourcePath [$sourceBranch]"
Write-Output "Integration: $integrationPath [$integrationBranch]"
Write-Output "Remote main: $remoteMain"

if ($sourceChanges.Count -gt 0) {
    Write-Warning 'Source worktree is dirty. Commit the finished scoped changes before integration.'
    $sourceChanges | ForEach-Object { Write-Output "  $_" }
}
if ($integrationChanges.Count -gt 0) {
    Write-Warning 'Main integration worktree is dirty. Preserve or finish those changes before integration.'
    $integrationChanges | ForEach-Object { Write-Output "  $_" }
}
if ($sourceChanges.Count -gt 0 -or $integrationChanges.Count -gt 0) {
    throw 'Integration stopped because every participating worktree must be clean.'
}

Invoke-Git -Repo $sourcePath -Arguments @('rev-parse', '--verify', "$remoteMain^{commit}") | Out-Null
$sourceCounts = (Get-GitLine -Repo $sourcePath -Arguments @('rev-list', '--left-right', '--count', "HEAD...$remoteMain")) -split '\s+'
$mainCounts = (Get-GitLine -Repo $integrationPath -Arguments @('rev-list', '--left-right', '--count', "HEAD...$remoteMain")) -split '\s+'
Write-Output "Source vs ${remoteMain}: ahead $($sourceCounts[0]), behind $($sourceCounts[1])"
Write-Output "Main vs ${remoteMain}: ahead $($mainCounts[0]), behind $($mainCounts[1])"
Write-Output "PLAN merge $remoteMain into $sourceBranch when needed"
Write-Output "PLAN update $MainBranch from $remoteMain, preserving local commits"
Write-Output "PLAN merge $sourceBranch into $MainBranch"

if (-not $Apply) {
    Write-Output 'No changes made. Re-run with -Apply after review.'
    exit 0
}

Write-Output "Fetching $Remote..."
Invoke-Git -Repo $sourcePath -Arguments @('fetch', $Remote, '--prune') | Where-Object { $_ -notlike 'warning:*' } | ForEach-Object { Write-Output "  $_" }

if ((Get-CleanStatus -Repo $sourcePath).Count -gt 0 -or (Get-CleanStatus -Repo $integrationPath).Count -gt 0) {
    throw 'A participating worktree changed after preview/fetch. Integration stopped.'
}

$sourceBehind = [int](((Get-GitLine -Repo $sourcePath -Arguments @('rev-list', '--left-right', '--count', "HEAD...$remoteMain")) -split '\s+')[1])
if ($sourceBehind -gt 0) {
    Write-Output "Merging $remoteMain into $sourceBranch..."
    Invoke-SafeMerge -Repo $sourcePath -Ref $remoteMain -Label "Source synchronization with $remoteMain"
}

$mainBehind = [int](((Get-GitLine -Repo $integrationPath -Arguments @('rev-list', '--left-right', '--count', "HEAD...$remoteMain")) -split '\s+')[1])
if ($mainBehind -gt 0) {
    Write-Output "Updating $MainBranch from $remoteMain..."
    Invoke-SafeMerge -Repo $integrationPath -Ref $remoteMain -Label "Main update from $remoteMain" -AllowFastForward
}

Write-Output "Merging $sourceBranch into $MainBranch..."
Invoke-SafeMerge -Repo $integrationPath -Ref $sourceBranch -Label "Feature merge from $sourceBranch"
Write-Output 'Local main merge completed. Run validation from the integration worktree before push or deployment.'
