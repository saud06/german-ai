#!/bin/bash

# =============================================================================
# German AI Language Learning Platform - Linux Setup Script
# =============================================================================
# This script sets up the development environment on Linux with:
# - Native Ollama running on GPU (NVIDIA/AMD)
# - Docker containers for other services (Piper, Whisper, Redis, etc.)
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
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

# =============================================================================
# Step 1: Check System Requirements
# =============================================================================
print_header "Step 1: Checking System Requirements"

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This script is for Linux only. Detected OS: $OSTYPE"
    exit 1
fi
print_success "Running on Linux"

# Check for Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first:"
    echo "  Visit: https://docs.docker.com/engine/install/"
    exit 1
fi
print_success "Docker is installed ($(docker --version))"

# Check for Docker Compose
if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first:"
    echo "  Visit: https://docs.docker.com/compose/install/"
    exit 1
fi
print_success "Docker Compose is installed"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker first:"
    echo "  sudo systemctl start docker"
    exit 1
fi
print_success "Docker daemon is running"

# =============================================================================
# Step 2: Detect GPU
# =============================================================================
print_header "Step 2: Detecting GPU"

GPU_TYPE="none"
GPU_DETECTED=false

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi &> /dev/null; then
        GPU_TYPE="nvidia"
        GPU_DETECTED=true
        GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)
        print_success "NVIDIA GPU detected: $GPU_INFO"
    fi
fi

# Check for AMD GPU
if [ "$GPU_DETECTED" = false ]; then
    if lspci | grep -i "vga.*amd" &> /dev/null || lspci | grep -i "3d.*amd" &> /dev/null; then
        GPU_TYPE="amd"
        GPU_DETECTED=true
        GPU_INFO=$(lspci | grep -i "vga.*amd\|3d.*amd" | head -n 1 | cut -d: -f3)
        print_success "AMD GPU detected: $GPU_INFO"
    fi
fi

# Check for Intel GPU
if [ "$GPU_DETECTED" = false ]; then
    if lspci | grep -i "vga.*intel" &> /dev/null; then
        GPU_TYPE="intel"
        GPU_DETECTED=true
        GPU_INFO=$(lspci | grep -i "vga.*intel" | head -n 1 | cut -d: -f3)
        print_warning "Intel GPU detected: $GPU_INFO"
        print_warning "Intel GPUs have limited AI acceleration support"
    fi
fi

if [ "$GPU_DETECTED" = false ]; then
    print_warning "No GPU detected. Ollama will run on CPU (slower performance)"
    print_info "For best performance, install a GPU (NVIDIA recommended)"
fi

# =============================================================================
# Step 3: Install Ollama
# =============================================================================
print_header "Step 3: Installing Ollama (Native GPU)"

if command -v ollama &> /dev/null; then
    print_success "Ollama is already installed ($(ollama --version))"
else
    print_info "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama installed successfully"
    else
        print_error "Failed to install Ollama"
        exit 1
    fi
fi

# =============================================================================
# Step 4: Configure Ollama for GPU
# =============================================================================
print_header "Step 4: Configuring Ollama for GPU"

# Stop Ollama if running
if systemctl is-active --quiet ollama 2>/dev/null; then
    print_info "Stopping Ollama service..."
    sudo systemctl stop ollama
fi

# Create systemd service for Ollama on custom port
print_info "Creating Ollama systemd service on port 11435..."

sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
Environment="OLLAMA_HOST=0.0.0.0:11435"
Environment="OLLAMA_ORIGINS=*"
Environment="OLLAMA_KEEP_ALIVE=24h"
Environment="OLLAMA_NUM_PARALLEL=2"
Environment="OLLAMA_MAX_LOADED_MODELS=2"
User=$USER
Group=$USER
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

# Reload systemd and start Ollama
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

# Wait for Ollama to start
print_info "Waiting for Ollama to start..."
sleep 5

# Check if Ollama is running
if curl -s http://localhost:11435/ &> /dev/null; then
    print_success "Ollama is running on port 11435"
else
    print_error "Failed to start Ollama"
    print_info "Check logs with: sudo journalctl -u ollama -f"
    exit 1
fi

# =============================================================================
# Step 5: Pull AI Models
# =============================================================================
print_header "Step 5: Pulling AI Models"

print_info "This will download ~7GB of AI models. This may take 10-30 minutes..."
echo ""

# Pull Gemma 2 for grammar checking
print_info "Pulling Gemma 2:9b (for grammar checking)..."
OLLAMA_HOST=http://localhost:11435 ollama pull gemma2:9b
print_success "Gemma 2:9b downloaded"

