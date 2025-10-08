# Proof-of-Skill Swarm Management Script
# Easy commands for managing your system

param(
    [Parameter(Position=0)]
    [ValidateSet('start', 'stop', 'restart', 'status', 'logs', 'clean', 'test', 'help')]
    [string]$Command = 'help'
)

function Show-Help {
    Write-Host "`n🌟 Proof-of-Skill Swarm Management" -ForegroundColor Cyan
    Write-Host "=" * 50
    Write-Host "`nAvailable Commands:" -ForegroundColor Yellow
    Write-Host "  start    - Start all services" -ForegroundColor White
    Write-Host "  stop     - Stop all services" -ForegroundColor White
    Write-Host "  restart  - Restart all services" -ForegroundColor White
    Write-Host "  status   - Show service status" -ForegroundColor White
    Write-Host "  logs     - View service logs" -ForegroundColor White
    Write-Host "  clean    - Clean and reset system" -ForegroundColor White
    Write-Host "  test     - Test API endpoints" -ForegroundColor White
    Write-Host "  help     - Show this help" -ForegroundColor White
    Write-Host "`nExamples:" -ForegroundColor Yellow
    Write-Host "  .\manage.ps1 start" -ForegroundColor Gray
    Write-Host "  .\manage.ps1 logs" -ForegroundColor Gray
    Write-Host "  .\manage.ps1 status" -ForegroundColor Gray
    Write-Host ""
}

function Start-Services {
    Write-Host "`n🚀 Starting Proof-of-Skill Swarm..." -ForegroundColor Cyan
    docker compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Services started successfully!" -ForegroundColor Green
        Write-Host "`n🌐 Access Points:" -ForegroundColor Cyan
        Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
        Write-Host "   Intent:   http://localhost:3001" -ForegroundColor White
        Write-Host "   Proof:    http://localhost:3005" -ForegroundColor White
    } else {
        Write-Host "❌ Failed to start services" -ForegroundColor Red
    }
}

function Stop-Services {
    Write-Host "`n🛑 Stopping Proof-of-Skill Swarm..." -ForegroundColor Cyan
    docker compose down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Services stopped successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to stop services" -ForegroundColor Red
    }
}

function Restart-Services {
    Write-Host "`n🔄 Restarting Proof-of-Skill Swarm..." -ForegroundColor Cyan
    docker compose restart
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Services restarted successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to restart services" -ForegroundColor Red
    }
}

function Show-Status {
    Write-Host "`n📊 Service Status:" -ForegroundColor Cyan
    docker compose ps
    
    Write-Host "`n🔍 Quick Health Checks:" -ForegroundColor Yellow
    
    $services = @{
        "Intent Processor" = "http://localhost:3001/health"
        "Challenge Gen" = "http://localhost:3002/health"
        "Proof System" = "http://localhost:3005/health"
    }
    
    foreach ($service in $services.GetEnumerator()) {
        try {
            $response = Invoke-WebRequest -Uri $service.Value -TimeoutSec 2 -ErrorAction Stop
            Write-Host "  ✅ $($service.Key)" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ $($service.Key)" -ForegroundColor Red
        }
    }
}

function Show-Logs {
    Write-Host "`n📋 Service Logs (Press Ctrl+C to exit):" -ForegroundColor Cyan
    Write-Host "Showing last 50 lines..." -ForegroundColor Gray
    docker compose logs --tail=50 -f
}

function Clean-System {
    Write-Host "`n🧹 Cleaning Proof-of-Skill Swarm..." -ForegroundColor Cyan
    Write-Host "This will remove all data and containers!" -ForegroundColor Yellow
    
    $confirm = Read-Host "Are you sure? (yes/no)"
    
    if ($confirm -eq "yes") {
        docker compose down -v
        Write-Host "✅ System cleaned!" -ForegroundColor Green
        Write-Host "Run '.\manage.ps1 start' to redeploy" -ForegroundColor Gray
    } else {
        Write-Host "❌ Cancelled" -ForegroundColor Yellow
    }
}

function Test-APIs {
    Write-Host "`n🧪 Testing API Endpoints..." -ForegroundColor Cyan
    
    # Test Intent API
    Write-Host "`n1. Testing Intent Processor..." -ForegroundColor Yellow
    try {
        $body = @{
            intent = "I want to prove my testing skills"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:3001/api/v1/intent" `
            -Method Post `
            -ContentType "application/json" `
            -Body $body `
            -TimeoutSec 5
        
        Write-Host "   ✅ Intent processed: $($response.intentId)" -ForegroundColor Green
        
        # Test Challenge Gen with processed intent
        Write-Host "`n2. Testing Challenge Generator..." -ForegroundColor Yellow
        $challengeBody = @{
            processedIntent = $response.processedIntent
        } | ConvertTo-Json
        
        $challengeResponse = Invoke-RestMethod -Uri "http://localhost:3002/api/v1/challenge" `
            -Method Post `
            -ContentType "application/json" `
            -Body $challengeBody `
            -TimeoutSec 5
        
        Write-Host "   ✅ Challenge created: $($challengeResponse.challengeId)" -ForegroundColor Green
        Write-Host "   📊 Difficulty: $($challengeResponse.difficulty)/10" -ForegroundColor Gray
        Write-Host "   🎯 Domain: $($challengeResponse.domain)" -ForegroundColor Gray
        
    } catch {
        Write-Host "   ❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "`n✅ API tests complete!" -ForegroundColor Cyan
}

# Main execution
switch ($Command) {
    'start'   { Start-Services }
    'stop'    { Stop-Services }
    'restart' { Restart-Services }
    'status'  { Show-Status }
    'logs'    { Show-Logs }
    'clean'   { Clean-System }
    'test'    { Test-APIs }
    'help'    { Show-Help }
    default   { Show-Help }
}
