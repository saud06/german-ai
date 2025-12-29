# GPU Backend Setup Guide

## 🎯 Overview

This project automatically detects the environment and uses the appropriate backend:

- **Local Dev (Mac):** Native Ollama with Apple Silicon GPU (Metal) - **1-3s generation**
- **Deployment (Server):** Docker Ollama with NVIDIA GPU - **1-3s generation**
- **Fallback:** Docker Ollama with CPU - **18-30s generation**

**No manual configuration needed!** The backend auto-detects and switches.

---

## 🍎 Local Development (Apple Silicon)

### Prerequisites
- macOS with Apple Silicon (M1/M2/M3)
- Homebrew installed

### Setup (One-time)

```bash
# Run the setup script
./setup-gpu.sh
```

This will:
1. Install Ollama (if not installed)
2. Start Ollama on port 11435 (GPU backend)
3. Download llama3.2:1b model
4. Optionally download mistral:7b

### Start Development

```bash
# Start Docker services (CPU backend as fallback)
docker compose up -d

# The backend will automatically use GPU (port 11435) when available!
```

### Verify GPU Backend

```bash
# Check if GPU backend is running
lsof -i :11435

# Check logs
tail -f /tmp/ollama-gpu.log

# Test GPU backend
curl http://localhost:11435/api/tags
```

### Performance

- **Transcription:** 1-2s (Whisper)
- **Generation:** 1-3s ⚡ (GPU)
- **Synthesis:** 2-3s (Piper)
- **Total:** ~5-8s ✅

---

## 🚀 Deployment (NVIDIA GPU Server)

### Prerequisites
- Linux server with NVIDIA GPU
- Docker with NVIDIA Container Toolkit
- NVIDIA drivers installed

### Setup NVIDIA Container Toolkit

```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Deploy with GPU

```bash
# Use production compose file
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify GPU is being used
docker exec german_ollama nvidia-smi
```

### Performance

- **Transcription:** 1-2s (Whisper)
- **Generation:** 1-3s ⚡ (NVIDIA GPU)
- **Synthesis:** 2-3s (Piper)
- **Total:** ~5-8s ✅

---

## 🔧 Environment Detection

The backend automatically detects the environment:

### Detection Logic

```python
# Check 1: Running in Docker?
if os.path.exists('/.dockerenv'):
    → Use Docker Ollama (port 11434)

# Check 2: Apple Silicon + Native Ollama available?
elif platform.machine() == 'arm64' and port_11435_open:
    → Use Native Ollama (port 11435) with GPU

# Check 3: Fallback
else:
    → Use Docker Ollama (port 11434)
```

### Logs

Check backend logs to see which backend is being used:

```bash
docker compose logs backend | grep "Backend Environment"
```

You'll see:
```
🔧 Backend Environment: local_gpu
🔧 Ollama Host: http://localhost:11435
🔧 GPU Available: True
🔧 Platform: Darwin (arm64)
```

Or in deployment:
```
🔧 Backend Environment: docker
🔧 Ollama Host: http://ollama:11434
🔧 GPU Available: False
🔧 Platform: Linux (x86_64)
```

---

## 📊 Performance Comparison

| Environment | Backend | Generation Time | Total Time |
|-------------|---------|-----------------|------------|
| **Local (Mac)** | Native GPU | 1-3s ⚡ | 5-8s |
| **Deployment (NVIDIA)** | Docker GPU | 1-3s ⚡ | 5-8s |
| **Fallback (CPU)** | Docker CPU | 18-30s ❌ | 23-35s |

---

## 🛠️ Troubleshooting

### GPU Backend Not Starting (Mac)

```bash
# Check if Ollama is running
lsof -i :11435

# Restart GPU backend
launchctl unload ~/Library/LaunchAgents/com.ollama.gpu.plist
launchctl load ~/Library/LaunchAgents/com.ollama.gpu.plist

# Check logs
tail -f /tmp/ollama-gpu.log
```

### Backend Using CPU Instead of GPU

```bash
# Check environment detection
docker compose logs backend | grep "Backend Environment"

# If showing "docker" instead of "local_gpu":
# 1. Ensure Ollama is running on port 11435
# 2. Restart backend
docker compose restart backend
```

### NVIDIA GPU Not Detected (Deployment)

```bash
# Check NVIDIA drivers
nvidia-smi

# Check Docker can access GPU
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Check container GPU access
docker exec german_ollama nvidia-smi
```

---

## 🎯 Commands Summary

### Local Development
```bash
# Setup (one-time)
./setup-gpu.sh

# Start services
docker compose up -d

# Stop GPU backend
launchctl unload ~/Library/LaunchAgents/com.ollama.gpu.plist
```

### Deployment
```bash
# Deploy with GPU
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check GPU usage
docker exec german_ollama nvidia-smi

# View logs
docker compose logs -f backend
```

---

## ✅ Success Indicators

You'll know GPU is working when you see:

1. **Logs show GPU backend:**
   ```
   🔧 Backend Environment: local_gpu (or docker with GPU)
   🔧 GPU Available: True
   ```

2. **Fast generation times:**
   ```
   ✅ AI response (2.5s, 35 chars): Mir geht's gut!
   ⏱️  Total time: 6.8s
   ```

3. **GPU usage in nvidia-smi** (deployment only)

---

## 📝 Notes

- **No code changes needed** between environments
- **Automatic detection** handles everything
- **Fallback to CPU** if GPU unavailable
- **Same codebase** for local and deployment
- **Zero manual configuration** required

---

## 🚀 Next Steps

1. Run `./setup-gpu.sh` (local dev)
2. Start services: `docker compose up -d`
3. Test voice chat
4. Enjoy 5-8s responses! ⚡
