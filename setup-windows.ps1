# =============================================================================
# German AI Language Learning Platform - Windows Setup Script
# =============================================================================
# This script sets up the development environment on Windows with:
# - Native Ollama running on GPU (NVIDIA/AMD)
# - Docker containers for other services (Piper, Whisper, Redis, etc.)
# =============================================================================

# Requires PowerShell 5.1 or higher
#Requires -Version 5.1

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
function Write-Header {
    param([string]$Message)
    Write-Host "`n=================================================================" -ForegroundColor Blue
    Write-Host "  $Message" -ForegroundColor Blue
    Write-Host "=================================================================`n" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

# =============================================================================
# Step 1: Check System Requirements
# =============================================================================
Write-Header "Step 1: Checking System Requirements"

# Check if running on Windows
if ($PSVersionTable.Platform -and $PSVersionTable.Platform -ne "Win32NT") {
    Write-Error-Custom "This script is for Windows only"
    exit 1
}
Write-Success "Running on Windows"

# Check for Docker Desktop
$dockerPath = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerPath) {
    Write-Error-Custom "Docker Desktop is not installed. Please install Docker Desktop first:"
    Write-Host "  Visit: https://www.docker.com/products/docker-desktop"
    exit 1
}
Write-Success "Docker Desktop is installed ($((docker --version)))"

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Success "Docker Desktop is running"
} catch {
    Write-Error-Custom "Docker Desktop is not running. Please start Docker Desktop first"
    exit 1
}

# Check for WSL2 (recommended for Docker Desktop)
$wslVersion = wsl --status 2>&1 | Select-String "Default Version: 2"
if ($wslVersion) {
    Write-Success "WSL2 is enabled (recommended for Docker)"
} else {
    Write-Warning-Custom "WSL2 is not detected. Docker Desktop works better with WSL2"
    Write-Info "To enable WSL2, run: wsl --set-default-version 2"
}

# =============================================================================
# Step 2: Detect GPU
# =============================================================================
Write-Header "Step 2: Detecting GPU"

$gpuDetected = $false
$gpuType = "none"
$gpuInfo = ""

# Check for NVIDIA GPU
try {
    $nvidiaGpu = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -like "*NVIDIA*" }
    if ($nvidiaGpu) {
        $gpuType = "nvidia"
        $gpuDetected = $true
        $gpuInfo = $nvidiaGpu.Name
        Write-Success "NVIDIA GPU detected: $gpuInfo"
        
        # Check for nvidia-smi
        $nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
        if ($nvidiaSmi) {
            Write-Success "NVIDIA drivers are installed"
        } else {
            Write-Warning-Custom "NVIDIA drivers may not be installed correctly"
            Write-Info "Download drivers from: https://www.nvidia.com/Download/index.aspx"
        }
    }
} catch {
    # NVIDIA GPU not found
}

# Check for AMD GPU
if (-not $gpuDetected) {
    try {
        $amdGpu = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -like "*AMD*" -or $_.Name -like "*Radeon*" }
        if ($amdGpu) {
            $gpuType = "amd"
            $gpuDetected = $true
            $gpuInfo = $amdGpu.Name
            Write-Success "AMD GPU detected: $gpuInfo"
            Write-Warning-Custom "AMD GPU support on Windows is experimental"
        }
    } catch {
        # AMD GPU not found
    }
}

# Check for Intel GPU
if (-not $gpuDetected) {
    try {
        $intelGpu = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -like "*Intel*" }
        if ($intelGpu) {
            $gpuType = "intel"
            $gpuDetected = $true
            $gpuInfo = $intelGpu.Name
            Write-Warning-Custom "Intel GPU detected: $gpuInfo"
            Write-Warning-Custom "Intel GPUs have limited AI acceleration support"
        }
    } catch {
        # Intel GPU not found
    }
}

if (-not $gpuDetected) {
    Write-Warning-Custom "No GPU detected. Ollama will run on CPU (slower performance)"
    Write-Info "For best performance, install a GPU (NVIDIA recommended)"
}

# =============================================================================
# Step 3: Install Ollama
# =============================================================================
Write-Header "Step 3: Installing Ollama (Native GPU)"

