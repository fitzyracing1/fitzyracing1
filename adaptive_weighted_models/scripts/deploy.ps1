param(
    [ValidateSet("local", "artifact", "publish")]
    [string]$Mode = "local",

    [ValidateSet("none", "patch", "minor", "major")]
    [string]$Bump = "none",

    [switch]$SkipTests,
    [switch]$SkipBuild,

    [ValidateSet("pypi", "testpypi", "private")]
    [string]$Registry = "pypi",

    [string]$RepositoryUrl = "",
    [string]$TwineUsername = "",
    [string]$TwinePassword = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

function Get-PythonExecutable {
    $candidates = @(
        "python",
        "py"
    )

    foreach ($candidate in $candidates) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($null -ne $cmd) {
            return $cmd.Source
        }
    }

    $fallback = "C:/Users/$env:USERNAME/AppData/Local/Microsoft/WindowsApps/python3.13.exe"
    if (Test-Path $fallback) {
        return $fallback
    }

    throw "No Python executable found. Install Python 3.10+ and retry."
}

$PythonExe = Get-PythonExecutable
Write-Host "Using Python: $PythonExe"

if ($Bump -ne "none") {
    & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "bump_version.ps1") -Part $Bump
}

if (-not $SkipTests) {
    & $PythonExe -m unittest discover -s tests -p "test_*.py"
}

if (-not $SkipBuild) {
    & $PythonExe -m pip install --upgrade build twine
    & $PythonExe -m build
}

$distDir = Join-Path $RepoRoot "dist"
if (-not (Test-Path $distDir)) {
    throw "dist directory not found. Build step did not produce artifacts."
}

$wheel = Get-ChildItem -Path $distDir -Filter "*.whl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($null -eq $wheel) {
    throw "No wheel found in dist/."
}

switch ($Mode) {
    "local" {
        Write-Host "Installing wheel locally: $($wheel.Name)"
        & $PythonExe -m pip install --force-reinstall $wheel.FullName
    }
    "artifact" {
        Write-Host "Build complete. Artifact ready: $($wheel.FullName)"
    }
    "publish" {
        $twineArgs = @("-m", "twine", "upload")

        if ($Registry -eq "testpypi") {
            $twineArgs += @("--repository-url", "https://test.pypi.org/legacy/")
        }

        if ($Registry -eq "private") {
            if ([string]::IsNullOrWhiteSpace($RepositoryUrl)) {
                throw "RepositoryUrl is required when Registry=private"
            }
            $twineArgs += @("--repository-url", $RepositoryUrl)
        }

        if (-not [string]::IsNullOrWhiteSpace($TwineUsername)) {
            $twineArgs += @("-u", $TwineUsername)
        }
        if (-not [string]::IsNullOrWhiteSpace($TwinePassword)) {
            $twineArgs += @("-p", $TwinePassword)
        }

        $twineArgs += "dist/*"

        Write-Host "Publishing artifacts via Twine..."
        & $PythonExe @twineArgs
    }
}

Write-Host "Deployment flow completed successfully."
