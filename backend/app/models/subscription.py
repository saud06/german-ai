"""
Subscription and payment models for Stripe integration
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SubscriptionTier(str, Enum):
    """Subscription tier levels"""
    FREE = "free"
    PREMIUM = "premium"
    PLUS = "plus"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"


class PaymentMethodType(str, Enum):
    """Payment method types"""
    CARD = "card"
    PAYPAL = "paypal"
    BANK_ACCOUNT = "bank_account"


class SubscriptionFeatures(BaseModel):
    """Features available for each subscription tier"""
    ai_minutes_per_day: Optional[int] = None  # None = unlimited
    scenarios_per_day: Optional[int] = None  # None = unlimited
    max_review_cards: Optional[int] = None  # None = unlimited
    offline_mode: bool = False
    custom_ai: bool = False
    business_german: bool = False
    priority_support: bool = False
    advanced_analytics: bool = False
    certification_prep: bool = False
    api_access: bool = False


class Subscription(BaseModel):
    """User subscription model"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    stripe_customer_id: str
    stripe_subscription_id: Optional[str] = None
    tier: SubscriptionTier = SubscriptionTier.FREE
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    trial_end: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class PaymentMethod(BaseModel):
    """Payment method model"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    stripe_payment_method_id: str
    type: PaymentMethodType
    last4: Optional[str] = None  # Last 4 digits of card
    brand: Optional[str] = None  # Card brand (visa, mastercard, etc.)
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class Invoice(BaseModel):
    """Invoice model"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    stripe_invoice_id: str
    stripe_subscription_id: Optional[str] = None
    amount: int  # Amount in cents
    currency: str = "usd"
    status: str  # paid, open, void, uncollectible
    invoice_pdf: Optional[str] = None  # URL to PDF
    hosted_invoice_url: Optional[str] = None  # URL to hosted invoice
    period_start: datetime
    period_end: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class UsageTracking(BaseModel):
    """Track user usage for free tier limits"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    date: datetime = Field(default_factory=lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
    ai_minutes_used: int = 0
    scenarios_completed: int = 0
    review_cards_added: int = 0
    last_reset: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class CheckoutSessionRequest(BaseModel):
    """Request to create a checkout session"""
    tier: SubscriptionTier
    success_url: str
    cancel_url: str
    trial_days: Optional[int] = None


class CheckoutSessionResponse(BaseModel):
    """Response with checkout session URL"""
    session_id: str
    checkout_url: str


class SubscriptionResponse(BaseModel):
    """Response with subscription details"""
    tier: SubscriptionTier
    status: SubscriptionStatus
    features: SubscriptionFeatures
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    trial_end: Optional[datetime] = None


class UsageResponse(BaseModel):
    """Response with current usage"""
    ai_minutes_used: int
    ai_minutes_limit: Optional[int]  # None = unlimited
    scenarios_completed: int
    scenarios_limit: Optional[int]  # None = unlimited
    can_use_ai: bool
    can_start_scenario: bool


# Tier features configuration
TIER_FEATURES = {
    SubscriptionTier.FREE: SubscriptionFeatures(
        ai_minutes_per_day=30,
        scenarios_per_day=2,  # 2 scenarios per day - realistic for daily practice
        max_review_cards=50,
        offline_mode=False,
        custom_ai=False,
        business_german=False,
        priority_support=False,
        advanced_analytics=False,
        certification_prep=False,
        api_access=False
    ),
    SubscriptionTier.PREMIUM: SubscriptionFeatures(
        ai_minutes_per_day=None,  # Unlimited
        scenarios_per_day=None,  # Unlimited
        max_review_cards=None,  # Unlimited
        offline_mode=True,
        custom_ai=False,
        business_german=False,
        priority_support=True,
        advanced_analytics=True,
        certification_prep=True,
        api_access=False
    ),
    SubscriptionTier.PLUS: SubscriptionFeatures(
        ai_minutes_per_day=None,  # Unlimited
        scenarios_per_day=None,  # Unlimited
        max_review_cards=None,  # Unlimited
        offline_mode=True,
        custom_ai=True,
        business_german=True,
        priority_support=True,
        advanced_analytics=True,
        certification_prep=True,
        api_access=True
    ),
    SubscriptionTier.ENTERPRISE: SubscriptionFeatures(
        ai_minutes_per_day=None,  # Unlimited
        scenarios_per_day=None,  # Unlimited
        max_review_cards=None,  # Unlimited
        offline_mode=True,
        custom_ai=True,
        business_german=True,
        priority_support=True,
        advanced_analytics=True,
        certification_prep=True,
        api_access=True
    )
}


def get_tier_features(tier: SubscriptionTier) -> SubscriptionFeatures:
    """Get features for a subscription tier"""
    return TIER_FEATURES.get(tier, TIER_FEATURES[SubscriptionTier.FREE])
