param(
  [string[]]$Root = @(),
  [string[]]$ExtraPath = @(),
  [switch]$IncludeTmpProfiles,
  [switch]$Apply,
  [switch]$Permanent,
  [switch]$ForceActiveProfile,
  [string]$QuarantineRoot = "",
  [int]$OlderThanHours = 0
)

$ErrorActionPreference = "Stop"

function Resolve-ExistingPath {
  param([string]$Path)
  if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
  try {
    return (Resolve-Path -LiteralPath $Path -ErrorAction Stop).ProviderPath
  } catch {
    return $null
  }
}

function Get-PathKind {
  param([string]$Path)
  $item = Get-Item -LiteralPath $Path -Force
  if ($item.PSIsContainer) { return "directory" }
  return "file"
}

function Get-PathSizeBytes {
  param([string]$Path)
  $item = Get-Item -LiteralPath $Path -Force
  if (-not $item.PSIsContainer) { return [int64]$item.Length }
  $sum = (Get-ChildItem -LiteralPath $Path -Force -Recurse -File -ErrorAction SilentlyContinue |
    Measure-Object -Property Length -Sum).Sum
  if ($null -eq $sum) { return 0 }
  return [int64]$sum
}

function Test-ProtectedPath {
  param([string]$Path)
  $normalized = $Path.ToLowerInvariant()
  $parts = $normalized -split '[\\/]'
  if ($parts -contains ".git") { return ".git repository data" }
  if ($parts -contains "node_modules") { return "node_modules dependency directory" }
  if ($parts -contains ".codex" -and $parts -contains "skills") { return "installed Codex skill directory" }
  if ($parts -contains ".agents" -and $parts -contains "skills") { return "installed agent skill directory" }
  foreach ($name in @("src", "app", "pages", "components")) {
    if ($parts -contains $name) { return "source directory segment: $name" }
  }
  $root = [System.IO.Path]::GetPathRoot($Path)
  if ($Path.TrimEnd('\','/') -eq $root.TrimEnd('\','/')) { return "filesystem root" }
  return ""
}

function Test-ChromeProfile {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path -PathType Container)) { return $false }
  $name = Split-Path -Leaf $Path
  $nameLooksLikeProfile = $name -like "chrome-cdp-profile*" -or $name -like "*-chrome-profile"
  $hasMarkers =
    (Test-Path -LiteralPath (Join-Path $Path "Default")) -or
    (Test-Path -LiteralPath (Join-Path $Path "Local State")) -or
    (Test-Path -LiteralPath (Join-Path $Path "Last Version")) -or
    (Test-Path -LiteralPath (Join-Path $Path "DevToolsActivePort"))
  return ($nameLooksLikeProfile -and $hasMarkers)
}

function Get-ActiveProfileReason {
  param([string]$Path)
  $markers = @("DevToolsActivePort", "SingletonLock", "SingletonCookie", "SingletonSocket", "LOCK")
  $present = @()
  foreach ($marker in $markers) {
    $candidate = Join-Path $Path $marker
    if (Test-Path -LiteralPath $candidate) { $present += $marker }
  }
  if ($present.Count -gt 0) { return "profile may be active: " + ($present -join ", ") }
  return ""
}

function New-Candidate {
  param(
    [string]$Path,
    [string]$Reason,
    [string]$Category
  )
  $resolved = Resolve-ExistingPath $Path
  if (-not $resolved) { return $null }
  $protected = Test-ProtectedPath $resolved
  $kind = Get-PathKind $resolved
  $lastWrite = (Get-Item -LiteralPath $resolved -Force).LastWriteTime
  $ageOk = $true
  if ($OlderThanHours -gt 0) {
    $ageOk = $lastWrite -lt (Get-Date).AddHours(-1 * $OlderThanHours)
  }
  $activeReason = ""
  if ($Category -eq "chrome-profile") {
    $activeReason = Get-ActiveProfileReason $resolved
  }
  [PSCustomObject]@{
    Path = $resolved
    Kind = $kind
    Category = $Category
    Reason = $Reason
    SizeMB = [Math]::Round((Get-PathSizeBytes $resolved) / 1MB, 2)
    LastWriteTime = $lastWrite
    ProtectedReason = $protected
    ActiveReason = $activeReason
    Eligible = ($protected -eq "" -and $ageOk -and ($activeReason -eq "" -or $ForceActiveProfile))
  }
}

function Add-Candidate {
  param(
    [System.Collections.Generic.List[object]]$List,
    [string]$Path,
    [string]$Reason,
    [string]$Category
  )
  $candidate = New-Candidate -Path $Path -Reason $Reason -Category $Category
  if ($null -eq $candidate) { return }
  if (-not ($List | Where-Object { $_.Path -eq $candidate.Path })) {
    [void]$List.Add($candidate)
  }
}

