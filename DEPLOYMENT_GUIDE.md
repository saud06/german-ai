# 🚀 German AI Learner - Deployment Guide

Complete guide for deploying the German AI Learner platform to production.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Requirements](#server-requirements)
3. [Quick Start](#quick-start)
4. [Production Deployment](#production-deployment)
5. [Configuration](#configuration)
6. [Monitoring](#monitoring)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)
9. [Scaling](#scaling)

---

## 🔧 Prerequisites

### Required Software:
- **Docker** 24.0+ ([Install Guide](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.20+ ([Install Guide](https://docs.docker.com/compose/install/))
- **Git** (for cloning repository)

### Optional (Recommended):
- **NVIDIA GPU** with CUDA support (for AI acceleration)
- **NVIDIA Container Toolkit** ([Install Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html))

### Verify Installation:
```bash
docker --version
docker-compose --version
nvidia-smi  # If using GPU
```

---

## 💻 Server Requirements

### Minimum (CPU-only):
- **CPU:** 8 cores
- **RAM:** 16GB
- **Disk:** 100GB SSD
- **Network:** 100 Mbps

**Expected Performance:**
- AI response time: 10-30s
- Concurrent users: 10-20
- Cost: ~$50/month (VPS)

### Recommended (GPU):
- **CPU:** 8+ cores
- **RAM:** 32GB
- **GPU:** NVIDIA RTX 3060 or better (12GB+ VRAM)
- **Disk:** 200GB SSD
- **Network:** 1 Gbps

**Expected Performance:**
- AI response time: 1-5s
- Concurrent users: 50-100
- Cost: ~$100-200/month (GPU VPS)

### Production (High Traffic):
- **CPU:** 16+ cores
- **RAM:** 64GB
- **GPU:** NVIDIA A100 or better
- **Disk:** 500GB NVMe SSD
- **Network:** 10 Gbps
- **Load Balancer:** Yes

**Expected Performance:**
- AI response time: <2s
- Concurrent users: 500+
- Cost: ~$500-1000/month

---

## ⚡ Quick Start

### 1. Clone Repository:
```bash
git clone https://github.com/yourusername/german-ai-learner.git
cd german-ai-learner
```

### 2. Configure Environment:
```bash
# Backend configuration
cp backend/.env.example backend/.env
nano backend/.env  # Edit with your settings

# Frontend configuration
cp frontend/.env.local.example frontend/.env.local
nano frontend/.env.local  # Set API URL
```

### 3. Deploy:
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh deploy
```

### 4. Access Platform:
- **Frontend:** http://your-server-ip:3000
- **Backend API:** http://your-server-ip:8000
- **API Docs:** http://your-server-ip:8000/docs

---

## 🏭 Production Deployment

### Step 1: Prepare Server

**Update system:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Install Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Install NVIDIA drivers (if using GPU):**
```bash
# Install NVIDIA drivers
sudo apt install nvidia-driver-535 -y

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update
sudo apt install nvidia-container-toolkit -y
sudo systemctl restart docker
```

**Verify GPU:**
```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Step 2: Configure Application

**Backend Environment (.env):**
```bash
# MongoDB
MONGODB_URL=mongodb://admin:secure_password@mongodb:27017/german_ai?authSource=admin

# Redis
REDIS_URL=redis://redis:6379

# JWT
JWT_SECRET=your_very_secure_random_secret_key_here

# AI Services
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=mistral:7b
WHISPER_HOST=http://whisper:9000
PIPER_HOST=http://piper:10200

# Features
ENABLE_AI_GRAMMAR=true
ENABLE_AI_QUIZ_TOPUP=true
ENABLE_VOICE=true

# CORS
CORS_ORIGINS=["http://your-domain.com","https://your-domain.com"]
```

**Frontend Environment (.env.local):**
```bash
NEXT_PUBLIC_API_URL=https://api.your-domain.com
```

### Step 3: SSL/HTTPS Setup

**Install Certbot:**
```bash
sudo apt install certbot python3-certbot-nginx -y
```

**Get SSL Certificate:**
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

**Configure Nginx:**
Create `nginx/nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket support
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### Step 4: Deploy

```bash
# Deploy with production configuration
./deploy.sh deploy

# Verify deployment
./deploy.sh status

# Check logs
./deploy.sh logs
```

### Step 5: Initialize Data

```bash
# Seed database
docker exec german_backend_prod python -m app.seed.seed_all

# Pull Ollama model
docker exec german_ollama_prod ollama pull mistral:7b

# Verify
curl http://localhost:8000/api/v1/analytics/health
```

---

## ⚙️ Configuration

### Environment Variables

**Backend (.env):**
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| MONGODB_URL | MongoDB connection string | - | Yes |
| REDIS_URL | Redis connection string | - | Yes |
| JWT_SECRET | Secret for JWT tokens | - | Yes |
| OLLAMA_HOST | Ollama API URL | http://localhost:11434 | Yes |
| OLLAMA_MODEL | AI model name | mistral:7b | Yes |
| WHISPER_HOST | Whisper API URL | http://localhost:9000 | Yes |
| PIPER_HOST | Piper API URL | http://localhost:10200 | Yes |
| ENABLE_AI_GRAMMAR | Enable AI grammar checking | true | No |
| ENABLE_AI_QUIZ_TOPUP | Enable AI quiz generation | true | No |
| ENABLE_VOICE | Enable voice features | true | No |
| CORS_ORIGINS | Allowed CORS origins | ["*"] | No |

**Frontend (.env.local):**
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| NEXT_PUBLIC_API_URL | Backend API URL | http://localhost:8000 | Yes |

### Docker Compose Configuration

**Resource Limits:**
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

**Health Checks:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## 📊 Monitoring

### Real-time Monitoring

**Start monitor:**
```bash
./monitor.sh
```

**Output:**
```
📊 German AI Learner - System Monitor
======================================
2025-11-08 08:30:00

🔧 Service Status:
  Backend:    ✓
  Frontend:   ✓
  MongoDB:    ✓
  Redis:      ✓
  Ollama:     ✓
  Whisper:    ✓
  Piper:      ✓

📈 Platform Metrics:
  Total Users:     150
  Total Scenarios: 10
  Total Quizzes:   500

💻 Resource Usage:
NAME                  CPU %    MEM USAGE
german_backend_prod   15.2%    2.1GB / 4GB
german_ollama_prod    45.8%    8.5GB / 16GB
...
```

### Analytics API

**System Health:**
```bash
curl http://localhost:8000/api/v1/analytics/health
```

**Full Metrics:**
```bash
curl http://localhost:8000/api/v1/analytics/metrics
```

**AI Features Stats:**
```bash
curl http://localhost:8000/api/v1/analytics/ai-features
```

### Logs

**View all logs:**
```bash
./deploy.sh logs
```

**View specific service:**
```bash
./deploy.sh logs backend
./deploy.sh logs ollama
```

**Follow logs:**
```bash
docker-compose -f docker-compose.production.yml logs -f backend
```

---

## 💾 Backup & Recovery

### Automated Backup

**Create backup:**
```bash
./deploy.sh backup
```

**Backups are stored in:**
```
./backups/
  ├── mongodb_20251108_083000.archive
  ├── volumes_20251108_083000.tar.gz
  └── ...
```

### Manual Backup

**MongoDB:**
```bash
docker exec german_mongodb_prod mongodump \
  --uri="mongodb://admin:password@localhost:27017/german_ai?authSource=admin" \
  --archive=/tmp/backup.archive

docker cp german_mongodb_prod:/tmp/backup.archive ./backup.archive
```

**Volumes:**
```bash
docker run --rm \
  -v german_ai_mongodb_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mongodb_data.tar.gz /data
```

### Restore

**MongoDB:**
```bash
docker cp ./backup.archive german_mongodb_prod:/tmp/backup.archive

docker exec german_mongodb_prod mongorestore \
  --uri="mongodb://admin:password@localhost:27017/german_ai?authSource=admin" \
  --archive=/tmp/backup.archive
```

**Volumes:**
```bash
docker run --rm \
  -v german_ai_mongodb_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/mongodb_data.tar.gz -C /
```

### Automated Backup Schedule

**Cron job (daily at 2 AM):**
```bash
crontab -e

# Add this line:
0 2 * * * cd /path/to/german-ai-learner && ./deploy.sh backup
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Ollama not responding:**
```bash
# Check logs
docker logs german_ollama_prod

# Restart service
docker restart german_ollama_prod

# Pull model again
docker exec german_ollama_prod ollama pull mistral:7b
```

**2. MongoDB connection failed:**
```bash
# Check if running
docker ps | grep mongodb

# Check logs
docker logs german_mongodb_prod

# Restart
docker restart german_mongodb_prod
```

**3. Frontend not loading:**
```bash
# Check logs
docker logs german_frontend_prod

# Rebuild
docker-compose -f docker-compose.production.yml build frontend
docker-compose -f docker-compose.production.yml up -d frontend
```

**4. Slow AI responses:**
```bash
# Check GPU usage
nvidia-smi

# Check Ollama logs
docker logs german_ollama_prod

# Warm up model
curl -X POST http://localhost:8000/api/v1/grammar/check-public \
  -H "Content-Type: application/json" \
  -d '{"sentence":"Test"}'
```

**5. Out of memory:**
```bash
# Check memory usage
docker stats

# Increase limits in docker-compose.production.yml
# Then restart:
./deploy.sh restart
```

### Debug Mode

**Enable debug logging:**
```bash
# In backend/.env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart
./deploy.sh restart backend
```

### Health Checks

**Check all services:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Health}}"
```

**Test endpoints:**
```bash
# Backend
curl http://localhost:8000/

# Frontend
curl http://localhost:3000/

# Ollama
curl http://localhost:11434/api/tags

# Whisper
curl http://localhost:9000/

# Redis
docker exec german_redis_prod redis-cli ping
```

---

## 📈 Scaling

### Horizontal Scaling

**Multiple Backend Instances:**
```yaml
backend:
  deploy:
    replicas: 3
```

**Load Balancer:**
```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

### Vertical Scaling

**Increase Resources:**
```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 8G
```

### Database Scaling

**MongoDB Replica Set:**
```yaml
mongodb:
  command: mongod --replSet rs0
```

**Redis Cluster:**
```yaml
redis:
  image: redis:7-alpine
  command: redis-server --cluster-enabled yes
```

### CDN Integration

**Static Assets:**
- Use CloudFlare or AWS CloudFront
- Configure in frontend build

**Media Files:**
- Store in S3 or similar
- Serve via CDN

---

## 🎯 Performance Optimization

### Caching

**Redis Configuration:**
```bash
# In docker-compose.production.yml
command: >
  redis-server
  --maxmemory 2gb
  --maxmemory-policy allkeys-lru
```

**Backend Caching:**
- Vocabulary: 1 hour
- Grammar rules: 1 hour
- Scenarios: 30 minutes
- User sessions: 24 hours

### Database Indexing

**MongoDB Indexes:**
```javascript
db.vocabulary.createIndex({ level: 1, word: 1 })
db.users.createIndex({ email: 1 }, { unique: true })
db.scenarios.createIndex({ difficulty: 1, category: 1 })
```

### AI Model Optimization

**Keep-Alive:**
```bash
# In backend/.env
OLLAMA_KEEP_ALIVE=30m
```

**Model Selection:**
- Development: `mistral:7b`
- Production: `mistral:7b-instruct-q4_K_M` (quantized)
- High-end: `mixtral:8x7b`

---

## 📞 Support

**Documentation:** See `PLATFORM_COMPLETE.md`  
**Issues:** GitHub Issues  
**Email:** support@german-ai-learner.com  

---

## ✅ Deployment Checklist

- [ ] Server meets minimum requirements
- [ ] Docker and Docker Compose installed
- [ ] NVIDIA drivers installed (if using GPU)
- [ ] Environment files configured
- [ ] SSL certificates obtained
- [ ] Nginx configured
- [ ] Firewall rules set
- [ ] Backup strategy in place
- [ ] Monitoring enabled
- [ ] Domain DNS configured
- [ ] Email notifications set up
- [ ] Load testing completed
- [ ] Security audit done

---

**🎉 Your German AI Learner platform is ready for production!**
