"""
Environment detection for automatic backend selection
"""
import os
import socket
import platform
from typing import Literal

def detect_environment() -> Literal["local_gpu", "docker"]:
    """
    Detect if running locally (with GPU) or in Docker
    
    Returns:
        "local_gpu": Running natively on Mac with GPU available
        "docker": Running in Docker container
    """
    # Check if running in Docker
    if os.path.exists('/.dockerenv'):
        return "docker"
    
    # Check if Docker hostname
    hostname = socket.gethostname()
    if hostname.startswith('docker-') or 'container' in hostname.lower():
        return "docker"
    
    # Check for Mac with Apple Silicon
    if platform.system() == 'Darwin' and platform.machine() == 'arm64':
        # Check if native Ollama is available on port 11435 (GPU backend)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 11435))
            sock.close()
            if result == 0:
                return "local_gpu"
        except:
            pass
    
    # Default to docker
    return "docker"

def get_ollama_host() -> str:
    """
    Get the appropriate Ollama host based on environment
    
    Returns:
        Ollama host URL
    """
    env = detect_environment()
    
    if env == "local_gpu":
        # Use native Ollama on port 11435 (GPU)
        return "http://localhost:11435"
    else:
        # Use Docker Ollama on port 11434
        return os.getenv("OLLAMA_HOST", "http://ollama:11434")

def is_gpu_available() -> bool:
    """Check if GPU backend is available"""
    return detect_environment() == "local_gpu"

def get_backend_info() -> dict:
    """Get backend information for logging"""
    env = detect_environment()
    return {
        "environment": env,
        "ollama_host": get_ollama_host(),
        "gpu_available": is_gpu_available(),
        "platform": platform.system(),
        "machine": platform.machine()
    }
