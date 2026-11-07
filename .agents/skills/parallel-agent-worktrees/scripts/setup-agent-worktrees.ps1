[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$Repository,

    [ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9._-]*$')]
    [string]$Task = 'workspace',

    [string]$DestinationRoot,

    [string]$BaseRef = 'HEAD',

    [ValidateSet('codex', 'gemini', 'claude')]
    [string[]]$Agents = @('codex', 'gemini', 'claude'),

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
        throw "git $($Arguments -join ' ') failed:`n$($output -join "`n")"
    }

    return @($output)
}

$repositoryPath = (Resolve-Path -LiteralPath $Repository).Path
$gitRoot = [string](Invoke-Git -Repo $repositoryPath -Arguments @('rev-parse', '--show-toplevel') | Select-Object -First 1)
$gitRoot = $gitRoot.Trim()
$repositoryPath = [System.IO.Path]::GetFullPath($gitRoot)
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

$baseCommit = [string](Invoke-Git -Repo $repositoryPath -Arguments @('rev-parse', '--verify', "$BaseRef^{commit}") | Select-Object -First 1)
$baseCommit = $baseCommit.Trim()
$status = @(Invoke-Git -Repo $repositoryPath -Arguments @('status', '--short', '--branch') | Where-Object { $_ -notlike 'warning:*' })
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

$mode = if ($Apply) { 'APPLY' } else { 'PREVIEW' }
Write-Output "Parallel agent worktrees: $mode"
Write-Output "Repository: $repositoryPath"
Write-Output "Base: $BaseRef -> $baseCommit"
Write-Output "Destination root: $destinationRootPath"
Write-Output 'Current status:'
$status | ForEach-Object { Write-Output "  $_" }

if ($status | Where-Object { $_ -notlike '##*' }) {
    Write-Warning 'Uncommitted and untracked files remain in the source checkout and will not be copied.'
}

foreach ($agent in $Agents) {
    $branch = "$agent/$Task"
    $destination = if ($registeredByAgent.ContainsKey($agent.ToLowerInvariant())) {
        $registeredByAgent[$agent.ToLowerInvariant()]
    } else {
        [System.IO.Path]::GetFullPath((Join-Path $destinationRootPath $agent))
    }
    $destinationKey = $destination.ToLowerInvariant()
    & git -C $repositoryPath show-ref --verify --quiet "refs/heads/$branch"
    $branchExists = $LASTEXITCODE -eq 0

    if ($registered.ContainsKey($destinationKey)) {
        $currentBranch = [string](Invoke-Git -Repo $destination -Arguments @('branch', '--show-current') | Select-Object -First 1)
        $currentBranch = $currentBranch.Trim()
        if ($currentBranch -eq $branch) {
            Write-Output "  EXISTS $agent -> $destination [$branch]"
            continue
        }
        if ($currentBranch -like "$agent/*") {
            Write-Output "  ACTIVE $agent -> $destination [$currentBranch]"
            continue
        }
        throw "Registered $agent worktree $destination uses '$currentBranch', which is outside the '$agent/*' branch namespace."
    }

    if (Test-Path -LiteralPath $destination) {
        throw "Destination exists but is not the expected registered worktree: $destination"
    }

    $operation = if ($branchExists) { 'attach existing branch' } else { 'create branch and worktree' }
    Write-Output "  PLAN $agent -> $destination [$branch] ($operation)"

    if (-not $Apply) {
        continue
    }

    [System.IO.Directory]::CreateDirectory($destinationRootPath) | Out-Null
    if ($branchExists) {
        Invoke-Git -Repo $repositoryPath -Arguments @('worktree', 'add', $destination, $branch) | ForEach-Object { Write-Output "    $_" }
    } else {
        Invoke-Git -Repo $repositoryPath -Arguments @('worktree', 'add', '-b', $branch, $destination, $baseCommit) | ForEach-Object { Write-Output "    $_" }
    }
}

if (-not $Apply) {
    Write-Output 'No changes made. Re-run with -Apply to create the planned worktrees.'
}
