# Launch the robot. Ensures the bridge is up, removes any STOP file, starts agent in background.
$ErrorActionPreference = "Stop"

$bridgeProc = Get-Process python* -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -and (Get-Process -Id $_.Id).MainModule.FileName -ne $null }

try {
    $health = Invoke-RestMethod -Uri http://127.0.0.1:17777/health -TimeoutSec 3
} catch { $health = $null }

if (-not $health -or -not $health.ok) {
    Write-Host "Bridge not running; starting..."
    Start-Process -FilePath "python" -ArgumentList "C:\Users\EC\ai-browser\bridge.py" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

if (Test-Path C:\Users\EC\robot\STOP) {
    Remove-Item C:\Users\EC\robot\STOP
    Write-Host "Cleared old STOP file."
}

Write-Host "Starting robot agent (logs at C:\Users\EC\robot\agent.log)..."
$p = Start-Process -FilePath "python" -ArgumentList "C:\Users\EC\robot\agent.py" `
    -WorkingDirectory "C:\Users\EC\robot" -WindowStyle Hidden -PassThru
Write-Host "Robot PID: $($p.Id)"
Write-Host ""
Write-Host "To stop:    New-Item C:\Users\EC\robot\STOP"
Write-Host "To tail:    Get-Content C:\Users\EC\robot\agent.log -Wait -Tail 20"
