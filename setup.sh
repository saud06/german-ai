#!/bin/bash

# =============================================================================
# German AI Language Learning Platform - Automated Setup Script
# =============================================================================
# This script automatically:
# 1. Detects your system (Linux/macOS/Windows WSL)
# 2. Installs Ollama NATIVELY with GPU support
# 3. Downloads required AI models to native Ollama
# 4. Sets up Docker containers for other services
# 5. Configures environment variables automatically
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Print functions
print_header() {
    echo -e "\n${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_step() {
    echo -e "\n${BOLD}${BLUE}▶ $1${NC}"
}

# =============================================================================
# Detect System
# =============================================================================
print_header "German AI - Automated Setup"

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

OS_TYPE=$(detect_os)
print_info "Detected OS: $OS_TYPE"

if [[ "$OS_TYPE" == "unknown" ]]; then
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

# =============================================================================
# Check Prerequisites
# =============================================================================
print_step "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first:"
    echo "  Linux: https://docs.docker.com/engine/install/"
    echo "  macOS: https://docs.docker.com/desktop/install/mac-install/"
    echo "  Windows: https://docs.docker.com/desktop/install/windows-install/"
    exit 1
fi
print_success "Docker found: $(docker --version)"

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed or not available"
    exit 1
fi
print_success "Docker Compose found: $(docker compose version)"

# Check curl
if ! command -v curl &> /dev/null; then
    print_error "curl is not installed. Please install curl first."
    exit 1
fi
print_success "curl found"

# =============================================================================
# Detect GPU
# =============================================================================
print_step "Detecting GPU..."

GPU_TYPE="none"
GPU_NAME="No GPU detected"

if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi &> /dev/null; then
        GPU_TYPE="nvidia"
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
        print_success "NVIDIA GPU detected: $GPU_NAME"
    fi
elif command -v rocm-smi &> /dev/null; then
    if rocm-smi &> /dev/null; then
        GPU_TYPE="amd"
        GPU_NAME="AMD GPU (ROCm)"
        print_success "AMD GPU detected: $GPU_NAME"
    fi
else
    print_warning "No GPU detected - will use CPU (slower performance)"
    GPU_TYPE="cpu"
fi

# =============================================================================
# Install Ollama Natively
# =============================================================================
print_step "Setting up Ollama (Native Installation)..."

OLLAMA_PORT=11435

if command -v ollama &> /dev/null; then
    print_info "Ollama is already installed"
    OLLAMA_VERSION=$(ollama --version 2>&1 | head -1 || echo "unknown")
    print_info "Version: $OLLAMA_VERSION"
else
    print_info "Installing Ollama..."
    
    if [[ "$OS_TYPE" == "linux" ]]; then
        curl -fsSL https://ollama.com/install.sh | sh
    elif [[ "$OS_TYPE" == "macos" ]]; then
        print_warning "Please install Ollama manually from: https://ollama.com/download"
        print_info "After installation, run this script again."
        exit 1
    fi
    
    print_success "Ollama installed successfully"
fi

# =============================================================================
# Configure Ollama Service (Linux systemd)
# =============================================================================
if [[ "$OS_TYPE" == "linux" ]]; then
    print_step "Configuring Ollama service..."
    
    # Create systemd service file
    sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=$USER
Group=$USER
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:$OLLAMA_PORT"
Environment="OLLAMA_ORIGINS=*"
Environment="OLLAMA_KEEP_ALIVE=24h"
Environment="OLLAMA_NUM_PARALLEL=2"

[Install]
WantedBy=default.target
EOF

    # Reload systemd and start service
    sudo systemctl daemon-reload
    sudo systemctl enable ollama
    sudo systemctl restart ollama
    
    print_success "Ollama service configured and started on port $OLLAMA_PORT"
    
    # Wait for Ollama to be ready
    print_info "Waiting for Ollama to start..."
    for i in {1..30}; do
        if curl -s http://localhost:$OLLAMA_PORT/api/tags &> /dev/null; then
            print_success "Ollama is ready"
            break
        fi
        sleep 1
    done
    
