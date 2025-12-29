"""
Debug endpoints for testing environment detection
"""
from fastapi import APIRouter
from ..environment import get_backend_info

router = APIRouter(tags=["debug"])

@router.get("/debug/backend-info")
async def get_backend_environment():
    """Get backend environment information"""
    return get_backend_info()
