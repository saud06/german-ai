#!/bin/bash

# GPU Performance Monitor for Apple Silicon
# Monitors Ollama GPU usage in real-time

echo "🔍 GPU Performance Monitor"
echo "=========================="
echo ""
echo "Monitoring Ollama GPU usage..."
echo "Press Ctrl+C to stop"
echo ""

# Check if asitop is installed
if command -v asitop &> /dev/null; then
    echo "Using asitop (best option)..."
    echo ""
    sudo asitop
else
    echo "⚠️  asitop not installed. Install with: pip3 install asitop"
    echo ""
    echo "Using powermetrics instead..."
    echo ""
    
    # Use powermetrics as fallback
    sudo powermetrics --samplers gpu_power,cpu_power -i 1000 -n 0 | while read line; do
        if [[ $line == *"GPU Power"* ]] || [[ $line == *"CPU Power"* ]] || [[ $line == *"GPU"* ]]; then
            echo "$line"
        fi
    done
fi
