# Script per fermare tutti i servizi RAG
# Uso: .\stop.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RAG Application - Stop All Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Funzione per fermare un processo su una porta
function Stop-ProcessOnPort {
    param([int]$Port, [string]$ServiceName)
    $process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    if ($process) {
        Write-Host "  [STOP] Fermando $ServiceName (PID: $process)..." -ForegroundColor Yellow
        Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] $ServiceName fermato" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  [SKIP] $ServiceName non è in esecuzione" -ForegroundColor Gray
        return $false
    }
}

# Ferma FastAPI
Write-Host "[STEP 1] Fermo FastAPI server..." -ForegroundColor Cyan
Stop-ProcessOnPort -Port 8000 -ServiceName "FastAPI"
Write-Host ""

# Ferma React Frontend
Write-Host "[STEP 2] Fermo React frontend..." -ForegroundColor Cyan
Stop-ProcessOnPort -Port 3000 -ServiceName "React Frontend"
Write-Host ""

# Ferma Inngest
Write-Host "[STEP 3] Fermo Inngest dev server..." -ForegroundColor Cyan
Stop-ProcessOnPort -Port 8288 -ServiceName "Inngest"
Write-Host ""

# Ferma Qdrant
Write-Host "[STEP 4] Fermo Qdrant container..." -ForegroundColor Cyan
$qdrantRunning = docker ps --filter "name=qdrant" --format "{{.Names}}" 2>&1
if ($qdrantRunning -like "*qdrant*") {
    Write-Host "  [STOP] Fermando Qdrant container..." -ForegroundColor Yellow
    docker stop qdrant | Out-Null
    Write-Host "  [OK] Qdrant container fermato" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] Qdrant container non è in esecuzione" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Tutti i servizi sono stati fermati" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

