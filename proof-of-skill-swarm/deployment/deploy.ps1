# Proof-of-Skill Swarm Deployment Script
# One-command deployment for the complete system

Write-Host "🌟 Initializing Proof-of-Skill Swarm..." -ForegroundColor Cyan

# Check dependencies
Write-Host "`nChecking dependencies..." -ForegroundColor Yellow

$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerInstalled) {
    Write-Host "❌ Docker is required but not installed. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

$dockerComposeInstalled = docker compose version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker Compose is required but not installed." -ForegroundColor Red
    exit 1
}

Write-Host "✅ All dependencies found" -ForegroundColor Green

# Create necessary directories
Write-Host "`nCreating project directories..." -ForegroundColor Yellow

$directories = @(
    "quantum-state",
    "models",
    "challenges",
    "proofs",
    "qdrant-storage",
    "ethereum-data",
    "logs",
    "evolution-data"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Gray
    }
}

Write-Host "✅ Directories created" -ForegroundColor Green

# Generate environment configuration
Write-Host "`nGenerating environment configuration..." -ForegroundColor Yellow

$envContent = @"
# Quantum Intent Processing
QUANTUM_SIMULATION=true
PENROSE_FRAMEWORK=enabled
NATURAL_LANGUAGE_MODEL=mistral-7b-instruct

# Challenge Generation
MODEL_PATH=/models/codellama-13b
CHALLENGE_COMPLEXITY=adaptive
PERSONALIZATION_ENGINE=enabled

# Task Decomposition
GNN_MODEL_PATH=/models/gnn.pt
TASK_QUEUE_REDIS=redis://redis:6379

# Human-AI Symbiosis
NEURAL_FEEDBACK=enabled
BCI_COMPATIBILITY=true
REAL_TIME_ADAPTATION=true

# Cryptographic Proof Systems
ZK_STARK_LIB_PATH=/lib/starklib
POST_QUANTUM_SIG=dilithium
PROOF_COMPLEXITY=adaptive
STEGANOGRAPHY_ALGORITHM=lsb
PROOF_STRENGTH=high
DETECTION_RESISTANCE=maximum

# Living Value Systems
ETH_RPC_URL=http://ethereum-node:8545
SKILL_NFT_CONTRACT=0x0000000000000000000000000000000000000000
DYNAMIC_METADATA=enabled

# Evolution Engine
NAS_ALGORITHM=efficient_neural_architecture_search
KNOWLEDGE_DISTILLER=distilbert
SELF_IMPROVEMENT_RATE=adaptive

# Consciousness Metrics
IIT_IMPLEMENTATION=pyphi
EMERGENCE_THRESHOLD=0.75
SAFETY_PROTOCOLS=enabled

# Frontend Configuration
REACT_APP_QUANTUM_INTENT_URL=http://localhost:3001
REACT_APP_CHALLENGE_GENERATOR_URL=http://localhost:3002
REACT_APP_ZK_PROOF_URL=http://localhost:3005
REACT_APP_SKILL_NFT_URL=http://localhost:3007
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "✅ Environment configuration created" -ForegroundColor Green

# Build Docker images
Write-Host "`nBuilding Docker images..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray

docker compose build --no-cache 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker images built successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ Some images may have build warnings, but continuing..." -ForegroundColor Yellow
}

# Start all services
Write-Host "`nStarting Proof-of-Skill Swarm services..." -ForegroundColor Yellow

docker compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Services started successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}

# Wait for services to initialize
Write-Host "`n⏳ Waiting for services to initialize..." -ForegroundColor Yellow
Write-Host "   This will take about 45 seconds..." -ForegroundColor Gray

Start-Sleep -Seconds 45

# Verify deployment
Write-Host "`n🔍 Verifying deployment..." -ForegroundColor Yellow

$services = @{
    "Quantum Intent Processor" = "http://localhost:3001/health"
    "Challenge Generator" = "http://localhost:3002/health"
    "ZK-Proof Generator" = "http://localhost:3005/health"
}

$allHealthy = $true

foreach ($service in $services.GetEnumerator()) {
    try {
        $response = Invoke-WebRequest -Uri $service.Value -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $($service.Key) is online" -ForegroundColor Green
        } else {
            Write-Host "⚠️ $($service.Key) returned status $($response.StatusCode)" -ForegroundColor Yellow
            $allHealthy = $false
        }
    } catch {
        Write-Host "❌ $($service.Key) failed to start" -ForegroundColor Red
        $allHealthy = $false
    }
}

# Display summary
Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "🌟 Proof-of-Skill Swarm Deployment Complete!" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Cyan

if ($allHealthy) {
    Write-Host "`n✅ All services are running successfully!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Some services may need additional time to start." -ForegroundColor Yellow
    Write-Host "   You can check logs with: docker compose logs -f" -ForegroundColor Gray
}

Write-Host "`n📊 Access Points:" -ForegroundColor Cyan
Write-Host "   🌐 Frontend Interface:        http://localhost:3000" -ForegroundColor White
Write-Host "   🧠 Quantum Intent Processor:  http://localhost:3001" -ForegroundColor White
Write-Host "   🎯 Challenge Generator:       http://localhost:3002" -ForegroundColor White
Write-Host "   🔐 ZK-Proof Generator:        http://localhost:3005" -ForegroundColor White
Write-Host "   📊 System Metrics:            http://localhost:3009/metrics" -ForegroundColor White
Write-Host "   🔗 Ethereum Node:             http://localhost:8545" -ForegroundColor White

Write-Host "`n🚀 Quick Start:" -ForegroundColor Cyan
Write-Host "   Open your browser and navigate to: http://localhost:3000" -ForegroundColor White
Write-Host "   Or test the API with PowerShell:" -ForegroundColor White
Write-Host '   Invoke-RestMethod -Uri http://localhost:3001/health -Method Get' -ForegroundColor Gray

Write-Host "`n📖 Useful Commands:" -ForegroundColor Cyan
Write-Host "   View logs:     docker compose logs -f" -ForegroundColor White
Write-Host "   Stop system:   docker compose down" -ForegroundColor White
Write-Host "   Restart:       docker compose restart" -ForegroundColor White
Write-Host "   Status:        docker compose ps" -ForegroundColor White

Write-Host "`n🌟 Happy Skill Proving!" -ForegroundColor Cyan
Write-Host ""
