"""
Organization Management Router
Multi-tenant organization CRUD and management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from ..db import get_db
from ..routers.auth import get_current_user
from ..models.organization import (
    Organization, OrganizationCreate, OrganizationUpdate,
    OrganizationMember, MemberInvite, OrganizationInvitation,
    OrganizationSettings, SubscriptionInfo, OrganizationLimits
)
import secrets
import hashlib

router = APIRouter(prefix="/organizations", tags=["Organizations"])


# Helper functions

async def check_organization_access(
    organization_id: str,
    user_id: str,
    required_role: str,
    db
) -> bool:
    """Check if user has required role in organization"""
    member = await db["organization_members"].find_one({
        "organization_id": organization_id,
        "user_id": user_id
    })
    
    if not member:
        return False
    
    role_hierarchy = ["viewer", "member", "admin", "owner"]
    user_role_level = role_hierarchy.index(member.get("role", "viewer"))
    required_role_level = role_hierarchy.index(required_role)
    
    return user_role_level >= required_role_level


async def get_user_organizations(user_id: str, db) -> List[str]:
    """Get list of organization IDs user belongs to"""
    memberships = await db["organization_members"].find(
        {"user_id": user_id}
    ).to_list(length=100)
    
    return [m["organization_id"] for m in memberships]


# Organization CRUD

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Create a new organization"""
    # Check if slug is already taken
    existing = await db["organizations"].find_one({"slug": org_data.slug})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization slug already exists"
        )
    
    # Create organization
    org = Organization(
        name=org_data.name,
        slug=org_data.slug,
        description=org_data.description,
        owner_id=user_id,
        total_users=1
    )
    
    result = await db["organizations"].insert_one(org.dict(by_alias=True, exclude={"id"}))
    org_id = str(result.inserted_id)
    
    # Add creator as owner
    member = OrganizationMember(
        organization_id=org_id,
        user_id=user_id,
        role="owner",
        permissions=["*"]  # Full permissions
    )
    
    await db["organization_members"].insert_one(member.dict(by_alias=True, exclude={"id"}))
    
    # Log audit event
    await db["audit_logs"].insert_one({
        "organization_id": org_id,
        "user_id": user_id,
        "action": "create",
        "resource_type": "organization",
        "resource_id": org_id,
        "ip_address": "0.0.0.0",  # Should be from request
        "user_agent": "API",
        "metadata": {"name": org_data.name},
        "created_at": datetime.utcnow()
    })
    
    return {"id": org_id, "message": "Organization created successfully"}


