# Resume Tailor Pro - PowerShell Startup Script
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   RESUME TAILOR PRO - Local AI ATS Resume Engine" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Refresh PATH for current session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify Python
try {
    $pyVer = python --version 2>&1
    Write-Host "[OK] $pyVer detected" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found in PATH." -ForegroundColor Red
    exit 1
}

# Verify pdflatex
try {
    $texCheck = pdflatex --version 2>&1 | Select-Object -First 1
    Write-Host "[OK] LaTeX Engine detected: $texCheck" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] pdflatex not found." -ForegroundColor Red
    exit 1
}

# Check API Key
if (-not $env:GEMINI_API_KEY -and -not $env:GOOGLE_API_KEY) {
    Write-Host "[INFO] GEMINI_API_KEY is not set in environment." -ForegroundColor Yellow
    Write-Host "       (You can paste it directly in the web UI or use the Smart ATS engine)" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Gemini API key configured!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Web Server..." -ForegroundColor Cyan
try {
    $s = New-Object System.Net.Sockets.UdpClient
    $s.Connect("8.8.8.8", 80)
    $lanIp = $s.Client.LocalEndPoint.Address.ToString()
    $s.Close()
    Write-Host "  PC Local:    http://127.0.0.1:5000" -ForegroundColor Green
    Write-Host "  iPhone / LAN: http://${lanIp}:5000  (Open in Safari on same Wi-Fi)" -ForegroundColor Yellow
} catch {
    Write-Host "  PC Local:    http://127.0.0.1:5000" -ForegroundColor Green
}
Write-Host ""

Set-Location -Path $PSScriptRoot
python app.py
