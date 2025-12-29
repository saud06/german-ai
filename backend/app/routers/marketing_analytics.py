"""
Marketing Analytics Router
Track conversions, A/B tests, and marketing metrics
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..db import get_db
from .auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/marketing", tags=["Marketing Analytics"])


class ConversionEvent(BaseModel):
    """Conversion event model"""
    event_type: str  # signup, trial_start, subscription, referral
    user_id: Optional[str] = None
    source: Optional[str] = None  # google, facebook, referral, direct
    campaign: Optional[str] = None
    metadata: Dict[str, Any] = {}


class ABTest(BaseModel):
    """A/B test model"""
    name: str
    variant_a: str
    variant_b: str
    metric: str  # conversion_rate, retention_rate, revenue
    start_date: datetime
    end_date: Optional[datetime] = None


# Conversion Tracking

@router.post("/track")
async def track_conversion(
    event: ConversionEvent,
    db=Depends(get_db)
):
    """Track a conversion event"""
    event_doc = {
        "event_type": event.event_type,
        "user_id": event.user_id,
        "source": event.source,
        "campaign": event.campaign,
        "metadata": event.metadata,
        "created_at": datetime.utcnow()
    }
    
    await db["conversion_events"].insert_one(event_doc)
    
    return {"message": "Event tracked successfully"}


@router.get("/conversions")
async def get_conversion_metrics(
    days: int = 30,
    db=Depends(get_db)
):
    """Get conversion metrics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total signups
    signups = await db["conversion_events"].count_documents({
        "event_type": "signup",
        "created_at": {"$gte": start_date}
    })
    
    # Trial starts
    trials = await db["conversion_events"].count_documents({
        "event_type": "trial_start",
        "created_at": {"$gte": start_date}
    })
    
    # Subscriptions
    subscriptions = await db["conversion_events"].count_documents({
        "event_type": "subscription",
        "created_at": {"$gte": start_date}
    })
    
    # Referrals
    referrals = await db["conversion_events"].count_documents({
        "event_type": "referral",
        "created_at": {"$gte": start_date}
    })
    
    # Calculate conversion rates
    signup_to_trial = (trials / signups * 100) if signups > 0 else 0
    trial_to_paid = (subscriptions / trials * 100) if trials > 0 else 0
    signup_to_paid = (subscriptions / signups * 100) if signups > 0 else 0
    
    return {
        "period_days": days,
        "signups": signups,
        "trials": trials,
        "subscriptions": subscriptions,
        "referrals": referrals,
        "conversion_rates": {
            "signup_to_trial": round(signup_to_trial, 2),
            "trial_to_paid": round(trial_to_paid, 2),
            "signup_to_paid": round(signup_to_paid, 2)
        }
    }


@router.get("/conversions/by-source")
async def get_conversions_by_source(
    days: int = 30,
    db=Depends(get_db)
):
    """Get conversions grouped by source"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {
            "$match": {
                "created_at": {"$gte": start_date},
                "source": {"$ne": None}
            }
        },
        {
            "$group": {
                "_id": {
                    "source": "$source",
                    "event_type": "$event_type"
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}}
    ]
    
    results = await db["conversion_events"].aggregate(pipeline).to_list(length=1000)
    
    # Organize by source
    by_source = {}
    for result in results:
        source = result["_id"]["source"]
        event_type = result["_id"]["event_type"]
        
        if source not in by_source:
            by_source[source] = {
                "signups": 0,
                "trials": 0,
                "subscriptions": 0,
                "referrals": 0
            }
        
        by_source[source][f"{event_type}s"] = result["count"]
    
    return {
        "period_days": days,
        "by_source": by_source
    }


@router.get("/conversions/funnel")
async def get_conversion_funnel(
    days: int = 30,
    db=Depends(get_db)
):
    """Get conversion funnel data"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get unique users at each stage
    signups = await db["conversion_events"].distinct(
        "user_id",
        {
            "event_type": "signup",
            "created_at": {"$gte": start_date}
        }
    )
    
    trials = await db["conversion_events"].distinct(
        "user_id",
        {
            "event_type": "trial_start",
            "created_at": {"$gte": start_date}
        }
    )
    
    subscriptions = await db["conversion_events"].distinct(
        "user_id",
        {
            "event_type": "subscription",
            "created_at": {"$gte": start_date}
        }
    )
    
    return {
        "period_days": days,
        "funnel": [
            {
                "stage": "Signup",
                "users": len(signups),
                "percentage": 100
            },
            {
                "stage": "Trial",
                "users": len(trials),
                "percentage": round(len(trials) / len(signups) * 100, 2) if signups else 0
            },
            {
                "stage": "Paid",
                "users": len(subscriptions),
                "percentage": round(len(subscriptions) / len(signups) * 100, 2) if signups else 0
            }
        ]
    }


# A/B Testing