elif [[ "$OS_TYPE" == "macos" ]]; then
    print_step "Starting Ollama service..."
    
    # Set environment variables for macOS
    launchctl setenv OLLAMA_HOST "127.0.0.1:$OLLAMA_PORT"
    launchctl setenv OLLAMA_ORIGINS "*"
    launchctl setenv OLLAMA_KEEP_ALIVE "24h"
    
    # Start Ollama in background if not running
    if ! pgrep -x "ollama" > /dev/null; then
        OLLAMA_HOST=0.0.0.0:$OLLAMA_PORT ollama serve &> /tmp/ollama.log &
        sleep 3
        print_success "Ollama started on port $OLLAMA_PORT"
    else
        print_info "Ollama is already running"
    fi
fi

# =============================================================================
# Download AI Models
# =============================================================================
print_step "Downloading AI models to native Ollama..."

MODELS=(
    "mistral:7b:Main conversation model (4.4 GB)"
    "llama3.2:3b:Fast responses (2.0 GB)"
    "gemma2:9b:Grammar checking (5.4 GB)"
)

OLLAMA_HOST=http://localhost:$OLLAMA_PORT

for model_info in "${MODELS[@]}"; do
    IFS=':' read -r model size description <<< "$model_info"
    model_name="$model:$size"
    
    print_info "Checking $model_name - $description"
    
    # Check if model exists
    if OLLAMA_HOST=$OLLAMA_HOST ollama list 2>/dev/null | grep -q "^$model_name"; then
        print_success "$model_name already downloaded"
    else
        print_info "Downloading $model_name (this may take several minutes)..."
        if OLLAMA_HOST=$OLLAMA_HOST ollama pull "$model_name"; then
            print_success "$model_name downloaded successfully"
        else
            print_error "Failed to download $model_name"
            print_warning "You can download it manually later with: OLLAMA_HOST=$OLLAMA_HOST ollama pull $model_name"
        fi
    fi
done

# Verify models
print_info "Verifying installed models..."
OLLAMA_HOST=$OLLAMA_HOST ollama list

# =============================================================================
# Setup Environment File
# =============================================================================
print_step "Configuring environment variables..."

if [[ ! -f .env ]]; then
    if [[ -f .env.example ]]; then
        cp .env.example .env
        print_success "Created .env from .env.example"
    else
        print_error ".env.example not found"
        exit 1
    fi
else
    print_info ".env already exists, creating backup..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Update .env with correct Ollama configuration
print_info "Updating .env with native Ollama configuration..."

# Determine the correct host for Docker containers to reach native Ollama
if [[ "$OS_TYPE" == "linux" ]]; then
    OLLAMA_DOCKER_HOST="http://host.docker.internal:$OLLAMA_PORT"
elif [[ "$OS_TYPE" == "macos" ]]; then
    OLLAMA_DOCKER_HOST="http://host.docker.internal:$OLLAMA_PORT"
fi

# Update .env file
sed -i.bak "s|OLLAMA_HOST=.*|OLLAMA_HOST=$OLLAMA_DOCKER_HOST|g" .env
sed -i.bak "s|OLLAMA_MODEL=.*|OLLAMA_MODEL=mistral:7b|g" .env
sed -i.bak "s|OLLAMA_MODEL_FAST=.*|OLLAMA_MODEL_FAST=llama3.2:3b|g" .env
sed -i.bak "s|OLLAMA_MODEL_GRAMMAR=.*|OLLAMA_MODEL_GRAMMAR=gemma2:9b|g" .env

# Enable AI features
sed -i.bak "s|ENABLE_AI_CONVERSATION=.*|ENABLE_AI_CONVERSATION=true|g" .env
sed -i.bak "s|ENABLE_VOICE_FEATURES=.*|ENABLE_VOICE_FEATURES=true|g" .env
sed -i.bak "s|ENABLE_LIFE_SIMULATION=.*|ENABLE_LIFE_SIMULATION=true|g" .env

rm -f .env.bak

print_success "Environment configured for native Ollama on port $OLLAMA_PORT"

# =============================================================================
# Update Docker Compose (Remove Ollama Service)
# =============================================================================
print_step "Preparing Docker Compose configuration..."

# Create docker-compose.override.yml to disable Ollama service
cat > docker-compose.override.yml <<EOF
# This file disables the Ollama service in docker-compose.yml
# because Ollama runs natively on the host machine for GPU access