if ($Root.Count -eq 0 -and $ExtraPath.Count -eq 0) {
  $Root = @((Get-Location).Path)
}

$candidates = [System.Collections.Generic.List[object]]::new()
$scannedRoots = [System.Collections.Generic.List[string]]::new()

foreach ($rootInput in $Root) {
  $root = Resolve-ExistingPath $rootInput
  if (-not $root) { continue }
  [void]$scannedRoots.Add($root)

  $artifactDir = Join-Path $root "artifacts"
  if (Test-Path -LiteralPath $artifactDir -PathType Container) {
    foreach ($pattern in @("page-full*.png", "*page-full*.png", "*full-page*.png", "*pixel-reference*.png", "*figma*screenshot*.png")) {
      Get-ChildItem -LiteralPath $artifactDir -Force -File -Recurse -Filter $pattern -ErrorAction SilentlyContinue |
        ForEach-Object {
          Add-Candidate $candidates $_.FullName "Figma page screenshot/reference under artifacts" "screenshot"
        }
    }
  }

  Get-ChildItem -LiteralPath $root -Force -Directory -Recurse -ErrorAction SilentlyContinue |
    Where-Object { Test-ChromeProfile $_.FullName } |
    ForEach-Object {
      Add-Candidate $candidates $_.FullName "Chrome/CDP profile produced by page capture" "chrome-profile"
    }
}

if ($IncludeTmpProfiles -and (Test-Path -LiteralPath "C:\tmp" -PathType Container)) {
  [void]$scannedRoots.Add("C:\tmp")
  Get-ChildItem -LiteralPath "C:\tmp" -Force -Directory -ErrorAction SilentlyContinue |
    Where-Object { Test-ChromeProfile $_.FullName } |
    ForEach-Object {
      Add-Candidate $candidates $_.FullName "Chrome profile under C:\tmp" "chrome-profile"
    }
}

foreach ($path in $ExtraPath) {
  Add-Candidate $candidates $path "Explicit user-approved path" "explicit"
}

$ordered = $candidates | Sort-Object Category, Path

$summary = [PSCustomObject]@{
  mode = $(if ($Apply) { if ($Permanent) { "permanent-delete" } else { "quarantine" } } else { "dry-run" })
  scannedRoots = @($scannedRoots | Select-Object -Unique)
  candidateCount = @($ordered).Count
  eligibleCount = @($ordered | Where-Object { $_.Eligible }).Count
  totalCandidateMB = [Math]::Round((($ordered | Measure-Object -Property SizeMB -Sum).Sum), 2)
}

Write-Output "Summary:"
$summary | ConvertTo-Json -Depth 4
Write-Output ""
Write-Output "Candidates:"
$ordered | Select-Object Eligible,Category,Kind,SizeMB,LastWriteTime,Path,Reason,ProtectedReason,ActiveReason | Format-Table -AutoSize

if (-not $Apply) {
  Write-Output ""
  Write-Output "Dry run only. Re-run with -Apply after user confirmation."
  exit 0
}

$eligible = @($ordered | Where-Object { $_.Eligible })
if ($eligible.Count -eq 0) {
  Write-Output ""
  Write-Output "No eligible candidates to clean."
  exit 0
}

if ([string]::IsNullOrWhiteSpace($QuarantineRoot)) {
  $QuarantineRoot = Join-Path $env:TEMP "figma-page-artifact-cleaner"
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$quarantineDir = Join-Path $QuarantineRoot "quarantine-$stamp"
if (-not $Permanent) {
  New-Item -ItemType Directory -Force -Path $quarantineDir | Out-Null
}

$results = [System.Collections.Generic.List[object]]::new()
foreach ($item in $eligible) {
  try {
    if ($Permanent) {
      Remove-Item -LiteralPath $item.Path -Force -Recurse
      [void]$results.Add([PSCustomObject]@{ Path = $item.Path; Action = "deleted"; Target = "" })
    } else {
      $safeName = ($item.Path -replace '^[A-Za-z]:', '') -replace '[\\/:*?"<>|]', '_'
      $target = Join-Path $quarantineDir $safeName
      Move-Item -LiteralPath $item.Path -Destination $target -Force
      [void]$results.Add([PSCustomObject]@{ Path = $item.Path; Action = "moved-to-quarantine"; Target = $target })
    }
  } catch {
    [void]$results.Add([PSCustomObject]@{ Path = $item.Path; Action = "failed"; Target = $_.Exception.Message })
  }
}

Write-Output ""
Write-Output "Cleanup results:"
$results | Format-Table -AutoSize
if (-not $Permanent) {
  Write-Output ""
  Write-Output "Quarantine: $quarantineDir"
}