@router.post("/ab-test")
async def create_ab_test(
    test: ABTest,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Create a new A/B test"""
    test_doc = {
        "name": test.name,
        "variant_a": test.variant_a,
        "variant_b": test.variant_b,
        "metric": test.metric,
        "start_date": test.start_date,
        "end_date": test.end_date,
        "created_by": user_id,
        "created_at": datetime.utcnow(),
        "active": True
    }
    
    result = await db["ab_tests"].insert_one(test_doc)
    
    return {
        "test_id": str(result.inserted_id),
        "message": "A/B test created successfully"
    }


@router.get("/ab-test/{test_id}/results")
async def get_ab_test_results(
    test_id: str,
    db=Depends(get_db)
):
    """Get A/B test results"""
    test = await db["ab_tests"].find_one({"_id": test_id})
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )
    
    # Get variant assignments
    variant_a_users = await db["ab_test_assignments"].count_documents({
        "test_id": test_id,
        "variant": "a"
    })
    
    variant_b_users = await db["ab_test_assignments"].count_documents({
        "test_id": test_id,
        "variant": "b"
    })
    
    # Get conversion counts (simplified)
    variant_a_conversions = await db["ab_test_conversions"].count_documents({
        "test_id": test_id,
        "variant": "a"
    })
    
    variant_b_conversions = await db["ab_test_conversions"].count_documents({
        "test_id": test_id,
        "variant": "b"
    })
    
    # Calculate conversion rates
    variant_a_rate = (variant_a_conversions / variant_a_users * 100) if variant_a_users > 0 else 0
    variant_b_rate = (variant_b_conversions / variant_b_users * 100) if variant_b_users > 0 else 0
    
    # Determine winner
    winner = None
    if variant_a_rate > variant_b_rate:
        winner = "a"
        improvement = ((variant_a_rate - variant_b_rate) / variant_b_rate * 100) if variant_b_rate > 0 else 0
    elif variant_b_rate > variant_a_rate:
        winner = "b"
        improvement = ((variant_b_rate - variant_a_rate) / variant_a_rate * 100) if variant_a_rate > 0 else 0
    else:
        improvement = 0
    
    return {
        "test_name": test["name"],
        "metric": test["metric"],
        "variant_a": {
            "name": test["variant_a"],
            "users": variant_a_users,
            "conversions": variant_a_conversions,
            "conversion_rate": round(variant_a_rate, 2)
        },
        "variant_b": {
            "name": test["variant_b"],
            "users": variant_b_users,
            "conversions": variant_b_conversions,
            "conversion_rate": round(variant_b_rate, 2)
        },
        "winner": winner,
        "improvement": round(improvement, 2) if winner else 0
    }


# Revenue Analytics

@router.get("/revenue")
async def get_revenue_metrics(
    days: int = 30,
    db=Depends(get_db)
):
    """Get revenue metrics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get paid invoices
    pipeline = [
        {
            "$match": {
                "status": "paid",
                "created_at": {"$gte": start_date}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_revenue": {"$sum": "$amount"},
                "invoice_count": {"$sum": 1}
            }
        }
    ]
    
    result = await db["invoices"].aggregate(pipeline).to_list(length=1)
    
    total_revenue = result[0]["total_revenue"] / 100 if result else 0  # Convert from cents
    invoice_count = result[0]["invoice_count"] if result else 0
    
    # Get active subscriptions
    active_subs = await db["subscriptions"].count_documents({
        "status": "active",
        "tier": {"$ne": "free"}
    })
    
    # Calculate MRR (Monthly Recurring Revenue)
    # Simplified: assume $9.99 for premium, $19.99 for plus
    premium_count = await db["subscriptions"].count_documents({
        "status": "active",
        "tier": "premium"
    })
    
    plus_count = await db["subscriptions"].count_documents({
        "status": "active",
        "tier": "plus"
    })
    
    mrr = (premium_count * 9.99) + (plus_count * 19.99)
    
    return {
        "period_days": days,
        "total_revenue": round(total_revenue, 2),
        "invoice_count": invoice_count,
        "average_invoice": round(total_revenue / invoice_count, 2) if invoice_count > 0 else 0,
        "active_subscriptions": active_subs,
        "mrr": round(mrr, 2),
        "arr": round(mrr * 12, 2)
    }


@router.get("/retention")
async def get_retention_metrics(
    db=Depends(get_db)
):
    """Get retention metrics"""
    # Get users who signed up 30+ days ago
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    old_users = await db["users"].count_documents({
        "created_at": {"$lt": thirty_days_ago}
    })
    
    # Get active users from that cohort
    active_old_users = await db["users"].count_documents({
        "created_at": {"$lt": thirty_days_ago},
        "last_active": {"$gte": datetime.utcnow() - timedelta(days=7)}
    })
    
    # Calculate retention rate
    retention_rate = (active_old_users / old_users * 100) if old_users > 0 else 0
    
    # Get churn rate (canceled subscriptions)
    total_subs = await db["subscriptions"].count_documents({
        "tier": {"$ne": "free"}
    })
    
    churned_subs = await db["subscriptions"].count_documents({
        "status": "canceled",
        "updated_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
    })
    
    churn_rate = (churned_subs / total_subs * 100) if total_subs > 0 else 0
    
    return {
        "retention_rate_30d": round(retention_rate, 2),
        "churn_rate_30d": round(churn_rate, 2),
        "active_users": active_old_users,
        "total_users": old_users
    }


@router.get("/cohort-analysis")
async def get_cohort_analysis(
    db=Depends(get_db)
):
    """Get cohort analysis"""
    # Group users by signup month
    pipeline = [
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m",
                        "date": "$created_at"
                    }
                },
                "users": {"$sum": 1}
            }
        },
        {"$sort": {"_id": -1}},
        {"$limit": 12}
    ]
    
    cohorts = await db["users"].aggregate(pipeline).to_list(length=12)
    
    return {
        "cohorts": [
            {
                "month": cohort["_id"],
                "users": cohort["users"]
            }
            for cohort in cohorts
        ]
    }