$ollamaPath = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollamaPath) {
    Write-Success "Ollama is already installed"
} else {
    Write-Info "Downloading Ollama installer..."
    
    $installerPath = "$env:TEMP\OllamaSetup.exe"
    $downloadUrl = "https://ollama.com/download/OllamaSetup.exe"
    
    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath
        Write-Success "Ollama installer downloaded"
        
        Write-Info "Installing Ollama... (This may take a few minutes)"
        Start-Process -FilePath $installerPath -Wait
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        $ollamaPath = Get-Command ollama -ErrorAction SilentlyContinue
        if ($ollamaPath) {
            Write-Success "Ollama installed successfully"
        } else {
            Write-Error-Custom "Failed to install Ollama. Please install manually from https://ollama.com"
            exit 1
        }
    } catch {
        Write-Error-Custom "Failed to download Ollama: $_"
        Write-Info "Please download and install manually from: https://ollama.com/download"
        exit 1
    }
}

# =============================================================================
# Step 4: Configure Ollama for GPU
# =============================================================================
Write-Header "Step 4: Configuring Ollama for GPU"

# Set Ollama environment variables for Windows
Write-Info "Configuring Ollama environment variables..."

# Set user environment variables
[System.Environment]::SetEnvironmentVariable("OLLAMA_HOST", "127.0.0.1:11435", "User")
[System.Environment]::SetEnvironmentVariable("OLLAMA_ORIGINS", "*", "User")
[System.Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "24h", "User")
[System.Environment]::SetEnvironmentVariable("OLLAMA_NUM_PARALLEL", "2", "User")
[System.Environment]::SetEnvironmentVariable("OLLAMA_MAX_LOADED_MODELS", "2", "User")

# Refresh environment variables in current session
$env:OLLAMA_HOST = "127.0.0.1:11435"
$env:OLLAMA_ORIGINS = "*"
$env:OLLAMA_KEEP_ALIVE = "24h"
$env:OLLAMA_NUM_PARALLEL = "2"
$env:OLLAMA_MAX_LOADED_MODELS = "2"

Write-Success "Ollama environment variables configured"

# Stop Ollama if running
Write-Info "Restarting Ollama service..."
try {
    Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
} catch {
    # Process not running
}

# Start Ollama service
Write-Info "Starting Ollama on port 11435..."
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

# Wait for Ollama to start
Write-Info "Waiting for Ollama to start..."
Start-Sleep -Seconds 5

# Check if Ollama is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11435/" -UseBasicParsing -TimeoutSec 5
    Write-Success "Ollama is running on port 11435"
} catch {
    Write-Error-Custom "Failed to start Ollama on port 11435"
    Write-Info "Try running manually: ollama serve"
    exit 1
}

# =============================================================================
# Step 5: Pull AI Models
# =============================================================================
Write-Header "Step 5: Pulling AI Models"

Write-Info "This will download ~7GB of AI models. This may take 10-30 minutes..."
Write-Host ""

# Pull Gemma 2 for grammar checking
Write-Info "Pulling Gemma 2:9b (for grammar checking)..."
$env:OLLAMA_HOST = "http://localhost:11435"
ollama pull gemma2:9b
Write-Success "Gemma 2:9b downloaded"

# Pull Mistral for general AI
Write-Info "Pulling Mistral 7B (for general AI tasks)..."
ollama pull mistral:7b
Write-Success "Mistral 7B downloaded"

# Pull Llama 3.2 for fast responses
Write-Info "Pulling Llama 3.2:3b (for fast responses)..."
ollama pull llama3.2:3b
Write-Success "Llama 3.2:3b downloaded"

# Verify models
Write-Info "Verifying installed models..."
ollama list

