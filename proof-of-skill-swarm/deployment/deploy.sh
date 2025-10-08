#!/bin/bash
# Proof-of-Skill Swarm Deployment Script for Linux/Mac
# One-command deployment for the complete system

echo "🌟 Initializing Proof-of-Skill Swarm..."

# Check dependencies
echo ""
echo "Checking dependencies..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed. Aborting."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is required but not installed. Aborting."
    exit 1
fi

echo "✅ All dependencies found"

# Create necessary directories
echo ""
echo "Creating project directories..."

mkdir -p quantum-state models challenges proofs qdrant-storage ethereum-data logs evolution-data

echo "✅ Directories created"

# Generate environment configuration
echo ""
echo "Generating environment configuration..."

cat > .env << 'EOF'
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
EOF

echo "✅ Environment configuration created"

# Start all services
echo ""
echo "Starting Proof-of-Skill Swarm services..."
echo "This may take a few minutes..."

docker compose up -d

if [ $? -eq 0 ]; then
    echo "✅ Services started successfully"
else
    echo "❌ Failed to start services"
    exit 1
fi

# Wait for services to initialize
echo ""
echo "⏳ Waiting for services to initialize..."
echo "   This will take about 45 seconds..."
sleep 45

# Verify deployment
echo ""
echo "🔍 Verifying deployment..."

check_service() {
    local name=$1
    local url=$2
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $name is online"
        return 0
    else
        echo "❌ $name failed to start"
        return 1
    fi
}

check_service "Quantum Intent Processor" "http://localhost:3001/health"
check_service "Challenge Generator" "http://localhost:3002/health"
check_service "ZK-Proof Generator" "http://localhost:3005/health"

# Display summary
echo ""
echo "======================================================================"
echo "🌟 Proof-of-Skill Swarm Deployment Complete!"
echo "======================================================================"

echo ""
echo "📊 Access Points:"
echo "   🌐 Frontend Interface:        http://localhost:3000"
echo "   🧠 Quantum Intent Processor:  http://localhost:3001"
echo "   🎯 Challenge Generator:       http://localhost:3002"
echo "   🔐 ZK-Proof Generator:        http://localhost:3005"
echo "   📊 System Metrics:            http://localhost:3009/metrics"
echo "   🔗 Ethereum Node:             http://localhost:8545"

echo ""
echo "🚀 Quick Start:"
echo "   Open your browser and navigate to: http://localhost:3000"
echo "   Or test the API:"
echo "   curl -X POST http://localhost:3002/api/v1/challenge \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"processedIntent\":{\"domain\":\"react\",\"difficulty\":5}}'"

echo ""
echo "📖 Useful Commands:"
echo "   View logs:     docker compose logs -f"
echo "   Stop system:   docker compose down"
echo "   Restart:       docker compose restart"
echo "   Status:        docker compose ps"

echo ""
echo "🌟 Happy Skill Proving!"
echo ""