@router.get("/")
async def list_organizations(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """List all organizations user belongs to"""
    org_ids = await get_user_organizations(user_id, db)
    
    organizations = []
    for org_id in org_ids:
        org = await db["organizations"].find_one({"_id": org_id})
        if org:
            # Get user's role
            member = await db["organization_members"].find_one({
                "organization_id": org_id,
                "user_id": user_id
            })
            
            org["_id"] = str(org["_id"])
            org["user_role"] = member.get("role") if member else "viewer"
            organizations.append(org)
    
    return {"organizations": organizations, "total": len(organizations)}


@router.get("/{organization_id}")
async def get_organization(
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get organization details"""
    # Check access
    has_access = await check_organization_access(organization_id, user_id, "viewer", db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    org = await db["organizations"].find_one({"_id": organization_id})
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    org["_id"] = str(org["_id"])
    return org


@router.patch("/{organization_id}")
async def update_organization(
    organization_id: str,
    org_data: OrganizationUpdate,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Update organization details"""
    # Check admin access
    has_access = await check_organization_access(organization_id, user_id, "admin", db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Build update dict
    update_data = {}
    if org_data.name:
        update_data["name"] = org_data.name
    if org_data.description:
        update_data["description"] = org_data.description
    if org_data.settings:
        update_data["settings"] = org_data.settings.dict()
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Update organization
    result = await db["organizations"].update_one(
        {"_id": organization_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Log audit event
    await db["audit_logs"].insert_one({
        "organization_id": organization_id,
        "user_id": user_id,
        "action": "update",
        "resource_type": "organization",
        "resource_id": organization_id,
        "ip_address": "0.0.0.0",
        "user_agent": "API",
        "metadata": update_data,
        "created_at": datetime.utcnow()
    })
    
    return {"message": "Organization updated successfully"}


@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Delete organization (owner only)"""
    # Check owner access
    has_access = await check_organization_access(organization_id, user_id, "owner", db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required"
        )
    
    # Delete organization
    await db["organizations"].delete_one({"_id": organization_id})
    
    # Delete all members
    await db["organization_members"].delete_many({"organization_id": organization_id})
    
    # Delete all API keys
    await db["api_keys"].delete_many({"organization_id": organization_id})
    
    # Delete all webhooks
    await db["webhooks"].delete_many({"organization_id": organization_id})
    
    # Log audit event
    await db["audit_logs"].insert_one({
        "organization_id": organization_id,
        "user_id": user_id,
        "action": "delete",
        "resource_type": "organization",
        "resource_id": organization_id,
        "ip_address": "0.0.0.0",
        "user_agent": "API",
        "metadata": {},
        "created_at": datetime.utcnow()
    })
    
    return {"message": "Organization deleted successfully"}


# Member Management

@router.get("/{organization_id}/members")
async def list_members(
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """List organization members"""
    # Check access
    has_access = await check_organization_access(organization_id, user_id, "member", db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    members = await db["organization_members"].find(
        {"organization_id": organization_id}
    ).to_list(length=1000)
    
    # Enrich with user data
    enriched_members = []
    for member in members:
        user = await db["users"].find_one({"_id": member["user_id"]})
        if user:
            member["_id"] = str(member["_id"])
            member["user_name"] = user.get("name", "Unknown")
            member["user_email"] = user.get("email", "")
            enriched_members.append(member)
    
    return {"members": enriched_members, "total": len(enriched_members)}


@router.post("/{organization_id}/invite")
async def invite_member(
    organization_id: str,
    invite_data: MemberInvite,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Invite a new member to organization"""
    # Check admin access
    has_access = await check_organization_access(organization_id, user_id, "admin", db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if user already exists
    existing_user = await db["users"].find_one({"email": invite_data.email})
    
    # Generate invitation token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    # Create invitation
    invitation = OrganizationInvitation(
        organization_id=organization_id,
        email=invite_data.email,
        role=invite_data.role,
        permissions=invite_data.permissions,
        invited_by=user_id,
        invitation_token=token,
        expires_at=expires_at
    )
    
    result = await db["organization_invitations"].insert_one(
        invitation.dict(by_alias=True, exclude={"id"})
    )
    
    # TODO: Send invitation email
    
    return {
        "invitation_id": str(result.inserted_id),
        "invitation_token": token,
        "expires_at": expires_at.isoformat(),
        "message": "Invitation sent successfully"
    }


@router.delete("/{organization_id}/members/{member_user_id}")
async def remove_member(
    organization_id: str,
    member_user_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Remove a member from organization"""
    # Check admin access
    has_access = await check_organization_access(organization_id, user_id, "admin", db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Cannot remove owner
    member = await db["organization_members"].find_one({
        "organization_id": organization_id,
        "user_id": member_user_id
    })
    
    if member and member.get("role") == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove organization owner"
        )
    
    # Remove member
    result = await db["organization_members"].delete_one({
        "organization_id": organization_id,
        "user_id": member_user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Update organization user count
    await db["organizations"].update_one(
        {"_id": organization_id},
        {"$inc": {"total_users": -1}}
    )
    
    return {"message": "Member removed successfully"}


# Statistics

@router.get("/{organization_id}/stats")
async def get_organization_stats(
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get organization statistics"""
    # Check access
    has_access = await check_organization_access(organization_id, user_id, "admin", db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get member count
    member_count = await db["organization_members"].count_documents({
        "organization_id": organization_id
    })
    
    # Get API key count
    api_key_count = await db["api_keys"].count_documents({
        "organization_id": organization_id,
        "active": True
    })
    
    # Get webhook count
    webhook_count = await db["webhooks"].count_documents({
        "organization_id": organization_id,
        "active": True
    })
    
    # Get total API calls (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    api_calls = await db["api_usage"].count_documents({
        "organization_id": organization_id,
        "created_at": {"$gte": thirty_days_ago}
    })
    
    return {
        "members": member_count,
        "api_keys": api_key_count,
        "webhooks": webhook_count,
        "api_calls_30d": api_calls
    }
