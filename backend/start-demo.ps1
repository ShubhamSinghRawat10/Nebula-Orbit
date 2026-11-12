$ErrorActionPreference = "Stop"
$port = if ($env:PORT) { [int]$env:PORT } else { 5000 }
$listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    Write-Error "Port $port is already served by PID $($listener.OwningProcess). Stop that Nebula process first (Ctrl+C in its terminal), then run this script again. This check avoids silently using an older backend process."
}

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Nebula Python environment was not found at $python. Create it and install backend requirements first."
}

Set-Location -LiteralPath $PSScriptRoot
$env:NEBULA_DEMO_MODE = "true"
$env:FLASK_DEBUG = "false"
$deps = Join-Path $PSScriptRoot ".deps"
$env:PYTHONPATH = if ($env:PYTHONPATH) { "$deps;$env:PYTHONPATH" } else { $deps }
Write-Host "Starting Nebula demo at http://127.0.0.1:$port (Ctrl+C stops this server)."
& $python app.py
