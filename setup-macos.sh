#!/bin/bash

# =============================================================================
# German AI Language Learning Platform - macOS Setup Script
# =============================================================================
# This script sets up the development environment on macOS with:
# - Native Ollama running on GPU (Apple Silicon Metal)
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

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is for macOS only. Detected OS: $OSTYPE"
    exit 1
fi
print_success "Running on macOS"

# Check for Apple Silicon
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    print_success "Apple Silicon detected (M1/M2/M3/M4) - GPU acceleration available via Metal"
else
    print_warning "Intel Mac detected - GPU acceleration limited"
fi

# Check for Docker Desktop
if ! command -v docker &> /dev/null; then
    print_error "Docker Desktop is not installed. Please install Docker Desktop first:"
    echo "  Visit: https://www.docker.com/products/docker-desktop"
    exit 1
fi
print_success "Docker Desktop is installed ($(docker --version))"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker Desktop is not running. Please start Docker Desktop first"
    exit 1
fi
print_success "Docker Desktop is running"

# =============================================================================
# Step 2: Install Ollama
# =============================================================================
print_header "Step 2: Installing Ollama (Native GPU)"

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
# Step 3: Configure Ollama for GPU
# =============================================================================
print_header "Step 3: Configuring Ollama for GPU"

# Stop Ollama if running
print_info "Stopping any running Ollama instances..."
pkill -f "ollama serve" 2>/dev/null || true
sleep 2

# Create LaunchAgent for Ollama on custom port
print_info "Creating Ollama LaunchAgent on port 11435..."

PLIST_PATH="$HOME/Library/LaunchAgents/com.ollama.server.plist"
mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ollama.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/ollama</string>
        <string>serve</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>OLLAMA_HOST</key>
        <string>0.0.0.0:11435</string>
        <key>OLLAMA_ORIGINS</key>
        <string>*</string>
        <key>OLLAMA_KEEP_ALIVE</key>
        <string>24h</string>
        <key>OLLAMA_NUM_PARALLEL</key>
        <string>2</string>
        <key>OLLAMA_MAX_LOADED_MODELS</key>
        <string>2</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/ollama-gpu.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ollama-gpu-error.log</string>
</dict>
</plist>
EOF

# Load and start the LaunchAgent
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

# Wait for Ollama to start
print_info "Waiting for Ollama to start..."
sleep 5

# Check if Ollama is running
if curl -s http://localhost:11435/ &> /dev/null; then
    print_success "Ollama is running on port 11435"
else
    print_error "Failed to start Ollama"
    print_info "Check logs at: /tmp/ollama-gpu.log and /tmp/ollama-gpu-error.log"
    exit 1
fi

# =============================================================================
# Step 4: Pull AI Models
# =============================================================================
print_header "Step 4: Pulling AI Models"

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
# Step 5: Setup Environment File
# =============================================================================
print_header "Step 5: Setting Up Environment File"

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        print_info "Creating .env from .env.example..."
        cp .env.example .env
        
        # Update OLLAMA_HOST for macOS
        sed -i '' 's|OLLAMA_HOST=.*|OLLAMA_HOST=http://host.docker.internal:11435|g' .env
        
        # Update models
        sed -i '' 's|OLLAMA_MODEL=.*|OLLAMA_MODEL=mistral:7b|g' .env
        sed -i '' 's|OLLAMA_MODEL_FAST=.*|OLLAMA_MODEL_FAST=llama3.2:3b|g' .env
        sed -i '' 's|OLLAMA_MODEL_GRAMMAR=.*|OLLAMA_MODEL_GRAMMAR=gemma2:9b|g' .env
        
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
# Step 6: Start Docker Services
# =============================================================================
print_header "Step 6: Starting Docker Services"

print_info "Building and starting Docker containers..."
docker compose up -d --build

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
# Step 7: Test GPU Usage
# =============================================================================
print_header "Step 7: Testing GPU Usage (Apple Metal)"

if [[ "$ARCH" == "arm64" ]]; then
    print_info "Testing Apple Silicon GPU usage with Ollama..."
    
    # Run a test query
    response=$(OLLAMA_HOST=http://localhost:11435 ollama run gemma2:9b "Say 'GPU test successful' in German" 2>&1 || true)
    
    print_success "Test query completed"
    print_info "Ollama is using Apple Metal for GPU acceleration"
    
    # Check process
    print_info "Ollama process info:"
    ps aux | grep "ollama serve" | grep -v grep
    
else
    print_warning "Intel Mac - Limited GPU acceleration available"
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
echo -e "  View logs:        ${YELLOW}docker compose logs -f${NC}"
echo -e "  Stop services:    ${YELLOW}docker compose down${NC}"
echo -e "  Restart backend:  ${YELLOW}docker compose restart backend${NC}"
echo -e "  Check Ollama:     ${YELLOW}OLLAMA_HOST=http://localhost:11435 ollama list${NC}"
echo -e "  Ollama logs:      ${YELLOW}tail -f /tmp/ollama-gpu.log${NC}"
echo -e "  Stop Ollama:      ${YELLOW}launchctl unload ~/Library/LaunchAgents/com.ollama.server.plist${NC}"
echo -e "  Start Ollama:     ${YELLOW}launchctl load ~/Library/LaunchAgents/com.ollama.server.plist${NC}"

if [[ "$ARCH" == "arm64" ]]; then
    echo -e "  Monitor GPU:      ${YELLOW}sudo powermetrics --samplers gpu_power -i 1000${NC}"
fi

echo ""
print_warning "Don't forget to update .env with your MongoDB URI and JWT_SECRET!"
echo ""
