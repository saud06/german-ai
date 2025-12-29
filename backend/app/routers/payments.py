"""
Payment and subscription API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from typing import Optional
import stripe
import os

from ..db import get_db
from ..security import get_current_user_id
from ..services.stripe_service import StripeService
from ..models.subscription import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    SubscriptionResponse,
    UsageResponse,
    SubscriptionTier
)


router = APIRouter(prefix="/payments", tags=["payments"])


def get_stripe_service(db=Depends(get_db)) -> StripeService:
    """Dependency to get Stripe service"""
    return StripeService(db)


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    user_id: str = Depends(get_current_user_id),
    stripe_service: StripeService = Depends(get_stripe_service)
):
    """
    Create a Stripe checkout session for subscription
    """
    try:
        result = await stripe_service.create_checkout_session(
            user_id=user_id,
            tier=request.tier,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            trial_days=request.trial_days
        )
        return CheckoutSessionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
    stripe_service: StripeService = Depends(get_stripe_service)
):
    """
    Handle Stripe webhooks
    """
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    try:
        payload = await request.body()
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle different event types
    event_type = event["type"]
    data = event["data"]["object"]
    
    try:
        if event_type == "checkout.session.completed":
            await stripe_service.handle_checkout_completed(data)
        elif event_type == "customer.subscription.updated":
            await stripe_service.handle_subscription_updated(data)
        elif event_type == "customer.subscription.deleted":
            await stripe_service.handle_subscription_deleted(data)
        elif event_type == "invoice.paid":
            await stripe_service.handle_invoice_paid(data)
        elif event_type == "invoice.payment_failed":
            # Handle failed payment (send email, etc.)
            pass
    except Exception as e:
        print(f"Error handling webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")
    
    return {"status": "success"}


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    user_id: str = Depends(get_current_user_id),
    stripe_service: StripeService = Depends(get_stripe_service)
):
    """
    Get current user's subscription details
    """
    subscription = await stripe_service.get_subscription(user_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return SubscriptionResponse(
        tier=SubscriptionTier(subscription["tier"]),
        status=subscription["status"],
        features=subscription["features"],
        current_period_end=subscription.get("current_period_end"),
        cancel_at_period_end=subscription.get("cancel_at_period_end", False),
        trial_end=subscription.get("trial_end")
    )


@router.post("/cancel-subscription")
async def cancel_subscription(
    immediate: bool = False,
    user_id: str = Depends(get_current_user_id),
    stripe_service: StripeService = Depends(get_stripe_service)
):
    """
    Cancel user's subscription
    """
    try:
        await stripe_service.cancel_subscription(user_id, immediate)
        return {"message": "Subscription canceled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/invoices")
async def get_invoices(
    limit: int = 10,
    user_id: str = Depends(get_current_user_id),
    stripe_service: StripeService = Depends(get_stripe_service)
):
    """
    Get user's invoices
    """
    invoices = await stripe_service.get_invoices(user_id, limit)
    return {"invoices": invoices}


@router.post("/customer-portal")
async def create_customer_portal(
    return_url: str,
    user_id: str = Depends(get_current_user_id),
    stripe_service: StripeService = Depends(get_stripe_service)
):
    """
    Create a Stripe customer portal session
    """
    try:
        portal_url = await stripe_service.create_customer_portal_session(user_id, return_url)
        return {"url": portal_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    user_id: str = Depends(get_current_user_id),
    stripe_service: StripeService = Depends(get_stripe_service)
):
    """
    Get current usage and limits
    """
    usage = await stripe_service.check_usage_limits(user_id)
    return UsageResponse(**usage)


@router.get("/pricing")
async def get_pricing():
    """
    Get pricing information for all tiers
    """
    return {
        "tiers": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "currency": "usd",
                "interval": "month",
                "features": [
                    "30 minutes/day AI conversation",
                    "5 scenarios per week",
                    "50 review cards",
                    "Basic features",
                    "Community support"
                ]
            },
            {
                "id": "premium",
                "name": "Premium",
                "price": 999,  # $9.99 in cents
                "currency": "usd",
                "interval": "month",
                "features": [
                    "Unlimited AI conversation",
                    "Unlimited scenarios",
                    "Unlimited review cards",
                    "Offline mode",
                    "Advanced analytics",
                    "Certification prep",
                    "Priority support"
                ],
                "popular": True
            },
            {
                "id": "plus",
                "name": "Plus",
                "price": 1999,  # $19.99 in cents
                "currency": "usd",
                "interval": "month",
                "features": [
                    "Everything in Premium",
                    "Custom AI personality",
                    "Business German focus",
                    "Industry-specific vocabulary",
                    "API access",
                    "Early feature access",
                    "1-on-1 support"
                ]
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price": None,  # Custom pricing
                "currency": "usd",
                "interval": "month",
                "features": [
                    "Everything in Plus",
                    "Self-hosted deployment",
                    "White-label branding",
                    "SSO integration",
                    "Admin dashboard",
                    "Custom content",
                    "SLA support",
                    "Dedicated account manager"
                ],
                "contact_sales": True
            }
        ]
    }
