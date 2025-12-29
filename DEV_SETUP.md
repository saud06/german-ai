# Development Setup Guide

## Architecture

### Native Services (GPU + Hot Reload)
- **Backend** (FastAPI) - Port 8000 - Hot reload enabled
- **Frontend** (Next.js) - Port 3000 - Hot reload enabled  
- **Ollama** (AI Models) - Port 11435 - GPU accelerated

### Docker Services
- **Redis** - Port 6379
- **Whisper** (Speech-to-Text) - Port 9000
- **Piper** (Text-to-Speech) - Port 10200

## Quick Start

```bash
# Start everything
./START_PROJECT.sh

# Stop everything
./STOP_PROJECT.sh
```

## Development Features

### Hot Reload
Both frontend and backend run natively with hot reload:
- **Frontend**: Any changes to `.tsx`, `.ts`, `.css` files auto-refresh
- **Backend**: Any changes to `.py` files auto-reload

### Logs
```bash
# Backend logs
tail -f /tmp/backend-native.log

# Frontend logs
tail -f /tmp/frontend-dev.log

# Docker services
docker compose logs -f whisper
docker compose logs -f piper
docker compose logs -f redis
```

## Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## AI Models (GPU Accelerated)
- **Mistral 7B** - Main AI model for conversations, grammar, quizzes
- **Llama 3.2 1B** - Fast model for quick responses

## Why This Setup?

### Native Frontend (Dev Mode)
- ✅ Instant hot reload - see changes immediately
- ✅ Better debugging with source maps
- ✅ Faster development cycle
- ✅ No Docker rebuild needed

### Native Backend (GPU Access)
- ✅ Direct GPU access for Ollama
- ✅ Hot reload with `--reload` flag
- ✅ Faster AI responses
- ✅ Better performance

### Docker Services
- ✅ Isolated environments for Redis, Whisper, Piper
- ✅ Easy to manage and restart
- ✅ Consistent across different machines

## Troubleshooting

### Frontend not updating?
The frontend is now in dev mode - just save your file and it will auto-refresh.

### Port already in use?
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Stop the project properly
./STOP_PROJECT.sh
```

### Need to rebuild?
Frontend changes are instant in dev mode. No rebuild needed!

## Production Deployment

For production, use Docker Compose with production builds:
```bash
docker compose up -d
```

This will build optimized production versions of both frontend and backend.
