#!/bin/bash
# Initialize Ollama with required models

set -e

echo "🤖 Initializing Ollama models..."

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama service..."
until docker compose exec ollama ollama list > /dev/null 2>&1; do
    echo "   Ollama not ready yet, waiting..."
    sleep 2
done

echo "✅ Ollama is ready!"

# Check and pull models
MODELS=("mistral:7b" "llama3.2:3b")

for MODEL in "${MODELS[@]}"; do
    echo ""
    echo "📥 Checking model: $MODEL"
    
    if docker compose exec ollama ollama list | grep -q "$MODEL"; then
        echo "   ✅ Model $MODEL already exists"
    else
        echo "   📥 Pulling model $MODEL (this may take several minutes)..."
        docker compose exec ollama ollama pull "$MODEL"
        echo "   ✅ Model $MODEL downloaded successfully"
    fi
done

echo ""
echo "🎉 All Ollama models are ready!"
echo ""
echo "Available models:"
docker compose exec ollama ollama list
