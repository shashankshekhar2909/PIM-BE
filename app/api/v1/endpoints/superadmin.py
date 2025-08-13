from fastapi import APIRouter, Depends, HTTPException, Body, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from app.models.product import Product
from app.models.audit import AuditLog
from app.models.category import Category
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

router = APIRouter()

def log_audit_action(
    db: Session,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    resource_name: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    metadata: Optional[Dict] = None
):
    """Log an audit action"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        audit_metadata=metadata
    )
    db.add(audit_log)
    db.commit()

def require_superadmin(current_user: User):
    """Require superadmin role"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")

def require_superadmin_or_analyst(current_user: User):
    """Require superadmin or analyst role"""
    if not (current_user.is_superadmin or current_user.is_analyst):
        raise HTTPException(status_code=403, detail="Superadmin or analyst access required")

# User Management Endpoints

@router.get("/users")
def list_all_users(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(100, ge=1, le=1000, description="Number of items per page (max 1000)"),
    skip: int = Query(None, description="Number of records to skip (deprecated, use page and page_size)"),
    limit: int = Query(None, description="Maximum number of records to return (deprecated, use page and page_size)"),
    role: Optional[str] = Query(None),
    tenant_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_blocked: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all users with pagination (superadmin and analyst only).
    Analysts can only view, superadmins can view and manage.
    """
    require_superadmin_or_analyst(current_user)
    
    # Handle deprecated skip/limit parameters
    if skip is not None or limit is not None:
        # Calculate page and page_size from skip/limit for backward compatibility
        if skip is not None and limit is not None:
            page = (skip // limit) + 1
            page_size = limit
        elif skip is not None:
            page = (skip // 100) + 1
            page_size = 100
        elif limit is not None:
            page = 1
            page_size = limit
    
    # Calculate actual skip and limit from page and page_size
    actual_skip = (page - 1) * page_size
    actual_limit = page_size
    
    query = db.query(User)
    
    # Apply filters
    if role:
        query = query.filter(User.role == role)
    if tenant_id:
        query = query.filter(User.tenant_id == tenant_id)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_blocked is not None:
        query = query.filter(User.is_blocked == is_blocked)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term)
            )
        )
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    users = query.offset(actual_skip).limit(actual_limit).all()
    
    # Log the action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="list_users",
        resource_type="users",
        details=f"Listed {len(users)} users (page {page}, page_size {page_size})",
        ip_address=None,
        user_agent=None
    )
    
    return {
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "tenant_id": user.tenant_id,
                "is_active": user.is_active,
                "is_blocked": user.is_blocked,
                "created_at": user.created_at,
                "last_login": user.last_login,
                "audit_logs_count": len(user.audit_logs)
            }
            for user in users
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size,
            "total_items": total_count,
            "has_next": page * page_size < total_count,
            "has_previous": page > 1,
            "next_page": page + 1 if page * page_size < total_count else None,
            "previous_page": page - 1 if page > 1 else None
        },
        "total_count": total_count,
        "skip": actual_skip,
        "limit": actual_limit
    }

@router.get("/users/{user_id}")
def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed user information (superadmin and analyst only)"""
    require_superadmin_or_analyst(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log the action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="read",
        resource_type="user",
        resource_id=user_id,
        resource_name=user.email
    )
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "tenant_name": user.tenant.company_name if user.tenant else None,
        "is_active": user.is_active,
        "is_blocked": user.is_blocked,
        "last_login": user.last_login,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "created_by": user.created_by,
        "notes": user.notes,
        "audit_logs_count": len(user.audit_logs)
    }

