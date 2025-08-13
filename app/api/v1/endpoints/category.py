from fastapi import APIRouter, Depends, Body, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.category import Category
from app.models.user import User
from app.utils.csv_utils import parse_category_csv
from typing import List, Dict, Any
import json

router = APIRouter()

@router.post("/upload/load")
async def load_category_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Load and parse category CSV file for editing.
    This endpoint parses the CSV and returns formatted data without saving to database.
    
    Expected CSV columns:
    - name (required)
    - description (optional)
    - schema_json (optional, JSON string)
    """
    try:
        # Parse CSV file
        categories_data = parse_category_csv(file)
        
        # Format data for editing (add validation status and edit flags)
        formatted_categories = []
        for i, category_data in enumerate(categories_data):
            formatted_category = {
                "index": i,
                "name": category_data['name'],
                "description": category_data.get('description', ''),
                "schema_json": category_data.get('schema_json', {}),
                "validation_status": "valid",  # valid, warning, error
                "validation_errors": [],
                "is_edited": False
            }
            
            # Add validation checks
            validation_errors = []
            if not formatted_category['name']:
                validation_errors.append("Name is required")
            if len(formatted_category['name']) > 255:
                validation_errors.append("Name is too long (max 255 characters)")
            
            if validation_errors:
                formatted_category['validation_status'] = 'error'
                formatted_category['validation_errors'] = validation_errors
            
            formatted_categories.append(formatted_category)
        
        return {
            "msg": f"Successfully loaded {len(formatted_categories)} categories for editing",
            "categories": formatted_categories,
            "total_count": len(formatted_categories),
            "valid_count": len([c for c in formatted_categories if c['validation_status'] == 'valid']),
            "error_count": len([c for c in formatted_categories if c['validation_status'] == 'error']),
            "warning_count": len([c for c in formatted_categories if c['validation_status'] == 'warning'])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading categories: {str(e)}")

@router.post("/upload/save")
async def save_category_data(
    categories: List[Dict[str, Any]] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save formatted category data to database after editing.
    This endpoint accepts the edited category data and saves it to the database.
    """
    try:
        created_categories = []
        errors = []
        
        for category_data in categories:
            try:
                # Validate required fields
                if not category_data.get('name'):
                    errors.append(f"Category at index {category_data.get('index', 'unknown')}: Name is required")
                    continue
                
                # Check if category already exists
                existing_category = db.query(Category).filter(
                    Category.name == category_data['name'],
                    Category.tenant_id == current_user.tenant_id
                ).first()
                
                if existing_category:
                    errors.append(f"Category with name '{category_data['name']}' already exists")
                    continue
                
                # Create category
                category = Category(
                    name=category_data['name'],
                    description=category_data.get('description', ''),
                    schema_json=category_data.get('schema_json', {}),
                    tenant_id=current_user.tenant_id
                )
                db.add(category)
                created_categories.append(category)
                
            except Exception as e:
                errors.append(f"Error creating category {category_data.get('name', 'unknown')}: {str(e)}")
        
        if errors:
            db.rollback()
            return {
                "msg": f"Failed to save {len(errors)} categories",
                "errors": errors,
                "created_count": 0,
                "total_count": len(categories)
            }
        
        db.commit()
        
        # Return created categories
        return {
            "msg": f"Successfully saved {len(created_categories)} categories",
            "categories": [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "schema_json": c.schema_json
                }
                for c in created_categories
            ],
            "created_count": len(created_categories),
            "total_count": len(categories)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving categories: {str(e)}")

@router.post("/upload")
async def upload_category_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload category CSV file (legacy endpoint - now redirects to load/save flow).
    
    Expected CSV columns:
    - name (required)
    - description (optional)
    - schema_json (optional, JSON string)
    """
    try:
        # Parse CSV file
        categories_data = parse_category_csv(file)
        
        # Create categories in database
        created_categories = []
        for category_data in categories_data:
            # Check if category already exists
            existing_category = db.query(Category).filter(
                Category.name == category_data['name'],
                Category.tenant_id == current_user.tenant_id
            ).first()
            
            if existing_category:
                continue  # Skip existing categories
            
            category = Category(
                name=category_data['name'],
                description=category_data.get('description', ''),
                schema_json=category_data.get('schema_json', {}),
                tenant_id=current_user.tenant_id
            )
            db.add(category)
            created_categories.append(category)
        
        db.commit()
        
        # Return created categories
        return {
            "msg": f"Successfully uploaded {len(created_categories)} categories",
            "categories": [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "schema_json": c.schema_json
                }
                for c in created_categories
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading categories: {str(e)}")

@router.post("")
def create_category(
    name: str = Body(...),
    description: str = Body(""),
    schema_data: dict = Body({}, alias="schema_json"),  # Renamed to avoid Pydantic conflict
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new category.
    
    Args:
        name: Category name (required)
        description: Category description (optional)
        schema_data: JSON schema for the category (optional)
    """
    try:
        # Check if category already exists
        existing_category = db.query(Category).filter(
            Category.name == name,
            Category.tenant_id == current_user.tenant_id
        ).first()
        
        if existing_category:
            raise HTTPException(status_code=400, detail=f"Category with name '{name}' already exists")
        
        # Create new category
        category = Category(
            name=name,
            description=description,
            schema_json=schema_data,  # Use the renamed field
            tenant_id=current_user.tenant_id
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        
        return {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "schema_json": category.schema_json,
            "created_at": category.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create category: {str(e)}")

@router.get("")
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    search: str = None
):
    """
    List categories for the current user's tenant.
    Supports pagination and search.
    """
    query = db.query(Category).filter(Category.tenant_id == current_user.tenant_id)
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Category.name.ilike(search_term)) |
            (Category.description.ilike(search_term))
        )
    
    # Apply pagination
    total_count = query.count()
    categories = query.offset(skip).limit(limit).all()
    
    return {
        "categories": [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "schema_json": c.schema_json
            }
            for c in categories
        ],
        "total_count": total_count,
        "skip": skip,
        "limit": limit
    }

