"""
Stripe payment service for subscription management
"""
import stripe
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

from ..models.subscription import (
    Subscription,
    SubscriptionTier,
    SubscriptionStatus,
    PaymentMethod,
    Invoice,
    UsageTracking,
    get_tier_features
)


class StripeService:
    """Service for managing Stripe payments and subscriptions"""
    
    def __init__(self, db):
        self.db = db
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.premium_price_id = os.getenv("STRIPE_PREMIUM_PRICE_ID")
        self.plus_price_id = os.getenv("STRIPE_PLUS_PRICE_ID")
    
    async def create_customer(self, user_id: str, email: str, name: str) -> str:
        """Create a Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": user_id}
            )
            
            # Save subscription record
            subscription_doc = {
                "user_id": user_id,
                "stripe_customer_id": customer.id,
                "tier": SubscriptionTier.FREE.value,
                "status": SubscriptionStatus.ACTIVE.value,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await self.db["subscriptions"].insert_one(subscription_doc)
            
            return customer.id
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create customer: {str(e)}")
    
    async def get_or_create_customer(self, user_id: str) -> str:
        """Get existing customer or create new one"""
        subscription = await self.db["subscriptions"].find_one({"user_id": user_id})
        
        if subscription and subscription.get("stripe_customer_id"):
            return subscription["stripe_customer_id"]
        
        # Get user details
        user = await self.db["users"].find_one({"_id": ObjectId(user_id)})
        if not user:
            raise Exception("User not found")
        
        return await self.create_customer(
            user_id=user_id,
            email=user.get("email", ""),
            name=user.get("name", "")
        )
    
    async def create_checkout_session(
        self,
        user_id: str,
        tier: SubscriptionTier,
        success_url: str,
        cancel_url: str,
        trial_days: Optional[int] = None
    ) -> Dict[str, str]:
        """Create a Stripe checkout session"""
        try:
            customer_id = await self.get_or_create_customer(user_id)
            
            # Determine price ID based on tier
            if tier == SubscriptionTier.PREMIUM:
                price_id = self.premium_price_id
            elif tier == SubscriptionTier.PLUS:
                price_id = self.plus_price_id
            else:
                raise Exception(f"Invalid tier for checkout: {tier}")
            
            # Create checkout session
            session_params = {
                "customer": customer_id,
                "payment_method_types": ["card"],
                "line_items": [{
                    "price": price_id,
                    "quantity": 1
                }],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": {
                    "user_id": user_id,
                    "tier": tier.value
                }
            }
            
            # Add trial if specified
            if trial_days:
                session_params["subscription_data"] = {
                    "trial_period_days": trial_days
                }
            
            session = stripe.checkout.Session.create(**session_params)
            
            return {
                "session_id": session.id,
                "checkout_url": session.url
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create checkout session: {str(e)}")
    
    async def handle_checkout_completed(self, session: Dict[str, Any]):
        """Handle successful checkout completion"""
        user_id = session["metadata"]["user_id"]
        tier = session["metadata"]["tier"]
        subscription_id = session["subscription"]
        
        # Get subscription details from Stripe
        stripe_subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Update subscription in database
        await self.db["subscriptions"].update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "stripe_subscription_id": subscription_id,
                    "tier": tier,
                    "status": stripe_subscription.status,
                    "current_period_start": datetime.fromtimestamp(stripe_subscription.current_period_start),
                    "current_period_end": datetime.fromtimestamp(stripe_subscription.current_period_end),
                    "cancel_at_period_end": stripe_subscription.cancel_at_period_end,
                    "trial_end": datetime.fromtimestamp(stripe_subscription.trial_end) if stripe_subscription.trial_end else None,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    async def handle_subscription_updated(self, subscription: Dict[str, Any]):
        """Handle subscription update webhook"""
        customer_id = subscription["customer"]
        
        # Find user by customer ID
        db_subscription = await self.db["subscriptions"].find_one({"stripe_customer_id": customer_id})
        if not db_subscription:
            return
        
        # Update subscription
        await self.db["subscriptions"].update_one(
            {"_id": db_subscription["_id"]},
            {
                "$set": {
                    "status": subscription["status"],
                    "current_period_start": datetime.fromtimestamp(subscription["current_period_start"]),
                    "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]),
                    "cancel_at_period_end": subscription["cancel_at_period_end"],
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    async def handle_subscription_deleted(self, subscription: Dict[str, Any]):
        """Handle subscription cancellation"""
        customer_id = subscription["customer"]
        
        # Find user by customer ID
        db_subscription = await self.db["subscriptions"].find_one({"stripe_customer_id": customer_id})
        if not db_subscription:
            return
        
        # Downgrade to free tier
        await self.db["subscriptions"].update_one(
            {"_id": db_subscription["_id"]},
            {
                "$set": {
                    "tier": SubscriptionTier.FREE.value,
                    "status": SubscriptionStatus.CANCELED.value,
                    "stripe_subscription_id": None,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    async def handle_invoice_paid(self, invoice: Dict[str, Any]):
        """Handle successful invoice payment"""
        customer_id = invoice["customer"]
        
        # Find user by customer ID
        db_subscription = await self.db["subscriptions"].find_one({"stripe_customer_id": customer_id})
        if not db_subscription:
            return
        
        # Save invoice record
        invoice_doc = {
            "user_id": db_subscription["user_id"],
            "stripe_invoice_id": invoice["id"],
            "stripe_subscription_id": invoice.get("subscription"),
            "amount": invoice["amount_paid"],
            "currency": invoice["currency"],
            "status": invoice["status"],
            "invoice_pdf": invoice.get("invoice_pdf"),
            "hosted_invoice_url": invoice.get("hosted_invoice_url"),
            "period_start": datetime.fromtimestamp(invoice["period_start"]),
            "period_end": datetime.fromtimestamp(invoice["period_end"]),
            "created_at": datetime.utcnow()
        }
        await self.db["invoices"].insert_one(invoice_doc)
    
    async def cancel_subscription(self, user_id: str, immediate: bool = False) -> bool:
        """Cancel a user's subscription"""
        try:
            subscription = await self.db["subscriptions"].find_one({"user_id": user_id})
            if not subscription or not subscription.get("stripe_subscription_id"):
                raise Exception("No active subscription found")
            
            # Cancel in Stripe
            if immediate:
                stripe.Subscription.delete(subscription["stripe_subscription_id"])
            else:
                stripe.Subscription.modify(
                    subscription["stripe_subscription_id"],
                    cancel_at_period_end=True
                )
            
            # Update database
            update_data = {
                "cancel_at_period_end": True,
                "updated_at": datetime.utcnow()
            }
            if immediate:
                update_data["tier"] = SubscriptionTier.FREE.value
                update_data["status"] = SubscriptionStatus.CANCELED.value
                update_data["stripe_subscription_id"] = None
            
            await self.db["subscriptions"].update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            return True
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to cancel subscription: {str(e)}")
    
    async def get_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's subscription details"""
        subscription = await self.db["subscriptions"].find_one({"user_id": user_id})
        if not subscription:
            return None
        
        tier = SubscriptionTier(subscription.get("tier", "free"))
        features = get_tier_features(tier)
        
        return {
            "tier": tier.value,
            "status": subscription.get("status", "active"),
            "features": features.dict(),
            "current_period_end": subscription.get("current_period_end"),
            "cancel_at_period_end": subscription.get("cancel_at_period_end", False),
            "trial_end": subscription.get("trial_end")
        }
    
    async def get_invoices(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's invoices"""
        invoices = await self.db["invoices"].find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        return [
            {
                "id": str(invoice["_id"]),
                "amount": invoice["amount"],
                "currency": invoice["currency"],
                "status": invoice["status"],
                "invoice_pdf": invoice.get("invoice_pdf"),
                "hosted_invoice_url": invoice.get("hosted_invoice_url"),
                "period_start": invoice["period_start"],
                "period_end": invoice["period_end"],
                "created_at": invoice["created_at"]
            }
            for invoice in invoices
        ]
    
    async def create_customer_portal_session(self, user_id: str, return_url: str) -> str:
        """Create a Stripe customer portal session"""
        try:
            customer_id = await self.get_or_create_customer(user_id)
            
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            
            return session.url
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create portal session: {str(e)}")
    
    async def check_usage_limits(self, user_id: str) -> Dict[str, Any]:
        """Check if user has exceeded usage limits"""
        subscription = await self.db["subscriptions"].find_one({"user_id": user_id})
        if not subscription:
            return {"can_use_ai": False, "can_start_scenario": False}
        
        tier = SubscriptionTier(subscription.get("tier", "free"))
        features = get_tier_features(tier)
        
        # Unlimited for premium tiers
        if features.ai_minutes_per_day is None:
            return {
                "can_use_ai": True,
                "can_start_scenario": True,
                "ai_minutes_used": 0,
                "ai_minutes_limit": None,
                "scenarios_completed": 0,
                "scenarios_limit": None
            }
        
        # Check daily usage for free tier
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        usage = await self.db["usage_tracking"].find_one({
            "user_id": user_id,
            "date": today
        })
        
        if not usage:
            # Create new usage record
            usage = {
                "user_id": user_id,
                "date": today,
                "ai_minutes_used": 0,
                "scenarios_completed": 0,
                "last_reset": datetime.utcnow()
            }
            await self.db["usage_tracking"].insert_one(usage)
        
        ai_minutes_used = usage.get("ai_minutes_used", 0)
        scenarios_completed = usage.get("scenarios_completed", 0)
        
        return {
            "can_use_ai": ai_minutes_used < features.ai_minutes_per_day,
            "can_start_scenario": scenarios_completed < features.scenarios_per_week,
            "ai_minutes_used": ai_minutes_used,
            "ai_minutes_limit": features.ai_minutes_per_day,
            "scenarios_completed": scenarios_completed,
            "scenarios_limit": features.scenarios_per_week
        }
    
    async def track_ai_usage(self, user_id: str, minutes: int):
        """Track AI usage minutes"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        await self.db["usage_tracking"].update_one(
            {"user_id": user_id, "date": today},
            {
                "$inc": {"ai_minutes_used": minutes},
                "$set": {"last_reset": datetime.utcnow()}
            },
            upsert=True
        )
    
    async def track_scenario_completion(self, user_id: str):
        """Track scenario completion"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        await self.db["usage_tracking"].update_one(
            {"user_id": user_id, "date": today},
            {
                "$inc": {"scenarios_completed": 1},
                "$set": {"last_reset": datetime.utcnow()}
            },
            upsert=True
        )