@router.post("/users")
def create_user(
    user_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new user (superadmin only)"""
    require_superadmin(current_user)
    
    # Validate required fields
    required_fields = ["email", "role"]
    for field in required_fields:
        if field not in user_data:
            raise HTTPException(status_code=400, detail=f"Field '{field}' is required")
    
    # Validate role
    valid_roles = ["superadmin", "analyst", "tenant_admin", "tenant_user"]
    if user_data["role"] not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data["email"]).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate tenant_id for tenant users
    if user_data["role"] in ["tenant_admin", "tenant_user"]:
        if "tenant_id" not in user_data or not user_data["tenant_id"]:
            raise HTTPException(status_code=400, detail="tenant_id is required for tenant users")
        
        # Check if tenant exists
        tenant = db.query(Tenant).filter(Tenant.id == user_data["tenant_id"]).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Create user
    user = User(
        email=user_data["email"],
        role=user_data["role"],
        first_name=user_data.get("first_name"),
        last_name=user_data.get("last_name"),
        tenant_id=user_data.get("tenant_id"),
        is_active=user_data.get("is_active", True),
        is_blocked=user_data.get("is_blocked", False),
        notes=user_data.get("notes"),
        created_by=current_user.id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log the action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="create",
        resource_type="user",
        resource_id=user.id,
        resource_name=user.email,
        details=f"Created user with role: {user.role}"
    )
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "is_active": user.is_active,
        "is_blocked": user.is_blocked,
        "created_at": user.created_at,
        "created_by": user.created_by
    }

@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    user_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user (superadmin only)"""
    require_superadmin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent updating own role to non-superadmin
    if user_id == current_user.id and user_data.get("role") != "superadmin":
        raise HTTPException(status_code=400, detail="Cannot change your own role from superadmin")
    
    # Update fields
    if "first_name" in user_data:
        user.first_name = user_data["first_name"]
    if "last_name" in user_data:
        user.last_name = user_data["last_name"]
    if "role" in user_data:
        # Validate role
        valid_roles = ["superadmin", "analyst", "tenant_admin", "tenant_user"]
        if user_data["role"] not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")
        user.role = user_data["role"]
    if "tenant_id" in user_data:
        if user_data["tenant_id"]:
            # Check if tenant exists
            tenant = db.query(Tenant).filter(Tenant.id == user_data["tenant_id"]).first()
            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")
        user.tenant_id = user_data["tenant_id"]
    if "is_active" in user_data:
        user.is_active = user_data["is_active"]
    if "is_blocked" in user_data:
        user.is_blocked = user_data["is_blocked"]
    if "notes" in user_data:
        user.notes = user_data["notes"]
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Log the action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="update",
        resource_type="user",
        resource_id=user_id,
        resource_name=user.email,
        details=f"Updated user fields: {list(user_data.keys())}"
    )
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "is_active": user.is_active,
        "is_blocked": user.is_blocked,
        "updated_at": user.updated_at,
        "notes": user.notes
    }

@router.post("/users/{user_id}/block")
def block_user(
    user_id: int,
    reason: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Block a user (superadmin only)"""
    require_superadmin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot block yourself")
    
    user.is_blocked = True
    user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log the action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="block",
        resource_type="user",
        resource_id=user_id,
        resource_name=user.email,
        details=f"Blocked user. Reason: {reason}"
    )
    
    return {"message": f"User {user.email} has been blocked", "reason": reason}

@router.post("/users/{user_id}/unblock")
def unblock_user(
    user_id: int,
    reason: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Unblock a user (superadmin only)"""
    require_superadmin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_blocked = False
    user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log the action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="unblock",
        resource_type="user",
        resource_id=user_id,
        resource_name=user.email,
        details=f"Unblocked user. Reason: {reason}"
    )
    
    return {"message": f"User {user.email} has been unblocked", "reason": reason}

@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    new_password: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reset user password (superadmin only)"""
    require_superadmin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # In a real implementation, you would hash the password
    # For now, we'll just update the password_hash field
    user.password_hash = f"hashed_{new_password}"  # This should be properly hashed
    user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log the action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="reset_password",
        resource_type="user",
        resource_id=user_id,
        resource_name=user.email,
        details="Password reset by superadmin"
    )
    
    return {"message": f"Password for user {user.email} has been reset"}

# Tenant Management Endpoints

@router.get("/tenants")
def list_all_tenants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None)
):
    """List all tenants (superadmin and analyst only)"""
    require_superadmin_or_analyst(current_user)
    
    query = db.query(Tenant)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(Tenant.company_name.ilike(search_term))
    
    total_count = query.count()
    tenants = query.offset(skip).limit(limit).all()
    
    # Log the action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="read",
        resource_type="tenant",
        details=f"Listed {len(tenants)} tenants",
        metadata={"total_count": total_count, "skip": skip, "limit": limit}
    )
    
    return {
        "tenants": [
            {
                "id": tenant.id,
                "company_name": tenant.company_name,
                "logo_url": tenant.logo_url,
                "created_at": tenant.created_at,
                "users_count": len(tenant.users),
                "products_count": len(tenant.products) if hasattr(tenant, 'products') else 0
            }
            for tenant in tenants
        ],
        "total_count": total_count,
        "skip": skip,
        "limit": limit
    }

@router.get("/tenants/{tenant_id}")
def get_tenant_details(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed tenant information (superadmin and analyst only)"""
    require_superadmin_or_analyst(current_user)
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Get users for this tenant
    users = db.query(User).filter(User.tenant_id == tenant_id).all()
    
    # Get products for this tenant
    products = db.query(Product).filter(Product.tenant_id == tenant_id).all()
    
    # Log the action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="read",
        resource_type="tenant",
        resource_id=tenant_id,
        resource_name=tenant.company_name
    )
    
    return {
        "id": tenant.id,
        "company_name": tenant.company_name,
        "logo_url": tenant.logo_url,
        "created_at": tenant.created_at,
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "is_blocked": user.is_blocked,
                "last_login": user.last_login
            }
            for user in users
        ],
        "products_count": len(products),
        "users_count": len(users)
    }

