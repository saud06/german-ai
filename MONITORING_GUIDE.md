# 🔍 GPU Performance Monitoring Guide

**For Apple Silicon (M1/M2/M3)**

---

## 🎯 Quick Start

### **Option 1: Simple Performance Monitor (Recommended)**

```bash
./monitor-performance.sh
```

Shows real-time stats for:
- Backend CPU/Memory
- Ollama GPU CPU/Memory
- Docker services status
- System resources
- Loaded models

---

## 📊 Monitoring Tools

### **1. Activity Monitor (Built-in)**

**GUI Method:**
1. Open Activity Monitor: `⌘ + Space` → type "Activity Monitor"
2. Go to **Window** → **GPU History**
3. Look for `ollama` process

**Shows:**
- GPU usage percentage
- GPU memory usage
- Real-time graphs

---

### **2. `asitop` - Best for Apple Silicon**

**Install:**
```bash
pip3 install asitop
```

**Run:**
```bash
sudo asitop
```

**What you see:**
```
╭─────────────────────────────────────────╮
│ GPU Usage:        ████████░░ 45%        │
│ GPU Power:        2.5W                  │
│ GPU Frequency:    1200 MHz              │
│ Neural Engine:    ██░░░░░░░░ 15%        │
│ Memory:           8.2 GB / 16 GB        │
│ CPU Usage:        ███░░░░░░░ 30%        │
╰─────────────────────────────────────────╯

Processes:
ollama          GPU: 45%  CPU: 15%  MEM: 2.1GB
Python          GPU: 0%   CPU: 5%   MEM: 150MB
```

**Best for:**
- Real-time GPU monitoring
- Detailed process stats
- Neural Engine usage
- Power consumption

---

### **3. `powermetrics` (Built-in)**

**Run:**
```bash
sudo powermetrics --samplers gpu_power -i 1000
```

**What you see:**
```
GPU Power: 2500 mW
GPU Utilization: 45%
GPU Frequency: 1200 MHz
GPU Active Residency: 45.2%
```

**Best for:**
- Detailed power metrics
- GPU frequency
- Precise measurements

---

### **4. Monitor Ollama Specifically**

**Check loaded models:**
```bash
curl http://localhost:11435/api/ps | python3 -m json.tool
```

**Response:**
```json
{
  "models": [
    {
      "name": "llama3.2:1b",
      "size": 1300000000,
      "digest": "...",
      "details": {
        "format": "gguf",
        "family": "llama",
        "parameter_size": "1.2B"
      }
    }
  ]
}
```

**Check Ollama process:**
```bash
ps aux | grep ollama
```

---

## 📈 Performance Benchmarking

### **Test AI Generation Speed**

Create a test script:

```bash
#!/bin/bash
echo "Testing AI generation speed..."

for i in {1..5}; do
    echo "Test $i:"
    time curl -s http://localhost:11435/api/generate -d '{
      "model": "llama3.2:1b",
      "prompt": "Hallo, wie geht es dir?",
      "stream": false
    }' | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])"
    echo ""
done
```

**Expected output:**
```
Test 1:
Mir geht es gut, danke!
real    0m1.234s  ← GPU time!

Test 2:
Sehr gut, und dir?
real    0m0.987s  ← Even faster (cached)
```

---

## 🔥 Performance Comparison

### **CPU vs GPU (Apple Silicon)**

| Metric | CPU (Docker) | GPU (Native) | Improvement |
|--------|--------------|--------------|-------------|
| **First Response** | 8-12s | 1-3s | **4-6x faster** |
| **Cached Response** | 5-8s | 0.5-1s | **8-10x faster** |
| **Power Usage** | ~5-8W | ~2-4W | **More efficient** |
| **Temperature** | Higher | Lower | **Cooler** |

---

## 🎯 What to Monitor During Voice Chat

### **Before Request:**
```bash
# Terminal 1: Monitor performance
./monitor-performance.sh

# Terminal 2: Watch backend logs
tail -f /tmp/backend-dev.log | grep -E "(🎤|✅|⏱️)"
```

### **During Voice Chat:**

1. **Speak German:** "Hallo, wie geht's?"

