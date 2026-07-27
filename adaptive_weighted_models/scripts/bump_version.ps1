param(
    [ValidateSet("patch", "minor", "major")]
    [string]$Part = "patch",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Pyproject = Join-Path $RepoRoot "pyproject.toml"

if (-not (Test-Path $Pyproject)) {
    throw "pyproject.toml not found at $Pyproject"
}

$content = Get-Content -Path $Pyproject -Raw
$match = [regex]::Match($content, 'version\s*=\s*"(?<v>\d+\.\d+\.\d+)"')
if (-not $match.Success) {
    throw "Unable to locate semantic version in pyproject.toml"
}

$current = $match.Groups["v"].Value
$parts = $current.Split('.') | ForEach-Object { [int]$_ }

switch ($Part) {
    "patch" { $parts[2] += 1 }
    "minor" { $parts[1] += 1; $parts[2] = 0 }
    "major" { $parts[0] += 1; $parts[1] = 0; $parts[2] = 0 }
}

$newVersion = "$($parts[0]).$($parts[1]).$($parts[2])"
$newContent = [regex]::Replace($content, 'version\s*=\s*"\d+\.\d+\.\d+"', "version = `"$newVersion`"", 1)

Write-Host "Current version: $current"
Write-Host "Next version:    $newVersion"

if ($DryRun) {
    Write-Host "Dry run only; no files were changed."
    exit 0
}

Set-Content -Path $Pyproject -Value $newContent -NoNewline
Write-Host "Updated pyproject.toml to version $newVersion"