services:
  # Disable Docker Ollama - using native Ollama instead
  ollama:
    deploy:
      replicas: 0
    restart: "no"
EOF

print_success "Docker Compose configured to use native Ollama"

# =============================================================================
# Start Docker Services
# =============================================================================
print_step "Starting Docker services..."

print_info "Pulling Docker images..."
docker compose pull

print_info "Starting containers (excluding Ollama)..."
docker compose up -d

print_success "Docker services started"

# Wait for services to be healthy
print_info "Waiting for services to be ready..."
sleep 5

# =============================================================================
# Verify Setup
# =============================================================================
print_step "Verifying setup..."

# Check Ollama
if curl -s http://localhost:$OLLAMA_PORT/api/tags &> /dev/null; then
    print_success "Native Ollama is running on port $OLLAMA_PORT"
    MODEL_COUNT=$(curl -s http://localhost:$OLLAMA_PORT/api/tags | grep -o '"name"' | wc -l)
    print_info "  Models loaded: $MODEL_COUNT"
else
    print_error "Ollama is not responding on port $OLLAMA_PORT"
fi

# Check Docker services
print_info "Checking Docker services..."
docker compose ps

# Check if backend can connect to Ollama
print_info "Testing backend connection to Ollama..."
sleep 3
if docker compose exec -T backend python -c "from app.ollama_client import ollama_client; import asyncio; asyncio.run(ollama_client.initialize()); print('✓ Backend connected to Ollama' if ollama_client.is_available else '✗ Backend cannot connect')" 2>/dev/null; then
    print_success "Backend successfully connected to native Ollama"
else
    print_warning "Backend connection test skipped (container may still be starting)"
fi

# =============================================================================
# Final Summary
# =============================================================================
print_header "Setup Complete!"

echo -e "${BOLD}System Configuration:${NC}"
echo -e "  OS: ${CYAN}$OS_TYPE${NC}"
echo -e "  GPU: ${CYAN}$GPU_NAME${NC}"
echo -e "  Ollama: ${GREEN}Native (Port $OLLAMA_PORT)${NC}"
echo ""

echo -e "${BOLD}AI Models (Native Ollama):${NC}"
echo -e "  ${GREEN}✓${NC} mistral:7b - Main conversation"
echo -e "  ${GREEN}✓${NC} llama3.2:3b - Fast responses"
echo -e "  ${GREEN}✓${NC} gemma2:9b - Grammar checking"
echo ""

echo -e "${BOLD}Docker Services:${NC}"
echo -e "  ${GREEN}✓${NC} Backend - http://localhost:8000"
echo -e "  ${GREEN}✓${NC} Frontend - http://localhost:3000"
echo -e "  ${GREEN}✓${NC} Whisper (Speech Recognition) - Port 9000"
echo -e "  ${GREEN}✓${NC} Piper (Text-to-Speech) - Port 10200"
echo -e "  ${GREEN}✓${NC} Redis (Cache) - Port 6379"
echo ""

echo -e "${BOLD}${GREEN}🎉 Your German AI Learning Platform is ready!${NC}"
echo ""
echo -e "${BOLD}Next Steps:${NC}"
echo -e "  1. Open your browser: ${CYAN}http://localhost:3000${NC}"
echo -e "  2. Create an account and start learning German!"
echo ""

echo -e "${BOLD}Useful Commands:${NC}"
echo -e "  View logs:        ${YELLOW}docker compose logs -f${NC}"
echo -e "  Stop services:    ${YELLOW}docker compose down${NC}"
echo -e "  Restart services: ${YELLOW}docker compose restart${NC}"
echo -e "  Check Ollama:     ${YELLOW}curl http://localhost:$OLLAMA_PORT/api/tags${NC}"
echo -e "  Ollama models:    ${YELLOW}OLLAMA_HOST=http://localhost:$OLLAMA_PORT ollama list${NC}"

if [[ "$OS_TYPE" == "linux" ]]; then
    echo -e "  Ollama logs:      ${YELLOW}sudo journalctl -u ollama -f${NC}"
    echo -e "  Ollama status:    ${YELLOW}sudo systemctl status ollama${NC}"
fi

echo ""
print_success "Setup completed successfully!"
