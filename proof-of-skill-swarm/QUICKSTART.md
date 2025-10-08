# 🚀 Quick Start Guide

## Get Started in 5 Minutes

### Step 1: Navigate to Project Directory
```powershell
cd c:\Users\srees\Downloads\aiJOB\proof-of-skill-swarm
```

### Step 2: Run Deployment Script
```powershell
.\deployment\deploy.ps1
```

Wait 45-60 seconds for services to initialize.

### Step 3: Open Your Browser
Navigate to: **http://localhost:3000**

### Step 4: Create Your First Skill Proof

1. **Enter your intent** in the text area:
   ```
   I want to prove my React debugging ability
   ```

2. **Click "Generate Challenge"**
   - System processes your intent
   - Generates personalized challenge
   - Shows difficulty, time limit, and rewards

3. **Complete the challenge**
   - Read the challenge description
   - Check off tasks as you complete them
   - Write your solution

4. **Submit your solution**
   - System evaluates your work
   - Generates ZK-proof
   - Calculates score

5. **Receive your Skill NFT**
   - NFT is minted with your proficiency level
   - Tokens are awarded
   - View your achievement!

## Common Commands

### View Service Logs
```powershell
docker compose logs -f quantum-intent-processor
docker compose logs -f challenge-generator
docker compose logs -f zk-proof-generator
```

### Check All Services
```powershell
docker compose ps
```

### Stop the System
```powershell
docker compose down
```

### Restart Services
```powershell
docker compose restart
```

### Clean Restart (Reset All Data)
```powershell
docker compose down -v
.\deployment\deploy.ps1
```

## API Testing

### Test Intent Processing
```powershell
curl -X POST http://localhost:3001/api/v1/intent `
  -H "Content-Type: application/json" `
  -d '{"intent":"I want to prove my Python skills"}'
```

### Test Challenge Generation
```powershell
curl -X POST http://localhost:3002/api/v1/challenge `
  -H "Content-Type: application/json" `
  -d '{"processedIntent":{"domain":"python","difficulty":5}}'
```

### Check Service Health
```powershell
curl http://localhost:3001/health
curl http://localhost:3002/health
curl http://localhost:3005/health
```

## Troubleshooting

### Ports Already in Use
1. Check what's using the ports:
   ```powershell
   netstat -ano | findstr :3000
   netstat -ano | findstr :3001
   ```

2. Stop conflicting services or modify `docker-compose.yml` ports

### Services Not Starting
1. Check Docker is running:
   ```powershell
   docker version
   ```

2. View detailed logs:
   ```powershell
   docker compose logs
   ```

3. Increase Docker memory (Settings → Resources → Memory to 8GB)

### Out of Disk Space
```powershell
# Clean up Docker
docker system prune -a

# Remove old volumes
docker volume prune
```

## Next Steps

1. **Explore the API** - Check [api-specs/proof-of-skill.yaml](api-specs/proof-of-skill.yaml)

2. **Read the full docs** - See [README.md](README.md)

3. **Deploy Smart Contracts** - Follow smart contract deployment guide

4. **Customize Configuration** - Edit `.env` file

5. **Join Community** - Discord, Twitter, Forum links in README

## Need Help?

- 📖 **Documentation**: Full README.md
- 🐛 **Issues**: Create GitHub issue
- 💬 **Community**: Join Discord
- 📧 **Email**: support@proofofskill.swarm

---

**You're all set! Start proving your skills! 🎯**
