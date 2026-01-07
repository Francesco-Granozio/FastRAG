# Script unico per avviare/riavviare tutti i servizi RAG
# Uso: .\start.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RAG Application - Start/Restart All" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Funzione per verificare se un processo è attivo su una porta
function Test-Port {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $null -ne $connection
}

# Funzione per fermare un processo su una porta
function Stop-ProcessOnPort {
    param([int]$Port, [string]$ServiceName)
    $process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    if ($process) {
        Write-Host "  [STOP] Fermando $ServiceName (PID: $process)..." -ForegroundColor Yellow
        Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        return $true
    }
    return $false
}

# Funzione per avviare un processo in una nuova finestra
function Start-Service {
    param([string]$ServiceName, [string]$Command, [int]$Port, [string]$Url, [int]$WaitSeconds = 5)
    
    if (Test-Port -Port $Port) {
        Write-Host "  [SKIP] $ServiceName è già attivo sulla porta $Port" -ForegroundColor Green
        return $true
    }
    
    Write-Host "  [START] Avvio $ServiceName..." -ForegroundColor Green
    try {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; $Command" -WindowStyle Normal -ErrorAction Stop
        Write-Host "  [WAIT] Attendo $WaitSeconds secondi per l'avvio..." -ForegroundColor Yellow
        
        # Attendi e verifica che la porta diventi disponibile
        $maxAttempts = $WaitSeconds * 2
        $attempt = 0
        $started = $false
        
        while ($attempt -lt $maxAttempts) {
            Start-Sleep -Milliseconds 500
            if (Test-Port -Port $Port) {
                $started = $true
                break
            }
            $attempt++
        }
        
        if ($started) {
            Write-Host "  [OK] $ServiceName avviato su $Url" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  [WARN] $ServiceName potrebbe non essere ancora pronto. Verifica manualmente." -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "  [ERROR] Impossibile avviare $ServiceName : $_" -ForegroundColor Red
        return $false
    }
}

# ============================================
# STEP 1: Qdrant (Docker)
# ============================================
Write-Host "[STEP 1] Verifica Qdrant container..." -ForegroundColor Cyan

$qdrantRunning = docker ps --filter "name=qdrant" --format "{{.Names}}" 2>&1
if ($qdrantRunning -like "*qdrant*") {
    Write-Host "  [OK] Qdrant container è già attivo" -ForegroundColor Green
} else {
    Write-Host "  [START] Avvio Qdrant container..." -ForegroundColor Yellow
    
    # Verifica se il container esiste ma è fermo
    $qdrantExists = docker ps -a --filter "name=qdrant" --format "{{.Names}}" 2>&1
    if ($qdrantExists -like "*qdrant*") {
        Write-Host "  [RESTART] Riavvio container esistente..." -ForegroundColor Yellow
        docker start qdrant | Out-Null
    } else {
        # Crea la directory di storage se non esiste
        $storagePath = Join-Path $PWD "qdrant_storage"
        if (-not (Test-Path $storagePath)) {
            New-Item -ItemType Directory -Path $storagePath | Out-Null
        }
        $storagePathWin = $storagePath -replace '\\', '/'
        Write-Host "  [CREATE] Creo nuovo container..." -ForegroundColor Yellow
        docker run -d --name qdrant -p 6333:6333 -v "${storagePathWin}:/qdrant/storage" qdrant/qdrant | Out-Null
    }
    
    Start-Sleep -Seconds 3
    Write-Host "  [OK] Qdrant container avviato su http://localhost:6333" -ForegroundColor Green
}

Write-Host ""

# ============================================
# STEP 2: FastAPI (Main App)
# ============================================
Write-Host "[STEP 2] Verifica FastAPI server (porta 8000)..." -ForegroundColor Cyan

if (Test-Port -Port 8000) {
    Write-Host "  [RESTART] FastAPI è attivo, riavvio..." -ForegroundColor Yellow
    Stop-ProcessOnPort -Port 8000 -ServiceName "FastAPI"
} else {
    Write-Host "  [INFO] FastAPI non è attivo" -ForegroundColor Gray
}

$fastApiStarted = Start-Service -ServiceName "FastAPI" -Command "uv run uvicorn app:app --host 127.0.0.1 --port 8000" -Port 8000 -Url "http://127.0.0.1:8000" -WaitSeconds 8

# Verifica che l'endpoint Inngest sia accessibile
if ($fastApiStarted) {
    Start-Sleep -Seconds 2
    try {
        $testResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/inngest" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Host "  [VERIFY] Endpoint Inngest verificato (Status: $($testResponse.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] Endpoint Inngest non ancora disponibile. Potrebbe essere necessario attendere qualche secondo." -ForegroundColor Yellow
    }
}

Write-Host ""

# ============================================
# STEP 3: React Frontend
# ============================================
Write-Host "[STEP 3] Verifica React frontend (porta 3000)..." -ForegroundColor Cyan

if (Test-Port -Port 3000) {
    Write-Host "  [RESTART] React frontend è attivo, riavvio..." -ForegroundColor Yellow
    Stop-ProcessOnPort -Port 3000 -ServiceName "React Frontend"
} else {
    Write-Host "  [INFO] React frontend non è attivo" -ForegroundColor Gray
}

# Verifica che esista la directory frontend
if (-not (Test-Path "frontend")) {
    Write-Host "  [ERROR] Directory 'frontend' non trovata!" -ForegroundColor Red
    Write-Host "  [INFO] Esegui prima: cd frontend && npm install" -ForegroundColor Yellow
} else {
    # Verifica che node_modules esista
    if (-not (Test-Path "frontend\node_modules")) {
        Write-Host "  [WARN] node_modules non trovato. Esegui: cd frontend; npm install" -ForegroundColor Yellow
    } else {
        Start-Service -ServiceName "React Frontend" -Command "cd frontend; npm run dev" -Port 3000 -Url "http://localhost:3000" -WaitSeconds 8
    }
}

Write-Host ""

# ============================================
# STEP 4: Inngest Dev Server
# ============================================
Write-Host "[STEP 4] Verifica Inngest dev server (porta 8288)..." -ForegroundColor Cyan

Start-Service -ServiceName "Inngest" -Command "npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery" -Port 8288 -Url "http://localhost:8288" -WaitSeconds 5

Write-Host ""

# ============================================
# Riepilogo
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Avvio completato!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifica finale dello stato dei servizi
Write-Host "Verifica finale servizi..." -ForegroundColor Cyan
$allOk = $true

if (Test-Port -Port 6333) {
    Write-Host "  [OK] Qdrant:    http://localhost:6333/dashboard" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Qdrant non è attivo" -ForegroundColor Red
    $allOk = $false
}

if (Test-Port -Port 8000) {
    Write-Host "  [OK] FastAPI:   http://127.0.0.1:8000" -ForegroundColor Green
    try {
        $test = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/inngest" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        Write-Host "  [OK] Endpoint Inngest: http://127.0.0.1:8000/api/inngest" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] FastAPI attivo ma endpoint Inngest non risponde" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [FAIL] FastAPI non è attivo" -ForegroundColor Red
    $allOk = $false
}

if (Test-Port -Port 3000) {
    Write-Host "  [OK] React Frontend: http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "  [WARN] React Frontend potrebbe non essere ancora pronto" -ForegroundColor Yellow
}

if (Test-Port -Port 8288) {
    Write-Host "  [OK] Inngest:   http://localhost:8288" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Inngest potrebbe non essere ancora pronto" -ForegroundColor Yellow
}

Write-Host ""
if ($allOk) {
    Write-Host "Tutti i servizi principali sono attivi!" -ForegroundColor Green
} else {
    Write-Host "Alcuni servizi potrebbero non essere attivi. Verifica le finestre PowerShell aperte per eventuali errori." -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Per fermare tutti i servizi, usa: .\stop.ps1" -ForegroundColor Yellow
Write-Host ""