# Pull Mistral for general AI
print_info "Pulling Mistral 7B (for general AI tasks)..."
OLLAMA_HOST=http://localhost:11435 ollama pull mistral:7b
print_success "Mistral 7B downloaded"

# Pull Llama 3.2 for fast responses
print_info "Pulling Llama 3.2:3b (for fast responses)..."
OLLAMA_HOST=http://localhost:11435 ollama pull llama3.2:3b
print_success "Llama 3.2:3b downloaded"

# Verify models
print_info "Verifying installed models..."
OLLAMA_HOST=http://localhost:11435 ollama list

# =============================================================================
# Step 6: Setup Environment File
# =============================================================================
print_header "Step 6: Setting Up Environment File"

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        print_info "Creating .env from .env.example..."
        cp .env.example .env
        
        # Update OLLAMA_HOST for Linux
        sed -i 's|OLLAMA_HOST=.*|OLLAMA_HOST=http://host.docker.internal:11435|g' .env
        
        # Update models
        sed -i 's|OLLAMA_MODEL=.*|OLLAMA_MODEL=mistral:7b|g' .env
        sed -i 's|OLLAMA_MODEL_FAST=.*|OLLAMA_MODEL_FAST=llama3.2:3b|g' .env
        sed -i 's|OLLAMA_MODEL_GRAMMAR=.*|OLLAMA_MODEL_GRAMMAR=gemma2:9b|g' .env
        
        print_success ".env file created"
        print_warning "Please update .env with your MongoDB URI and JWT_SECRET"
    else
        print_error ".env.example not found"
        exit 1
    fi
else
    print_success ".env file already exists"
fi

# =============================================================================
# Step 7: Start Docker Services
# =============================================================================
print_header "Step 7: Starting Docker Services"

print_info "Building and starting Docker containers..."
docker compose -f docker-compose.linux.yml up -d --build

# Wait for services to be healthy
print_info "Waiting for services to be ready..."
sleep 10

# Check service health
print_info "Checking service health..."

services=("backend" "frontend" "redis" "whisper" "piper")
all_healthy=true

for service in "${services[@]}"; do
    if docker ps --filter "name=german_$service" --filter "status=running" | grep -q "german_$service"; then
        print_success "$service is running"
    else
        print_error "$service is not running"
        all_healthy=false
    fi
done

# =============================================================================
# Step 8: Test GPU Usage
# =============================================================================
print_header "Step 8: Testing GPU Usage"

if [ "$GPU_TYPE" = "nvidia" ]; then
    print_info "Testing NVIDIA GPU usage with Ollama..."
    
    # Run a test query
    response=$(OLLAMA_HOST=http://localhost:11435 ollama run gemma2:9b "Say 'GPU test successful' in German" 2>&1 || true)
    
    if echo "$response" | grep -q "GPU"; then
        print_success "GPU is being used by Ollama"
    else
        print_warning "Unable to confirm GPU usage. Check with: nvidia-smi"
    fi
    
    # Show GPU usage
    print_info "Current GPU usage:"
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv
    
elif [ "$GPU_TYPE" = "amd" ]; then
    print_info "AMD GPU detected. Ollama should use ROCm if available"
    print_info "Check GPU usage with: rocm-smi"
    
else
    print_warning "No NVIDIA/AMD GPU. Ollama is running on CPU"
fi

# =============================================================================
# Final Summary
# =============================================================================
print_header "Setup Complete! 🎉"

echo -e "${GREEN}✓ Ollama is running natively on GPU (port 11435)${NC}"
echo -e "${GREEN}✓ Docker services are running${NC}"
echo -e "${GREEN}✓ AI models are downloaded and ready${NC}"
echo ""
echo -e "${BLUE}Access the application:${NC}"
echo -e "  Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "  Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo -e "  View logs:        ${YELLOW}docker compose -f docker-compose.linux.yml logs -f${NC}"
echo -e "  Stop services:    ${YELLOW}docker compose -f docker-compose.linux.yml down${NC}"
echo -e "  Restart backend:  ${YELLOW}docker compose -f docker-compose.linux.yml restart backend${NC}"
echo -e "  Check Ollama:     ${YELLOW}OLLAMA_HOST=http://localhost:11435 ollama list${NC}"
echo -e "  Ollama logs:      ${YELLOW}sudo journalctl -u ollama -f${NC}"

if [ "$GPU_TYPE" = "nvidia" ]; then
    echo -e "  GPU monitoring:   ${YELLOW}watch -n 1 nvidia-smi${NC}"
elif [ "$GPU_TYPE" = "amd" ]; then
    echo -e "  GPU monitoring:   ${YELLOW}watch -n 1 rocm-smi${NC}"
fi

echo ""
print_warning "Don't forget to update .env with your MongoDB URI and JWT_SECRET!"
echo ""
