"""
Organization models for multi-tenant architecture
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ])

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if ObjectId.is_valid(v):
            return str(v)
        raise ValueError("Invalid ObjectId")


class OrganizationSettings(BaseModel):
    """Organization-specific settings"""
    primary_color: str = "#3B82F6"
    secondary_color: str = "#10B981"
    logo_url: Optional[str] = None
    custom_domain: Optional[str] = None
    sso_enabled: bool = False
    api_enabled: bool = False
    webhook_enabled: bool = False
    custom_branding: bool = False
    
    class Config:
        json_encoders = {ObjectId: str}


class SubscriptionInfo(BaseModel):
    """Subscription information"""
    tier: str = "free"  # free, premium, plus, enterprise
    status: str = "active"  # active, cancelled, past_due, trialing
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    
    class Config:
        json_encoders = {ObjectId: str}


class OrganizationLimits(BaseModel):
    """Usage limits for organization"""
    max_users: int = 5
    max_api_calls_per_hour: int = 100
    max_scenarios: int = 10
    max_storage_mb: int = 100
    max_webhooks: int = 5
    
    class Config:
        json_encoders = {ObjectId: str}


class Organization(BaseModel):
    """Organization model for multi-tenancy"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    slug: str  # Unique subdomain/identifier
    description: Optional[str] = None
    
    # Branding
    settings: OrganizationSettings = Field(default_factory=OrganizationSettings)
    
    # Subscription
    subscription: SubscriptionInfo = Field(default_factory=SubscriptionInfo)
    
    # Limits
    limits: OrganizationLimits = Field(default_factory=OrganizationLimits)
    
    # Owner
    owner_id: str
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Stats
    total_users: int = 0
    total_api_calls: int = 0
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class OrganizationMember(BaseModel):
    """User membership in an organization"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    organization_id: str
    user_id: str
    
    # Role and permissions
    role: str = "member"  # owner, admin, member, viewer
    permissions: List[str] = []  # Specific permissions
    
    # Invitation
    invited_by: Optional[str] = None
    invitation_accepted: bool = True
    
    # Metadata
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class OrganizationInvitation(BaseModel):
    """Invitation to join an organization"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    organization_id: str
    email: str
    role: str = "member"
    permissions: List[str] = []
    
    # Invitation details
    invited_by: str
    invitation_token: str
    expires_at: datetime
    accepted: bool = False
    accepted_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class APIKey(BaseModel):
    """API key for programmatic access"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    organization_id: str
    
    # Key details
    name: str
    key_hash: str  # Hashed API key
    key_prefix: str  # First 8 chars for display (e.g., "sk_live_...")
    
    # Permissions and limits
    permissions: List[str] = []  # Scoped permissions
    rate_limit: int = 100  # Requests per hour
    
    # Usage tracking
    total_requests: int = 0
    last_used_at: Optional[datetime] = None
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    active: bool = True
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Webhook(BaseModel):
    """Webhook configuration"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    organization_id: str
    
    # Webhook details
    url: str
    events: List[str] = []  # Event types to subscribe to
    secret: str  # For signature verification
    
    # Configuration
    active: bool = True
    description: Optional[str] = None
    
    # Stats
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    last_delivery_at: Optional[datetime] = None
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class WebhookDelivery(BaseModel):
    """Webhook delivery attempt"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    webhook_id: str
    organization_id: str
    
    # Event details
    event_type: str
    payload: Dict[str, Any]
    
    # Delivery details
    status: str = "pending"  # pending, delivered, failed
    attempts: int = 0
    max_attempts: int = 3
    
    # Response
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AuditLog(BaseModel):
    """Audit log for compliance"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    organization_id: str
    user_id: str
    
    # Action details
    action: str  # create, update, delete, view, export
    resource_type: str  # user, scenario, achievement, etc.
    resource_id: Optional[str] = None
    
    # Request details
    ip_address: str
    user_agent: str
    
    # Additional context
    metadata: Dict[str, Any] = {}
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Request/Response models for API

class OrganizationCreate(BaseModel):
    """Request model for creating an organization"""
    name: str
    slug: str
    description: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """Request model for updating an organization"""
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[OrganizationSettings] = None


class MemberInvite(BaseModel):
    """Request model for inviting a member"""
    email: str
    role: str = "member"
    permissions: List[str] = []


class APIKeyCreate(BaseModel):
    """Request model for creating an API key"""
    name: str
    permissions: List[str] = []
    rate_limit: int = 100
    expires_in_days: Optional[int] = None


class WebhookCreate(BaseModel):
    """Request model for creating a webhook"""
    url: str
    events: List[str]
    description: Optional[str] = None
