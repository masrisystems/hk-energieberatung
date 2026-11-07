[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [ValidateSet('Audit', 'Apply')]
    [string]$Action = 'Audit',

    [string]$PlanPath,

    [string]$ConfirmPlanId,

    [string[]]$PreserveProcessName = @(),

    [ValidateRange(1, 240)]
    [int]$PlanMaxAgeMinutes = 30,

    [ValidateRange(1, 120)]
    [int]$GracePeriodSeconds = 20
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not ([System.Management.Automation.PSTypeName]'OvernightDesktopHelper').Type) {
    Add-Type @'
using System;
using System.Diagnostics;
using System.Collections.Generic;
using System.Runtime.InteropServices;

public class OvernightDesktopHelper {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern IntPtr OpenDesktop(string lpszDesktop, uint dwFlags, bool fInherit, uint dwDesiredAccess);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetThreadDesktop(IntPtr hDesktop);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool CloseDesktop(IntPtr hDesktop);

    public class ProcWinInfo {
        public int Id { get; set; }
        public string Title { get; set; }
        public long Handle { get; set; }
    }

    public static List<ProcWinInfo> GetDesktopProcessesWithWindows() {
        var list = new List<ProcWinInfo>();
        var t = new System.Threading.Thread(() => {
            IntPtr hDesk = OpenDesktop("default", 0, false, 0x01FF);
            if (hDesk != IntPtr.Zero) {
                SetThreadDesktop(hDesk);
            }
            try {
                foreach (var p in Process.GetProcesses()) {
                    try {
                        if (p.MainWindowHandle != IntPtr.Zero && !string.IsNullOrWhiteSpace(p.MainWindowTitle)) {
                            list.Add(new ProcWinInfo {
                                Id = p.Id,
                                Title = p.MainWindowTitle,
                                Handle = p.MainWindowHandle.ToInt64()
                            });
                        }
                    } catch {}
                }
            } finally {
                if (hDesk != IntPtr.Zero) {
                    CloseDesktop(hDesk);
                }
            }
        });
        t.SetApartmentState(System.Threading.ApartmentState.STA);
        t.Start();
        t.Join();
        return list;
    }

    public static bool ProcessHasWindowOnDefaultDesktop(int processId) {
        bool hasWindow = false;
        var t = new System.Threading.Thread(() => {
            IntPtr hDesk = OpenDesktop("default", 0, false, 0x01FF);
            if (hDesk != IntPtr.Zero) {
                SetThreadDesktop(hDesk);
            }
            try {
                var p = Process.GetProcessById(processId);
                hasWindow = (p.MainWindowHandle != IntPtr.Zero && !string.IsNullOrWhiteSpace(p.MainWindowTitle));
            } catch {}
            finally {
                if (hDesk != IntPtr.Zero) {
                    CloseDesktop(hDesk);
                }
            }
        });
        t.SetApartmentState(System.Threading.ApartmentState.STA);
        t.Start();
        t.Join();
        return hasWindow;
    }

    public static bool CloseProcessMainWindow(int processId) {
        bool result = false;
        var t = new System.Threading.Thread(() => {
            IntPtr hDesk = OpenDesktop("default", 0, false, 0x01FF);
            if (hDesk != IntPtr.Zero) {
                SetThreadDesktop(hDesk);
            }
            try {
                var p = Process.GetProcessById(processId);
                result = p.CloseMainWindow();
            } catch {}
            finally {
                if (hDesk != IntPtr.Zero) {
                    CloseDesktop(hDesk);
                }
            }
        });
        t.SetApartmentState(System.Threading.ApartmentState.STA);
        t.Start();
        t.Join();
        return result;
    }
}
'@
}

function Get-NormalizedProcessName {
    param([AllowNull()][string]$Name)

    if ([string]::IsNullOrWhiteSpace($Name)) {
        return ''
    }

    return [System.IO.Path]::GetFileNameWithoutExtension($Name).ToLowerInvariant()
}