@router.put("/tenants/{tenant_id}")
def update_tenant(
    tenant_id: int,
    tenant_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update tenant (superadmin only)"""
    require_superadmin(current_user)
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Update fields
    if "company_name" in tenant_data:
        tenant.company_name = tenant_data["company_name"]
    if "logo_url" in tenant_data:
        tenant.logo_url = tenant_data["logo_url"]
    
    db.commit()
    db.refresh(tenant)
    
    # Log the action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="update",
        resource_type="tenant",
        resource_id=tenant_id,
        resource_name=tenant.company_name,
        details=f"Updated tenant fields: {list(tenant_data.keys())}"
    )
    
    return {
        "id": tenant.id,
        "company_name": tenant.company_name,
        "logo_url": tenant.logo_url,
        "created_at": tenant.created_at
    }

# Product Management Endpoints

@router.get("/products")
def list_all_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tenant_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None)
):
    """List all products (superadmin and analyst only)"""
    require_superadmin_or_analyst(current_user)
    
    query = db.query(Product)
    
    if tenant_id:
        query = query.filter(Product.tenant_id == tenant_id)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.sku_id.ilike(search_term),
                Product.manufacturer.ilike(search_term),
                Product.supplier.ilike(search_term)
            )
        )
    
    total_count = query.count()
    products = query.offset(skip).limit(limit).all()
    
    # Log the action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="read",
        resource_type="product",
        details=f"Listed {len(products)} products",
        metadata={"total_count": total_count, "skip": skip, "limit": limit}
    )
    
    return {
        "products": [
            {
                "id": product.id,
                "sku_id": product.sku_id,
                "tenant_id": product.tenant_id,
                "tenant_name": product.tenant.company_name if product.tenant else None,
                "category_id": product.category_id,
                "price": product.price,
                "manufacturer": product.manufacturer,
                "supplier": product.supplier,
                "image_url": product.image_url,
                "created_at": product.created_at,
                "updated_at": product.updated_at
            }
            for product in products
        ],
        "total_count": total_count,
        "skip": skip,
        "limit": limit
    }

# Audit Log Endpoints

@router.get("/audit-logs")
def get_audit_logs(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(100, ge=1, le=1000, description="Number of items per page (max 1000)"),
    skip: int = Query(None, description="Number of records to skip (deprecated, use page and page_size)"),
    limit: int = Query(None, description="Maximum number of records to return (deprecated, use page and page_size)"),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit logs with pagination (superadmin and analyst only)"""
    require_superadmin_or_analyst(current_user)
    
    # Handle deprecated skip/limit parameters
    if skip is not None or limit is not None:
        # Calculate page and page_size from skip/limit for backward compatibility
        if skip is not None and limit is not None:
            page = (skip // limit) + 1
            page_size = limit
        elif skip is not None:
            page = (skip // 100) + 1
            page_size = 100
        elif limit is not None:
            page = 1
            page_size = limit
    
    # Calculate actual skip and limit from page and page_size
    actual_skip = (page - 1) * page_size
    actual_limit = page_size
    
    query = db.query(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(AuditLog.created_at >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(AuditLog.created_at <= end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
    
    # Order by most recent first
    query = query.order_by(desc(AuditLog.created_at))
    
    total_count = query.count()
    audit_logs = query.offset(actual_skip).limit(actual_limit).all()
    
    return {
        "audit_logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "user_email": log.user.email if log.user else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "resource_name": log.resource_name,
                "details": log.details,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "metadata": log.audit_metadata,
                "created_at": log.created_at
            }
            for log in audit_logs
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size,
            "total_items": total_count,
            "has_next": page * page_size < total_count,
            "has_previous": page > 1,
            "next_page": page + 1 if page * page_size < total_count else None,
            "previous_page": page - 1 if page > 1 else None
        },
        "total_count": total_count,
        "skip": actual_skip,
        "limit": actual_limit
    }

# Dashboard Endpoints

@router.get("/dashboard")
def get_superadmin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get superadmin dashboard statistics"""
    require_superadmin_or_analyst(current_user)
    
    # Get counts
    total_users = db.query(User).count()
    total_tenants = db.query(Tenant).count()
    total_products = db.query(Product).count()
    total_categories = db.query(Category).count()
    
    # Get recent activity
    recent_audit_logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(10).all()
    
    # Get user statistics by role
    users_by_role = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    
    # Get blocked users count
    blocked_users_count = db.query(User).filter(User.is_blocked == True).count()
    
    # Log the action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="read",
        resource_type="dashboard",
        details="Accessed superadmin dashboard"
    )
    
    return {
        "statistics": {
            "total_users": total_users,
            "total_tenants": total_tenants,
            "total_products": total_products,
            "total_categories": total_categories,
            "blocked_users": blocked_users_count
        },
        "users_by_role": {role: count for role, count in users_by_role},
        "recent_activity": [
            {
                "id": log.id,
                "user_email": log.user.email if log.user else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_name": log.resource_name,
                "created_at": log.created_at
            }
            for log in recent_audit_logs
        ]
    } 