# Helper script to run backend on Windows
$ErrorActionPreference = "Stop"

# Ensure we operate from the script's own directory
Set-Location -Path $PSScriptRoot

# Create and activate virtual environment if not present
if (!(Test-Path ".venv")) {
    python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