# =============================================================================
# Step 6: Setup Environment File
# =============================================================================
Write-Header "Step 6: Setting Up Environment File"

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Info "Creating .env from .env.example..."
        Copy-Item ".env.example" ".env"
        
        # Update .env for Windows
        $envContent = Get-Content ".env"
        $envContent = $envContent -replace "OLLAMA_HOST=.*", "OLLAMA_HOST=http://host.docker.internal:11435"
        $envContent = $envContent -replace "OLLAMA_MODEL=.*", "OLLAMA_MODEL=mistral:7b"
        $envContent = $envContent -replace "OLLAMA_MODEL_FAST=.*", "OLLAMA_MODEL_FAST=llama3.2:3b"
        $envContent = $envContent -replace "OLLAMA_MODEL_GRAMMAR=.*", "OLLAMA_MODEL_GRAMMAR=gemma2:9b"
        $envContent | Set-Content ".env"
        
        Write-Success ".env file created"
        Write-Warning-Custom "Please update .env with your MongoDB URI and JWT_SECRET"
    } else {
        Write-Error-Custom ".env.example not found"
        exit 1
    }
} else {
    Write-Success ".env file already exists"
}

# =============================================================================
# Step 7: Start Docker Services
# =============================================================================
Write-Header "Step 7: Starting Docker Services"

Write-Info "Building and starting Docker containers..."
docker compose -f docker-compose.windows.yml up -d --build

# Wait for services to be healthy
Write-Info "Waiting for services to be ready..."
Start-Sleep -Seconds 10

# Check service health
Write-Info "Checking service health..."

$services = @("backend", "frontend", "redis", "whisper", "piper")
$allHealthy = $true

foreach ($service in $services) {
    $containerName = "german_$service"
    $container = docker ps --filter "name=$containerName" --filter "status=running" --format "{{.Names}}"
    
    if ($container -eq $containerName) {
        Write-Success "$service is running"
    } else {
        Write-Error-Custom "$service is not running"
        $allHealthy = $false
    }
}

# =============================================================================
# Step 8: Test GPU Usage
# =============================================================================
Write-Header "Step 8: Testing GPU Usage"

if ($gpuType -eq "nvidia") {
    Write-Info "Testing NVIDIA GPU usage with Ollama..."
    
    # Run a test query
    $env:OLLAMA_HOST = "http://localhost:11435"
    $response = ollama run gemma2:9b "Say 'GPU test successful' in German" 2>&1
    
    Write-Success "Test query completed"
    
    # Check GPU usage with nvidia-smi
    $nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if ($nvidiaSmi) {
        Write-Info "Current GPU usage:"
        nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv
    }
    
} elseif ($gpuType -eq "amd") {
    Write-Info "AMD GPU detected. Ollama should use ROCm if available"
    Write-Warning-Custom "AMD GPU support on Windows is experimental"
    
} else {
    Write-Warning-Custom "No NVIDIA/AMD GPU. Ollama is running on CPU"
}

# =============================================================================
# Final Summary
# =============================================================================
Write-Header "Setup Complete! 🎉"

Write-Host "✓ Ollama is running natively on GPU (port 11435)" -ForegroundColor Green
Write-Host "✓ Docker services are running" -ForegroundColor Green
Write-Host "✓ AI models are downloaded and ready" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Blue
Write-Host "  Frontend:  " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor Green
Write-Host "  Backend:   " -NoNewline; Write-Host "http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs:  " -NoNewline; Write-Host "http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Blue
Write-Host "  View logs:        " -NoNewline; Write-Host "docker compose -f docker-compose.windows.yml logs -f" -ForegroundColor Yellow
Write-Host "  Stop services:    " -NoNewline; Write-Host "docker compose -f docker-compose.windows.yml down" -ForegroundColor Yellow
Write-Host "  Restart backend:  " -NoNewline; Write-Host "docker compose -f docker-compose.windows.yml restart backend" -ForegroundColor Yellow
Write-Host "  Check Ollama:     " -NoNewline; Write-Host "`$env:OLLAMA_HOST='http://localhost:11435'; ollama list" -ForegroundColor Yellow

if ($gpuType -eq "nvidia") {
    Write-Host "  GPU monitoring:   " -NoNewline; Write-Host "nvidia-smi -l 1" -ForegroundColor Yellow
}

Write-Host ""
Write-Warning-Custom "Don't forget to update .env with your MongoDB URI and JWT_SECRET!"
Write-Host ""