@router.get("/{id}")
def get_category(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific category by ID (tenant-scoped).
    """
    category = db.query(Category).filter(
        Category.id == id,
        Category.tenant_id == current_user.tenant_id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "schema_json": category.schema_json
    }

@router.put("/{id}")
def update_category(
    id: int,
    category_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific category by ID (tenant-scoped).
    """
    category = db.query(Category).filter(
        Category.id == id,
        Category.tenant_id == current_user.tenant_id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update fields
    if 'name' in category_data:
        # Check if name already exists for this tenant
        existing_category = db.query(Category).filter(
            Category.name == category_data['name'],
            Category.tenant_id == current_user.tenant_id,
            Category.id != id
        ).first()
        if existing_category:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        category.name = category_data['name']
    
    if 'description' in category_data:
        category.description = category_data['description']
    if 'schema_json' in category_data:
        category.schema_json = category_data['schema_json']
    
    db.commit()
    db.refresh(category)
    
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "schema_json": category.schema_json
    }

@router.delete("/{id}")
def delete_category(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific category by ID (tenant-scoped).
    """
    category = db.query(Category).filter(
        Category.id == id,
        Category.tenant_id == current_user.tenant_id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has products
    from app.models.product import Product
    product_count = db.query(Product).filter(Product.category_id == id).count()
    if product_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete category: {product_count} products are associated with this category"
        )
    
    db.delete(category)
    db.commit()
    
    return {"msg": "Category deleted successfully"}

@router.get("/{id}/schema")
def get_category_schema(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get schema for a specific category (tenant-scoped).
    """
    category = db.query(Category).filter(
        Category.id == id,
        Category.tenant_id == current_user.tenant_id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {
        "id": category.id,
        "name": category.name,
        "schema_json": category.schema_json
    }

@router.put("/{id}/schema")
def edit_category_schema(
    id: int,
    schema_data: dict = Body(..., alias="schema_json"),  # Renamed to avoid Pydantic conflict
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Edit category schema.
    
    Args:
        id: Category ID
        schema_data: New JSON schema for the category
    """
    try:
        # Get category
        category = db.query(Category).filter(
            Category.id == id,
            Category.tenant_id == current_user.tenant_id
        ).first()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Update schema
        category.schema_json = schema_data  # Use the renamed field
        db.commit()
        db.refresh(category)
        
        return {
            "id": category.id,
            "name": category.name,
            "schema_json": category.schema_json,
            "updated_at": category.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update category schema: {str(e)}")

@router.delete("/admin/{id}")
def delete_category_admin(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete any category by ID (superadmin only).
    This endpoint allows superadmin users to delete categories from any tenant.
    
    ⚠️  WARNING: This will permanently delete:
    - Category and all its data
    - All products in this category will have category_id set to NULL
    """
    # Only superadmin can delete any category
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Only superadmin users can delete any category")
    
    # Find the category to delete
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get category info for response
    category_info = {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "tenant_id": category.tenant_id
    }
    
    # Get tenant info if available
    from app.models.tenant import Tenant
    tenant = None
    if category.tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == category.tenant_id).first()
        if tenant:
            category_info["tenant_name"] = tenant.company_name
    
    # Check if category has products
    from app.models.product import Product
    product_count = db.query(Product).filter(Product.category_id == id).count()
    
    if product_count > 0:
        # Set category_id to NULL for all products in this category
        db.query(Product).filter(Product.category_id == id).update({Product.category_id: None})
        category_info["products_affected"] = product_count
        category_info["action"] = "Products unlinked from category"
    
    # Delete the category
    db.delete(category)
    db.commit()
    
    return {
        "message": f"Category '{category_info['name']}' deleted successfully",
        "deleted_category": category_info,
        "deleted_by": current_user.email,
        "products_affected": product_count if product_count > 0 else 0
    } 