2. **Watch logs:**
```
🎤 Transcribing audio...
✅ Transcribed (0.8s): Hallo, wie geht's?
🤖 Generating AI response...
✅ AI response (1.2s): Mir geht's gut!
✅ Audio synthesized (2.1s)
⏱️  Total time: 4.1s
```

3. **Check GPU usage spike:**
   - GPU usage jumps to 40-60% during generation
   - Drops back to idle after response
   - Total spike duration: ~1-3 seconds

---

## 📊 Expected Performance Metrics

### **Development Mode (GPU)**

```
Component         Time      GPU Usage   CPU Usage
─────────────────────────────────────────────────
Whisper (tiny)    0.5-1.5s  0%          15-25%
Ollama (GPU)      1-3s      40-60%      10-15%
Piper (TTS)       2-3s      0%          20-30%
─────────────────────────────────────────────────
Total Pipeline    5-7s      Peak: 60%   Peak: 30%
```

### **Idle State**
```
Backend:    CPU: 0-2%   Memory: 150MB
Ollama:     CPU: 0-1%   Memory: 1.5GB (model loaded)
GPU:        0-5%        (idle)
```

### **During Generation**
```
Backend:    CPU: 5-10%  Memory: 150MB
Ollama:     CPU: 10-15% Memory: 2.5GB
GPU:        40-60%      (active)
```

---

## 🛠️ Troubleshooting

### **GPU Not Being Used?**

Check if Ollama is using GPU:
```bash
# Check process
ps aux | grep ollama

# Should show /usr/local/bin/ollama or similar
# NOT docker container
```

**Verify GPU backend:**
```bash
curl http://localhost:8000/api/v1/debug/backend-info | python3 -m json.tool
```

**Expected:**
```json
{
    "environment": "local_gpu",
    "ollama_host": "http://localhost:11435",
    "gpu_available": true
}
```

### **Slow Performance?**

1. **Check if model is loaded:**
```bash
curl http://localhost:11435/api/ps
```

2. **Pre-warm the model:**
```bash
curl http://localhost:11435/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "test",
  "keep_alive": "24h"
}'
```

3. **Monitor during request:**
```bash
./monitor-performance.sh
```

---

## 📝 Monitoring Scripts

### **Created Scripts:**

1. **`monitor-performance.sh`** - Real-time dashboard
   - Backend status
   - Ollama status
   - Docker services
   - System resources

2. **`monitor-gpu.sh`** - GPU-specific monitoring
   - Uses `asitop` if available
   - Falls back to `powermetrics`

3. **`test-voice-pipeline.sh`** - System tests
   - Verifies all services
   - Checks GPU availability
   - Tests endpoints

---

## 🎯 Quick Commands

```bash
# Monitor everything
./monitor-performance.sh

# GPU-specific monitoring
./monitor-gpu.sh

# Or use asitop directly
sudo asitop

# Check backend logs
tail -f /tmp/backend-dev.log

# Check Ollama models
curl http://localhost:11435/api/ps

# Test system
./test-voice-pipeline.sh
```

---

## 📈 Performance Tips

### **Maximize GPU Performance:**

1. **Keep model loaded:**
   - Set `OLLAMA_KEEP_ALIVE=24h` in `.env`
   - Model stays in memory for 24 hours

2. **Use smaller models for speed:**
   - `llama3.2:1b` - Fastest (1-2s)
   - `mistral:7b` - Better quality (2-4s)

3. **Monitor temperature:**
   - Use `asitop` to watch temperature
   - If too hot, reduce concurrent requests

4. **Close other GPU apps:**
   - Chrome/Safari can use GPU
   - Close unused apps for max performance

---

## ✅ Summary

**Best Monitoring Setup:**

1. **Install asitop:**
   ```bash
   pip3 install asitop
   ```

2. **Run monitoring:**
   ```bash
   # Terminal 1: System monitor
   sudo asitop
   
   # Terminal 2: Backend logs
   tail -f /tmp/backend-dev.log | grep -E "(🎤|✅|⏱️)"
   ```

3. **Test voice chat:**
   - Go to http://localhost:3000/voice-chat
   - Speak German
   - Watch GPU spike during generation

**Expected GPU Usage:**
- Idle: 0-5%
- During generation: 40-60%
- Duration: 1-3 seconds
- Power: 2-4W

---

**Happy monitoring!** 📊⚡