function Get-ProcessCreationUtc {
    param([Parameter(Mandatory)]$CimProcess)

    $created = [datetime]$CimProcess.CreationDate
    return $created.ToUniversalTime().ToString('o')
}

function Get-Sha256Text {
    param([AllowNull()][string]$Text)

    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes([string]$Text)
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

function Get-ProcessIdentityHash {
    param([Parameter(Mandatory)]$CimProcess)

    $identity = @(
        [string]$CimProcess.ProcessId
        (Get-NormalizedProcessName -Name $CimProcess.Name)
        (Get-ProcessCreationUtc -CimProcess $CimProcess)
        [string]$CimProcess.ExecutablePath
        [string]$CimProcess.CommandLine
    ) -join "`n"

    return Get-Sha256Text -Text $identity
}

function Get-OvernightInventory {
    param([string[]]$AdditionalPreserveNames = @())

    $cimProcesses = @(Get-CimInstance Win32_Process -ErrorAction Stop | Select-Object ProcessId, ParentProcessId, Name, ExecutablePath, CommandLine, CreationDate, SessionId)
    $cimById = @{}
    $childrenByParent = @{}

    foreach ($process in $cimProcesses) {
        $processId = [int]$process.ProcessId
        $parentId = [int]$process.ParentProcessId
        $cimById[$processId] = $process
        if (-not $childrenByParent.ContainsKey($parentId)) {
            $childrenByParent[$parentId] = [System.Collections.Generic.List[int]]::new()
        }
        $childrenByParent[$parentId].Add($processId)
    }

    $windowById = @{}
    foreach ($process in Get-Process -ErrorAction SilentlyContinue) {
        try {
            if ($process.MainWindowHandle -ne 0 -and -not [string]::IsNullOrWhiteSpace($process.MainWindowTitle)) {
                $windowById[[int]$process.Id] = [pscustomobject]@{
                    Title = [string]$process.MainWindowTitle
                    Handle = [int64]$process.MainWindowHandle
                }
            }
        } catch {
            # A process can exit or deny access between enumeration and inspection.
        }
    }

    if ($windowById.Count -eq 0) {
        try {
            $deskWindows = [OvernightDesktopHelper]::GetDesktopProcessesWithWindows()
            foreach ($item in $deskWindows) {
                $windowById[[int]$item.Id] = [pscustomobject]@{
                    Title = [string]$item.Title
                    Handle = [int64]$item.Handle
                }
            }
        } catch {
            # Fallback not available; continue
        }
    }

    $protected = @{}
    function Add-Protection {
        param([int]$ProcessId, [string]$Reason)

        if (-not $protected.ContainsKey($ProcessId)) {
            $protected[$ProcessId] = [System.Collections.Generic.List[string]]::new()
        }
        if (-not $protected[$ProcessId].Contains($Reason)) {
            $protected[$ProcessId].Add($Reason)
        }
    }

    $systemNames = @(
        'idle', 'system', 'secure system', 'registry', 'memory compression',
        'smss', 'csrss', 'wininit', 'services', 'lsaiso', 'lsass', 'winlogon',
        'fontdrvhost', 'dwm', 'svchost', 'wudfhost', 'spoolsv', 'msmpeng',
        'nissrv', 'securityhealthservice', 'securityhealthsystray', 'searchindexer',
        'taskhostw', 'sihost', 'ctfmon', 'explorer', 'shellexperiencehost',
        'startmenuexperiencehost', 'searchhost', 'runtimebroker',
        'applicationframehost', 'systemsettings', 'textinputhost', 'lockapp', 'widgets',
        'widgetservice', 'dllhost', 'conhost', 'audiodg'
    )
    $systemNameSet = @{}
    foreach ($name in $systemNames) {
        $systemNameSet[$name] = $true
    }

    foreach ($process in $cimProcesses) {
        $normalizedName = Get-NormalizedProcessName -Name $process.Name
        if ([int]$process.SessionId -eq 0 -or $systemNameSet.ContainsKey($normalizedName)) {
            Add-Protection -ProcessId ([int]$process.ProcessId) -Reason 'Windows system, service, security, or shell process'
        }
    }

    $currentId = [int]$PID
    while ($currentId -gt 0 -and $cimById.ContainsKey($currentId)) {
        Add-Protection -ProcessId $currentId -Reason 'Invoking AI or PowerShell process chain'
        $nextId = [int]$cimById[$currentId].ParentProcessId
        if ($nextId -eq $currentId) {
            break
        }
        $currentId = $nextId
    }

    $scheduleMarker = '(?i)(antigravity|[\\/]\.gemini[\\/](?:antigravity|config[\\/]sidecars)|language_server(?:\.exe)?|multicall\s+schedule|agentapi(?:\.exe)?\s+new-conversation|sidecar_data)'
    $treeRoots = [System.Collections.Generic.List[int]]::new()

    foreach ($process in $cimProcesses) {
        $identityText = @([string]$process.Name, [string]$process.ExecutablePath, [string]$process.CommandLine) -join "`n"
        if ($identityText -match $scheduleMarker) {
            $processId = [int]$process.ProcessId
            Add-Protection -ProcessId $processId -Reason 'Antigravity or scheduled sidecar marker'
            $treeRoots.Add($processId)

            $ancestorId = [int]$process.ParentProcessId
            while ($ancestorId -gt 0 -and $cimById.ContainsKey($ancestorId)) {
                Add-Protection -ProcessId $ancestorId -Reason 'Ancestor of Antigravity or scheduled sidecar process'
                $nextId = [int]$cimById[$ancestorId].ParentProcessId
                if ($nextId -eq $ancestorId) {
                    break
                }
                $ancestorId = $nextId
            }
        }
    }

    $preserveNameSet = @{}
    foreach ($name in $AdditionalPreserveNames) {
        $normalized = Get-NormalizedProcessName -Name $name
        if (-not [string]::IsNullOrWhiteSpace($normalized)) {
            $preserveNameSet[$normalized] = $true
        }
    }

    foreach ($process in $cimProcesses) {
        $normalizedName = Get-NormalizedProcessName -Name $process.Name
        if ($preserveNameSet.ContainsKey($normalizedName)) {
            $processId = [int]$process.ProcessId
            Add-Protection -ProcessId $processId -Reason 'User-specified preserved process name'
            $treeRoots.Add($processId)
        }
    }

    $queue = [System.Collections.Generic.Queue[int]]::new()
    foreach ($rootId in $treeRoots) {
        $queue.Enqueue($rootId)
    }
    $visited = @{}
    while ($queue.Count -gt 0) {
        $parentId = $queue.Dequeue()
        if ($visited.ContainsKey($parentId)) {
            continue
        }
        $visited[$parentId] = $true
        if (-not $childrenByParent.ContainsKey($parentId)) {
            continue
        }
        foreach ($childId in $childrenByParent[$parentId]) {
            Add-Protection -ProcessId $childId -Reason 'Descendant of a protected scheduler or user-preserved process'
            $queue.Enqueue($childId)
        }
    }

    $currentSessionId = [int](Get-Process -Id $PID -ErrorAction Stop).SessionId
    $candidates = [System.Collections.Generic.List[object]]::new()
    $protectedRows = [System.Collections.Generic.List[object]]::new()
    $backgroundRows = [System.Collections.Generic.List[object]]::new()

    foreach ($process in $cimProcesses | Sort-Object Name, ProcessId) {
        $processId = [int]$process.ProcessId
        $row = [pscustomobject]@{
            ProcessId = $processId
            Name = Get-NormalizedProcessName -Name $process.Name
            Title = if ($windowById.ContainsKey($processId)) { [string]$windowById[$processId].Title } else { '' }
            ExecutablePath = [string]$process.ExecutablePath
            CreatedUtc = Get-ProcessCreationUtc -CimProcess $process
            IdentityHash = Get-ProcessIdentityHash -CimProcess $process
        }

        if ($protected.ContainsKey($processId)) {
            $protectedRows.Add([pscustomobject]@{
                ProcessId = $row.ProcessId
                Name = $row.Name
                Title = $row.Title
                Reasons = @($protected[$processId])
                IdentityHash = $row.IdentityHash
            })
        } elseif ([int]$process.SessionId -eq $currentSessionId -and $windowById.ContainsKey($processId)) {
            $candidates.Add($row)
        } else {
            $backgroundRows.Add([pscustomobject]@{
                ProcessId = $row.ProcessId
                Name = $row.Name
                Classification = 'Preserved: no closeable top-level window or not in the invoking interactive session'
            })
        }
    }

    return [pscustomobject]@{
        CurrentSessionId = $currentSessionId
        Candidates = @($candidates)
        Protected = @($protectedRows)
        BackgroundPreserved = @($backgroundRows)
        ProtectedProcessIds = @($protected.Keys | ForEach-Object { [int]$_ })
        AllProcessIdentities = @($cimProcesses | ForEach-Object {
            [pscustomobject]@{
                ProcessId = [int]$_.ProcessId
                IdentityHash = Get-ProcessIdentityHash -CimProcess $_
            }
        })
    }
}

function Write-AuditSummary {
    param([Parameter(Mandatory)]$Plan)

    Write-Output ''
    Write-Output 'Candidate windows (eligible for a graceful close after confirmation):'
    if (@($Plan.Candidates).Count -eq 0) {
        Write-Output '  None'
    } else {
        $Plan.Candidates | Select-Object ProcessId, Name, Title | Format-Table -AutoSize
    }

    Write-Output "Protected processes: $(@($Plan.Protected).Count)"
    $importantProtected = @($Plan.Protected | Where-Object {
        (@($_.Reasons) -join ' ') -match 'Antigravity|sidecar|Invoking AI|user-specified'
    })
    if ($importantProtected.Count -gt 0) {
        $importantProtected | Select-Object ProcessId, Name, Title, @{Name='Reason';Expression={ @($_.Reasons) -join '; ' }} | Format-Table -AutoSize
    }

    Write-Output "Background or uncertain processes preserved: $(@($Plan.BackgroundPreserved).Count)"
    Write-Output "Plan ID: $($Plan.PlanId)"
    Write-Output "Plan path: $($Plan.PlanPath)"
    Write-Output 'No process has been closed. Apply requires this exact plan ID.'
}

if ($Action -eq 'Audit') {
    $inventory = Get-OvernightInventory -AdditionalPreserveNames $PreserveProcessName
    $localAppData = [Environment]::GetFolderPath('LocalApplicationData')
    if ([string]::IsNullOrWhiteSpace($localAppData)) {
        throw 'Could not resolve the current user LocalApplicationData folder.'
    }

    $reportRoot = Join-Path $localAppData 'MasriSystems\OvernightServerMode\reports'
    [System.IO.Directory]::CreateDirectory($reportRoot) | Out-Null
    $createdUtc = [datetime]::UtcNow
    $planId = [guid]::NewGuid().ToString()
    $resolvedPlanPath = Join-Path $reportRoot ("plan-{0}-{1}.json" -f $createdUtc.ToString('yyyyMMdd-HHmmss'), $planId)

    $plan = [pscustomobject]@{
        SchemaVersion = 1
        PlanId = $planId
        CreatedUtc = $createdUtc.ToString('o')
        ExpiresUtc = $createdUtc.AddMinutes($PlanMaxAgeMinutes).ToString('o')
        ComputerName = [Environment]::MachineName
        UserName = [Environment]::UserName
        CurrentSessionId = $inventory.CurrentSessionId
        PreserveProcessName = @($PreserveProcessName)
        Candidates = @($inventory.Candidates)
        Protected = @($inventory.Protected)
        BackgroundPreserved = @($inventory.BackgroundPreserved)
        PlanPath = $resolvedPlanPath
        Safety = [pscustomobject]@{
            Method = 'CloseMainWindow only'
            ForceTerminationAvailable = $false
            ServicesOrScheduledTasksChanged = $false
        }
    }

    $json = $plan | ConvertTo-Json -Depth 8
    [System.IO.File]::WriteAllText($resolvedPlanPath, $json, [System.Text.UTF8Encoding]::new($false))
    Write-AuditSummary -Plan $plan
    exit 0
}

if ([string]::IsNullOrWhiteSpace($PlanPath)) {
    throw '-PlanPath is required for Apply.'
}
if ([string]::IsNullOrWhiteSpace($ConfirmPlanId)) {
    throw '-ConfirmPlanId is required for Apply.'
}

$resolvedInputPlanPath = (Resolve-Path -LiteralPath $PlanPath -ErrorAction Stop).Path
$plan = Get-Content -LiteralPath $resolvedInputPlanPath -Raw | ConvertFrom-Json
if ([int]$plan.SchemaVersion -ne 1) {
    throw "Unsupported plan schema version: $($plan.SchemaVersion)"
}
if ([string]$plan.PlanId -cne $ConfirmPlanId) {
    throw 'The confirmation plan ID does not exactly match the saved plan.'
}
if ([string]$plan.ComputerName -cne [Environment]::MachineName -or [string]$plan.UserName -cne [Environment]::UserName) {
    throw 'The plan belongs to a different computer or user.'
}
if ([datetime]::UtcNow -gt [datetime]$plan.ExpiresUtc) {
    throw 'The plan has expired. Generate and review a fresh audit plan.'
}

$freshInventory = Get-OvernightInventory -AdditionalPreserveNames @($plan.PreserveProcessName)
$freshProtectedIds = @{}
foreach ($protectedId in $freshInventory.ProtectedProcessIds) {
    $freshProtectedIds[[int]$protectedId] = $true
}
$freshIdentityById = @{}
foreach ($identity in $freshInventory.AllProcessIdentities) {
    $freshIdentityById[[int]$identity.ProcessId] = [string]$identity.IdentityHash
}

$results = [System.Collections.Generic.List[object]]::new()
foreach ($target in @($plan.Candidates)) {
    $processId = [int]$target.ProcessId
    $result = [ordered]@{
        ProcessId = $processId
        Name = [string]$target.Name
        Title = [string]$target.Title
        Status = ''
        Detail = ''
    }

    if (-not $freshIdentityById.ContainsKey($processId)) {
        $result.Status = 'AlreadyExited'
        $result.Detail = 'The planned PID no longer exists.'
        $results.Add([pscustomobject]$result)
        continue
    }

    if ($freshIdentityById[$processId] -cne [string]$target.IdentityHash) {
        $result.Status = 'IdentityChanged'
        $result.Detail = 'PID identity, start time, executable path, or command line changed; left running.'
        $results.Add([pscustomobject]$result)
        continue
    }

    if ($freshProtectedIds.ContainsKey($processId)) {
        $result.Status = 'NowProtected'
        $result.Detail = 'Fresh protection rules classify this PID as protected; left running.'
        $results.Add([pscustomobject]$result)
        continue
    }

    $currentProcess = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($null -eq $currentProcess) {
        $result.Status = 'AlreadyExited'
        $result.Detail = 'The process exited during revalidation.'
        $results.Add([pscustomobject]$result)
        continue
    }
    $hasWindow = ($currentProcess.MainWindowHandle -ne 0 -and -not [string]::IsNullOrWhiteSpace($currentProcess.MainWindowTitle))
    if (-not $hasWindow) {
        $hasWindow = [OvernightDesktopHelper]::ProcessHasWindowOnDefaultDesktop($processId)
    }

    if (-not $hasWindow) {
        $result.Status = 'NoCloseableWindow'
        $result.Detail = 'No visible top-level window remains; left running.'
        $results.Add([pscustomobject]$result)
        continue
    }

    if (-not $PSCmdlet.ShouldProcess("PID $processId ($($target.Name)) - $($target.Title)", 'Request graceful window close')) {
        $result.Status = 'WhatIf'
        $result.Detail = 'No close request was sent.'
        $results.Add([pscustomobject]$result)
        continue
    }

    $accepted = $false
    if ($currentProcess.MainWindowHandle -ne 0) {
        $accepted = $currentProcess.CloseMainWindow()
    } else {
        $accepted = [OvernightDesktopHelper]::CloseProcessMainWindow($processId)
    }
    if (-not $accepted) {
        $result.Status = 'CloseNotAccepted'
        $result.Detail = 'The application did not accept a normal window-close request; left running.'
        $results.Add([pscustomobject]$result)
        continue
    }

    if ($currentProcess.WaitForExit($GracePeriodSeconds * 1000)) {
        $result.Status = 'Closed'
        $result.Detail = 'The process exited after a normal window-close request.'
    } else {
        $result.Status = 'StillRunning'
        $result.Detail = 'The application may be showing an unsaved-work prompt or refused to exit; no force action was taken.'
    }
    $results.Add([pscustomobject]$result)
}

$postInventory = Get-OvernightInventory -AdditionalPreserveNames @($plan.PreserveProcessName)
$postIdentityById = @{}
foreach ($identity in $postInventory.AllProcessIdentities) {
    $postIdentityById[[int]$identity.ProcessId] = [string]$identity.IdentityHash
}

$protectedChecks = [System.Collections.Generic.List[object]]::new()
foreach ($protectedProcess in @($plan.Protected)) {
    $processId = [int]$protectedProcess.ProcessId
    $status = if (-not $postIdentityById.ContainsKey($processId)) {
        'ExitedOrReplaced'
    } elseif ($postIdentityById[$processId] -ceq [string]$protectedProcess.IdentityHash) {
        'AliveSameIdentity'
    } else {
        'PidReusedOrIdentityChanged'
    }
    $protectedChecks.Add([pscustomobject]@{
        ProcessId = $processId
        Name = [string]$protectedProcess.Name
        Status = $status
        Reasons = @($protectedProcess.Reasons)
    })
}

$completedUtc = [datetime]::UtcNow
$resultPath = Join-Path (Split-Path -Parent $resolvedInputPlanPath) ("result-{0}-{1}.json" -f $completedUtc.ToString('yyyyMMdd-HHmmss'), $plan.PlanId)
$resultDocument = [pscustomobject]@{
    SchemaVersion = 1
    PlanId = [string]$plan.PlanId
    CompletedUtc = $completedUtc.ToString('o')
    Results = @($results)
    ProtectedProcessChecks = @($protectedChecks)
    Safety = [pscustomobject]@{
        Method = 'CloseMainWindow only'
        ForceTerminationUsed = $false
        ServicesOrScheduledTasksChanged = $false
    }
}
[System.IO.File]::WriteAllText($resultPath, ($resultDocument | ConvertTo-Json -Depth 8), [System.Text.UTF8Encoding]::new($false))

Write-Output ''
Write-Output 'Graceful-close results:'
$results | Format-Table ProcessId, Name, Status, Detail -AutoSize
Write-Output "Protected processes with the same identity: $(@($protectedChecks | Where-Object Status -eq 'AliveSameIdentity').Count) / $(@($protectedChecks).Count)"
Write-Output "Result path: $resultPath"
Write-Output 'No force termination, service change, scheduled-task change, sleep change, or power-plan change was performed.'
