# 🚀 German AI Platform - Complete Setup Guide

This guide will help you set up the German AI Language Learning Platform on your local machine. The setup ensures **AI models run natively on your GPU** for maximum performance, while other services run in Docker containers.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
  - [macOS Setup](#macos-setup)
  - [Linux Setup](#linux-setup)
  - [Windows Setup](#windows-setup)
- [Architecture Overview](#architecture-overview)
- [Manual Setup](#manual-setup)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## 🖥️ System Requirements

### Minimum Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 15GB free space (for AI models and Docker images)
- **Internet**: Stable connection for downloading models (~7GB)

### Software Requirements
- **Docker Desktop**: Latest version
- **MongoDB Atlas**: Free tier account (or local MongoDB)
- **Git**: For cloning the repository

### GPU Requirements (Recommended)
- **macOS**: Apple Silicon (M1/M2/M3/M4) with Metal support
- **Linux**: NVIDIA GPU (CUDA support) or AMD GPU (ROCm support)
- **Windows**: NVIDIA GPU (CUDA support) or AMD GPU

> **Note**: The platform works on CPU, but GPU provides 10-15x faster AI responses.

---

## 🚀 Quick Start

Choose your operating system and follow the automated setup:

### 🍎 macOS Setup

**For Apple Silicon (M1/M2/M3/M4) or Intel Macs**

1. **Clone the repository**
```bash
git clone https://github.com/saud06/german-ai.git
cd german-ai
```

2. **Run the setup script**
```bash
chmod +x setup-macos.sh
./setup-macos.sh
```

3. **Configure your environment**
```bash
# Edit .env file with your MongoDB URI
nano .env

# Update these values:
# MONGODB_URI=your_mongodb_atlas_uri
# JWT_SECRET=your_secure_random_string_min_32_chars
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**What the script does:**
- ✅ Installs Ollama natively (GPU-accelerated via Metal)
- ✅ Configures Ollama on port 11435
- ✅ Downloads AI models (Gemma 2, Mistral 7B, Llama 3.2)
- ✅ Starts Docker containers (Whisper, Piper, Redis, Backend, Frontend)
- ✅ Verifies GPU usage

---

### 🐧 Linux Setup

**For Ubuntu, Debian, Fedora, and other Linux distributions**

1. **Clone the repository**
```bash
git clone https://github.com/saud06/german-ai.git
cd german-ai
```

2. **Run the setup script**
```bash
chmod +x setup-linux.sh
./setup-linux.sh
```

3. **Configure your environment**
```bash
# Edit .env file with your MongoDB URI
nano .env

# Update these values:
# MONGODB_URI=your_mongodb_atlas_uri
# JWT_SECRET=your_secure_random_string_min_32_chars
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**What the script does:**
- ✅ Detects GPU (NVIDIA/AMD/Intel)
- ✅ Installs Ollama natively (GPU-accelerated)
- ✅ Creates systemd service for Ollama on port 11435
- ✅ Downloads AI models (Gemma 2, Mistral 7B, Llama 3.2)
- ✅ Starts Docker containers (Whisper, Piper, Redis, Backend, Frontend)
- ✅ Verifies GPU usage with nvidia-smi or rocm-smi

**GPU Support:**
- **NVIDIA**: Requires CUDA drivers installed
- **AMD**: Requires ROCm drivers installed
- **Intel**: Limited support, CPU fallback

---

### 🪟 Windows Setup

**For Windows 10/11 with WSL2 or native Docker Desktop**

1. **Clone the repository**
```powershell
git clone https://github.com/saud06/german-ai.git
cd german-ai
```

2. **Run the setup script** (PowerShell as Administrator)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup-windows.ps1
```

3. **Configure your environment**
```powershell
# Edit .env file with your MongoDB URI
notepad .env

# Update these values:
# MONGODB_URI=your_mongodb_atlas_uri
# JWT_SECRET=your_secure_random_string_min_32_chars
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**What the script does:**
- ✅ Detects GPU (NVIDIA/AMD/Intel)
- ✅ Installs Ollama natively (GPU-accelerated)
- ✅ Configures Ollama on port 11435
- ✅ Downloads AI models (Gemma 2, Mistral 7B, Llama 3.2)
- ✅ Starts Docker containers (Whisper, Piper, Redis, Backend, Frontend)
- ✅ Verifies GPU usage with nvidia-smi

**GPU Support:**
- **NVIDIA**: Requires CUDA drivers installed
- **AMD**: Experimental support
- **Intel**: Limited support, CPU fallback

---

## 🏗️ Architecture Overview

### Service Distribution

| Service | Location | Port | GPU | Purpose |
|---------|----------|------|-----|---------|
| **Ollama** | **Native (Host)** | **11435** | **✅ Yes** | **AI Models (Gemma 2, Mistral, Llama)** |
| Backend | Docker | 8000 | ❌ No | FastAPI REST API |
| Frontend | Docker | 3000 | ❌ No | Next.js Web App |
| Whisper | Docker | 9000 | ❌ No | Speech-to-Text |
| Piper | Docker | 10200 | ❌ No | Text-to-Speech |
| Redis | Docker | 6379 | ❌ No | Caching |
| MongoDB | Atlas/Cloud | 27017 | ❌ No | Database |

### Why This Architecture?

**Native Ollama on GPU:**
- ⚡ **10-15x faster** AI responses (1-2s vs 10-15s on CPU)
- 🎯 **Better quality** with larger models (Mistral 7B, Gemma 2)
- 💰 **Zero cost** - no API fees
- 🔒 **Privacy** - all AI processing stays local

**Docker for Other Services:**
- 📦 **Easy deployment** - one command to start everything
- 🔄 **Consistent environment** - works the same everywhere
- 🛠️ **Easy updates** - rebuild containers without affecting Ollama

### AI Model Usage

| Feature | Model | Size | Purpose |
|---------|-------|------|---------|
| Grammar Checking | Gemma 2:9b | 5.4GB | High accuracy German grammar |
| Quiz Generation | Mistral 7B | 4.1GB | Natural question generation |
| Scenarios | Mistral 7B | 4.1GB | Conversational AI |
| Voice Chat | Llama 3.2:3b | 2.0GB | Fast responses |

---

## 🔧 Manual Setup

If the automated scripts don't work, follow these manual steps:

### Step 1: Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

### Step 2: Configure Ollama

**macOS/Linux:**
```bash
# Set environment variables
export OLLAMA_HOST=0.0.0.0:11435
export OLLAMA_KEEP_ALIVE=24h

# Start Ollama
ollama serve
```

**Windows (PowerShell):**
```powershell
$env:OLLAMA_HOST = "127.0.0.1:11435"
$env:OLLAMA_KEEP_ALIVE = "24h"
ollama serve
```

### Step 3: Pull AI Models

```bash
# Set Ollama host
export OLLAMA_HOST=http://localhost:11435  # macOS/Linux
$env:OLLAMA_HOST = "http://localhost:11435"  # Windows

# Pull models
ollama pull gemma2:9b
ollama pull mistral:7b
ollama pull llama3.2:3b
```

### Step 4: Setup Environment File

```bash
cp .env.example .env
```

Edit `.env` and update:
```bash
# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=german_ai

# Security
JWT_SECRET=your-super-secret-jwt-key-min-32-chars

# Ollama (Native GPU)
OLLAMA_HOST=http://host.docker.internal:11435
OLLAMA_MODEL=mistral:7b
OLLAMA_MODEL_FAST=llama3.2:3b
OLLAMA_MODEL_GRAMMAR=gemma2:9b
```

### Step 5: Start Docker Services

**macOS:**
```bash
docker compose up -d --build
```

**Linux:**
```bash
docker compose -f docker-compose.linux.yml up -d --build
```

**Windows:**
```powershell
docker compose -f docker-compose.windows.yml up -d --build
```

---

## 🔍 Troubleshooting

### Ollama Issues

**Problem: Ollama not starting**
```bash
# Check if port 11435 is in use
lsof -i :11435  # macOS/Linux
netstat -ano | findstr :11435  # Windows

# Kill the process and restart
pkill ollama  # macOS/Linux
Stop-Process -Name "ollama" -Force  # Windows
```

**Problem: Models not downloading**
```bash
# Check Ollama connection
curl http://localhost:11435/

# Check disk space
df -h  # macOS/Linux
Get-PSDrive  # Windows

# Retry model pull
OLLAMA_HOST=http://localhost:11435 ollama pull gemma2:9b
```

**Problem: GPU not being used**

**NVIDIA (Linux/Windows):**
```bash
# Check GPU availability
nvidia-smi

# Check CUDA installation
nvcc --version

# Monitor GPU usage while running Ollama
watch -n 1 nvidia-smi
```

**AMD (Linux):**
```bash
# Check GPU availability
rocm-smi

# Monitor GPU usage
watch -n 1 rocm-smi
```

**Apple Silicon (macOS):**
```bash
# Monitor GPU usage
sudo powermetrics --samplers gpu_power -i 1000
```

### Docker Issues

**Problem: Docker containers not starting**
```bash
# Check Docker status
docker ps -a

# View logs
docker compose logs backend
docker compose logs frontend

# Rebuild containers
docker compose down
docker compose up -d --build
```

**Problem: Backend can't connect to Ollama**
```bash
# Check if Ollama is accessible from Docker
docker exec german_backend curl http://host.docker.internal:11435/

# If fails, check Docker network
docker network ls
docker network inspect german-ai-network
```

**Problem: Port conflicts**
```bash
# Check what's using the ports
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :11435  # Ollama

# Kill processes or change ports in docker-compose.yml
```

### MongoDB Issues

**Problem: Can't connect to MongoDB**
```bash
# Test MongoDB connection
docker exec german_backend python3 -c "from app.db import get_db; import asyncio; asyncio.run(get_db())"

# Check .env file
cat .env | grep MONGODB_URI

# Verify MongoDB Atlas IP whitelist
# Go to MongoDB Atlas → Network Access → Add IP Address → Allow Access from Anywhere (0.0.0.0/0)
```

### Performance Issues

**Problem: Slow AI responses**
```bash
# Check if Ollama is using GPU
# NVIDIA
nvidia-smi

# AMD
rocm-smi

# Apple Silicon
sudo powermetrics --samplers gpu_power -i 1000

# Check Ollama logs
tail -f /tmp/ollama-gpu.log  # macOS
sudo journalctl -u ollama -f  # Linux
```

**Problem: High CPU usage**
```bash
# Check Docker resource limits
docker stats

# Reduce parallel requests in .env
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
```

---

## ❓ FAQ

### General Questions

**Q: Do I need a GPU?**
A: No, but highly recommended. GPU provides 10-15x faster AI responses. The platform works on CPU but will be slower.

**Q: How much disk space do I need?**
A: ~15GB total:
- AI models: ~7GB
- Docker images: ~5GB
- Application code: ~500MB
- MongoDB data: ~2GB (grows over time)

**Q: Can I use local MongoDB instead of Atlas?**
A: Yes, but not recommended for development. If you want local MongoDB:
```bash
# Start MongoDB in Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Update .env
MONGODB_URI=mongodb://localhost:27017
```

**Q: How do I update the AI models?**
```bash
# Pull latest versions
OLLAMA_HOST=http://localhost:11435 ollama pull gemma2:9b
OLLAMA_HOST=http://localhost:11435 ollama pull mistral:7b

# Restart backend
docker compose restart backend
```

### Platform-Specific Questions

**Q: (macOS) Does this work on Intel Macs?**
A: Yes, but GPU acceleration is limited. Apple Silicon (M1/M2/M3/M4) provides best performance via Metal.

**Q: (Linux) Which GPU is best?**
A: NVIDIA GPUs with CUDA support provide best compatibility. AMD GPUs work with ROCm but may require additional setup.

**Q: (Windows) Do I need WSL2?**
A: Not required, but recommended for better Docker performance. The setup works with both native Docker Desktop and WSL2.

**Q: (Windows) Can I use AMD GPU?**
A: AMD GPU support on Windows is experimental. NVIDIA GPUs are recommended for best results.

### Development Questions

**Q: How do I view logs?**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend

# Ollama logs
tail -f /tmp/ollama-gpu.log  # macOS
sudo journalctl -u ollama -f  # Linux
```

**Q: How do I restart services?**
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend

# Rebuild after code changes
docker compose up -d --build backend
```

**Q: How do I stop everything?**
```bash
# Stop Docker containers
docker compose down

# Stop Ollama (macOS)
launchctl unload ~/Library/LaunchAgents/com.ollama.server.plist

# Stop Ollama (Linux)
sudo systemctl stop ollama

# Stop Ollama (Windows)
Stop-Process -Name "ollama" -Force
```

**Q: How do I seed the database?**
```bash
# Seed learning path
docker compose exec backend python scripts/seed_complete_learning_path.py

# Seed vocabulary
docker compose exec backend python scripts/import_seed_words.py

# Seed achievements
docker compose exec backend python scripts/seed_achievements.py

# Create admin user
docker compose exec backend python scripts/set_admin.py
```

---

## 📞 Support

If you encounter issues not covered in this guide:

1. **Check logs**: `docker compose logs -f`
2. **Check Ollama**: `curl http://localhost:11435/`
3. **Check GPU**: `nvidia-smi` / `rocm-smi` / `powermetrics`
4. **GitHub Issues**: https://github.com/saud06/german-ai/issues
5. **Email**: saud06@example.com

---

## 🎉 Success Checklist

After setup, verify everything works:

- [ ] Ollama running on port 11435
- [ ] AI models downloaded (gemma2:9b, mistral:7b, llama3.2:3b)
- [ ] GPU being used (check with nvidia-smi/rocm-smi/powermetrics)
- [ ] Docker containers running (backend, frontend, redis, whisper, piper)
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend API accessible at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] MongoDB connection working
- [ ] Grammar check working (test on Grammar Coach page)
- [ ] Voice features working (test on Speech Practice page)

**Congratulations! You're ready to learn German with AI! 🇩🇪🚀**
