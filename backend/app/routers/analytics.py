"""
Analytics and performance monitoring endpoints
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from ..db import get_db
from ..redis_client import redis_client
from ..ollama_client import ollama_client
import psutil
import time
import subprocess
import platform

router = APIRouter(prefix="/analytics")

class GPUMetrics(BaseModel):
    available: bool
    name: Optional[str] = None
    memory_used_mb: Optional[float] = None
    memory_total_mb: Optional[float] = None
    memory_percent: Optional[float] = None
    utilization_percent: Optional[float] = None
    temperature: Optional[float] = None

def get_gpu_metrics() -> Optional[GPUMetrics]:
    """
    Get GPU metrics for macOS (Metal) or NVIDIA GPUs
    """
    try:
        system = platform.system()
        
        if system == "Darwin":  # macOS
            # Try to get Metal GPU info
            try:
                # Get GPU info using system_profiler
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                if result.returncode == 0:
                    output = result.stdout
                    gpu_name = None
                    vram_mb = None
                    
                    # Parse GPU name
                    for line in output.split('\n'):
                        if 'Chipset Model:' in line:
                            gpu_name = line.split(':')[1].strip()
                        elif 'VRAM' in line or 'Metal' in line:
                            # Try to extract VRAM size
                            parts = line.split(':')
                            if len(parts) > 1:
                                vram_str = parts[1].strip()
                                if 'GB' in vram_str:
                                    try:
                                        vram_gb = float(vram_str.split()[0])
                                        vram_mb = vram_gb * 1024
                                    except:
                                        pass
                    
                    # For macOS, we can't easily get real-time GPU utilization
                    # But we can provide basic info
                    return GPUMetrics(
                        available=True,
                        name=gpu_name or "Apple GPU",
                        memory_total_mb=vram_mb,
                        memory_used_mb=None,  # Not available on macOS without additional tools
                        memory_percent=None,
                        utilization_percent=None,  # Not easily available on macOS
                        temperature=None
                    )
            except Exception as e:
                print(f"macOS GPU detection error: {e}")
                return GPUMetrics(available=False)
        
        else:  # Linux/Windows - try nvidia-smi
            try:
                result = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu",
                        "--format=csv,noheader,nounits"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                if result.returncode == 0:
                    parts = result.stdout.strip().split(',')
                    if len(parts) >= 5:
                        name = parts[0].strip()
                        memory_used = float(parts[1].strip())
                        memory_total = float(parts[2].strip())
                        utilization = float(parts[3].strip())
                        temperature = float(parts[4].strip())
                        
                        return GPUMetrics(
                            available=True,
                            name=name,
                            memory_used_mb=memory_used,
                            memory_total_mb=memory_total,
                            memory_percent=round((memory_used / memory_total) * 100, 1),
                            utilization_percent=utilization,
                            temperature=temperature
                        )
            except Exception as e:
                print(f"NVIDIA GPU detection error: {e}")
                return GPUMetrics(available=False)
        
        return GPUMetrics(available=False)
    
    except Exception as e:
        print(f"GPU metrics error: {e}")
        return GPUMetrics(available=False)

class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    memory_available_gb: float
    disk_percent: float
    uptime_seconds: float
    gpu: Optional[GPUMetrics] = None

class AIMetrics(BaseModel):
    model: str
    is_available: bool
    total_requests: int
    avg_response_time: float
    cache_hit_rate: float

class UsageStats(BaseModel):
    total_users: int
    active_users_24h: int
    total_scenarios: int
    active_conversations: int
    total_quizzes_taken: int
    total_grammar_checks: int

class PerformanceMetrics(BaseModel):
    system: SystemMetrics
    ai: AIMetrics
    usage: UsageStats
    timestamp: str

@router.get('/metrics', response_model=PerformanceMetrics)
async def get_metrics(db=Depends(get_db)):
    """
    Get comprehensive system, AI, and usage metrics
    """
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime = time.time() - psutil.boot_time()
    
    # Get GPU metrics
    gpu_metrics = get_gpu_metrics()
    
    system_metrics = SystemMetrics(
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        memory_used_gb=round(memory.used / (1024**3), 2),
        memory_total_gb=round(memory.total / (1024**3), 2),
        memory_available_gb=round(memory.available / (1024**3), 2),
        disk_percent=disk.percent,
        uptime_seconds=uptime,
        gpu=gpu_metrics
    )
    
    # AI metrics
    total_requests = await redis_client.get("ai:total_requests") or 0
    total_time = await redis_client.get("ai:total_time") or 0
    cache_hits = await redis_client.get("ai:cache_hits") or 0
    
    avg_response_time = float(total_time) / max(int(total_requests), 1)
    cache_hit_rate = float(cache_hits) / max(int(total_requests), 1) * 100
    
    ai_metrics = AIMetrics(
        model=ollama_client.model,
        is_available=ollama_client.is_available,
        total_requests=int(total_requests),
        avg_response_time=round(avg_response_time, 2),
        cache_hit_rate=round(cache_hit_rate, 2)
    )
    
    # Usage stats
    total_users = await db["users"].count_documents({})
    
    # Active users in last 24h (based on conversation activity)
    yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
    active_users = await db["conversation_states"].distinct(
        "user_id",
        {"updated_at": {"$gte": yesterday.isoformat()}}
    )
    
    total_scenarios = await db["scenarios"].count_documents({})
    active_conversations = await db["conversation_states"].count_documents(
        {"status": "active"}
    )
    
    total_quizzes = await db["quiz_sessions"].count_documents({})
    total_grammar = await db["grammar_history"].count_documents({})
    
    usage_stats = UsageStats(
        total_users=total_users,
        active_users_24h=len(active_users),
        total_scenarios=total_scenarios,
        active_conversations=active_conversations,
        total_quizzes_taken=total_quizzes,
        total_grammar_checks=total_grammar
    )
    
    return PerformanceMetrics(
        system=system_metrics,
        ai=ai_metrics,
        usage=usage_stats,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

class AIUsageLog(BaseModel):
    feature: str
    response_time: float
    success: bool
    timestamp: str

@router.post('/log-ai-usage')
async def log_ai_usage(log: AIUsageLog):
    """
    Log AI usage for analytics
    """
    # Increment counters
    await redis_client.incr("ai:total_requests")
    await redis_client.incr(f"ai:{log.feature}:requests")
    
    if log.success:
        # Track response time
        current_total = await redis_client.get("ai:total_time") or 0
        await redis_client.set("ai:total_time", float(current_total) + log.response_time)
        
        # Track per-feature metrics
        await redis_client.incr(f"ai:{log.feature}:success")
        feature_time = await redis_client.get(f"ai:{log.feature}:time") or 0
        await redis_client.set(f"ai:{log.feature}:time", float(feature_time) + log.response_time)
    
    return {"status": "logged"}

class FeatureStats(BaseModel):
    feature: str
    total_requests: int
    success_count: int
    avg_response_time: float
    success_rate: float

@router.get('/ai-features', response_model=List[FeatureStats])
async def get_ai_feature_stats():
    """
    Get per-feature AI statistics
    """
    features = ["grammar", "quiz", "voice", "scenario"]
    stats = []
    
    for feature in features:
        requests = await redis_client.get(f"ai:{feature}:requests") or 0
        success = await redis_client.get(f"ai:{feature}:success") or 0
        total_time = await redis_client.get(f"ai:{feature}:time") or 0
        
        requests = int(requests)
        success = int(success)
        total_time = float(total_time)
        
        avg_time = total_time / max(success, 1)
        success_rate = (success / max(requests, 1)) * 100
        
        stats.append(FeatureStats(
            feature=feature,
            total_requests=requests,
            success_count=success,
            avg_response_time=round(avg_time, 2),
            success_rate=round(success_rate, 2)
        ))
    
    return stats

class HealthCheck(BaseModel):
    status: str
    services: Dict[str, bool]
    timestamp: str

@router.get('/health', response_model=HealthCheck)
async def health_check(db=Depends(get_db)):
    """
    Comprehensive health check for all services
    """
    services = {}
    
    # Check database
    try:
        await db.command("ping")
        services["database"] = True
    except:
        services["database"] = False
    
    # Check Redis
    try:
        await redis_client.ping()
        services["redis"] = True
    except:
        services["redis"] = False
    
    # Check Ollama
    services["ollama"] = ollama_client.is_available
    
    # Overall status
    all_healthy = all(services.values())
    status = "healthy" if all_healthy else "degraded"
    
    return HealthCheck(
        status=status,
        services=services,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

class TopUser(BaseModel):
    user_id: str
    email: Optional[str]
    activity_count: int
    last_active: str

@router.get('/top-users', response_model=List[TopUser])
async def get_top_users(limit: int = 10, db=Depends(get_db)):
    """
    Get most active users
    """
    # Aggregate user activity from conversation_states
    pipeline = [
        {"$group": {
            "_id": "$user_id",
            "count": {"$sum": 1},
            "last_active": {"$max": "$updated_at"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    
    results = await db["conversation_states"].aggregate(pipeline).to_list(length=limit)
    
    top_users = []
    for result in results:
        user_id = result["_id"]
        
        # Get user email
        user = await db["users"].find_one({"_id": user_id})
        email = user.get("email") if user else None
        
        top_users.append(TopUser(
            user_id=user_id,
            email=email,
            activity_count=result["count"],
            last_active=result.get("last_active", "")
        ))
    
    return top_users

class PopularScenario(BaseModel):
    scenario_id: str
    name: str
    start_count: int
    completion_rate: float

@router.get('/popular-scenarios', response_model=List[PopularScenario])
async def get_popular_scenarios(limit: int = 10, db=Depends(get_db)):
    """
    Get most popular scenarios
    """
    # Count scenario starts
    pipeline = [
        {"$group": {
            "_id": "$scenario_id",
            "starts": {"$sum": 1},
            "completions": {
                "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
            }
        }},
        {"$sort": {"starts": -1}},
        {"$limit": limit}
    ]
    
    results = await db["conversation_states"].aggregate(pipeline).to_list(length=limit)
    
    popular = []
    for result in results:
        scenario_id = result["_id"]
        
        # Get scenario name
        scenario = await db["scenarios"].find_one({"_id": scenario_id})
        name = scenario.get("name") if scenario else "Unknown"
        
        starts = result["starts"]
        completions = result["completions"]
        completion_rate = (completions / max(starts, 1)) * 100
        
        popular.append(PopularScenario(
            scenario_id=scenario_id,
            name=name,
            start_count=starts,
            completion_rate=round(completion_rate, 2)
        ))
    
    return popular


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    name: str
    total_xp: int
    level: int
    current_streak: int
    scenarios_completed: int
    words_learned: int

@router.get('/leaderboard', response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 10, db=Depends(get_db)):
    """
    Get top users leaderboard by XP
    """
    # Get top users by XP
    user_stats = await db["user_stats"].find().sort("total_xp", -1).limit(limit).to_list(length=limit)
    
    leaderboard = []
    for idx, stats in enumerate(user_stats, 1):
        user_id = stats.get("user_id")
        
        # Get user name
        user = await db["users"].find_one({"_id": user_id})
        name = user.get("name") if user else "Anonymous"
        
        leaderboard.append(LeaderboardEntry(
            rank=idx,
            user_id=user_id,
            name=name,
            total_xp=stats.get("total_xp", 0),
            level=stats.get("level", 1),
            current_streak=stats.get("current_streak", 0),
            scenarios_completed=stats.get("scenarios_completed", 0),
            words_learned=stats.get("words_learned", 0)
        ))
    
    return leaderboard
