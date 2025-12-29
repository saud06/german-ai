#!/bin/bash

# GPU Backend Setup Script for Apple Silicon
# This script sets up the native Ollama instance for GPU acceleration

echo "🚀 Setting up GPU Backend for Apple Silicon..."

# Check if running on Mac
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is for macOS only"
    exit 1
fi

# Check if Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "⚠️  Warning: Not running on Apple Silicon. GPU acceleration may not be available."
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    brew install ollama
else
    echo "✅ Ollama already installed"
fi

# Stop any existing Ollama services first
echo "🛑 Stopping existing Ollama services..."
launchctl unload ~/Library/LaunchAgents/com.ollama.gpu.plist 2>/dev/null || true
brew services stop ollama 2>/dev/null || true
killall ollama 2>/dev/null || true
sleep 2

# Check if Ollama is running on port 11435
if lsof -Pi :11435 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Ollama GPU backend already running on port 11435"
else
    echo "🚀 Starting Ollama GPU backend on port 11435..."
    
    # Detect Ollama path
    OLLAMA_PATH=$(which ollama)
    if [ -z "$OLLAMA_PATH" ]; then
        echo "❌ Ollama not found in PATH"
        exit 1
    fi
    echo "📍 Using Ollama at: $OLLAMA_PATH"
    
    # Create launchd plist for auto-start
    cat > ~/Library/LaunchAgents/com.ollama.gpu.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ollama.gpu</string>
    <key>ProgramArguments</key>
    <array>
        <string>$OLLAMA_PATH</string>
        <string>serve</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>OLLAMA_HOST</key>
        <string>0.0.0.0:11435</string>
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
    
    # Load the service
    launchctl load ~/Library/LaunchAgents/com.ollama.gpu.plist
    
    echo "⏳ Waiting for Ollama GPU backend to start..."
    
    # Wait up to 30 seconds for service to start
    for i in {1..30}; do
        if lsof -Pi :11435 -sTCP:LISTEN -t >/dev/null ; then
            echo "✅ Ollama GPU backend started successfully!"
            break
        fi
        sleep 1
        echo -n "."
    done
    echo ""
    
    # Check if it started
    if ! lsof -Pi :11435 -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Failed to start Ollama GPU backend"
        echo "📝 Check logs: tail -f /tmp/ollama-gpu-error.log"
        exit 1
    fi
fi

# Pull models
echo "📥 Pulling models..."
OLLAMA_HOST=http://localhost:11435 ollama pull llama3.2:1b
echo "✅ llama3.2:1b downloaded"

# Optional: Pull Mistral for better quality
read -p "📥 Download Mistral:7b for better quality? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    OLLAMA_HOST=http://localhost:11435 ollama pull mistral:7b
    echo "✅ mistral:7b downloaded"
fi

echo ""
echo "✅ GPU Backend Setup Complete!"
echo ""
echo "📊 Backend Status:"
echo "  - Docker (CPU):  http://localhost:8000  (Port 11434)"
echo "  - Native (GPU):  http://localhost:8001  (Port 11435)"
echo ""
echo "🎯 The backend will automatically use GPU when available!"
echo ""
echo "To stop GPU backend:"
echo "  launchctl unload ~/Library/LaunchAgents/com.ollama.gpu.plist"
echo ""
