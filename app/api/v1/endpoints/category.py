from fastapi import APIRouter, Depends, Body, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.models.category import Category
from app.utils.csv_utils import parse_category_csv

router = APIRouter()

@router.post("/upload")
async def upload_category_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload category CSV file.
    
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
            # TODO: Set tenant_id from auth context in real app
            category = Category(
                name=category_data['name'],
                description=category_data.get('description', ''),
                schema_json=category_data.get('schema_json', {}),
                tenant_id=1  # TODO: Get from auth context
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
    schema_json: dict = Body({}),
    db: Session = Depends(get_db)
):
    # TODO: Set tenant_id from auth context in real app
    category = Category(name=name, description=description, schema_json=schema_json, tenant_id=1)
    db.add(category)
    db.commit()
    db.refresh(category)
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "schema_json": category.schema_json
    }

@router.get("")
def list_categories():
    # TODO: Implement list categories
    return {"msg": "List categories"}

@router.get("/{id}/schema")
def get_category_schema(id: int):
    # TODO: Implement get category schema
    return {"msg": f"Get schema for category {id}"}

@router.put("/{id}/schema")
def edit_category_schema(id: int):
    # TODO: Implement edit category schema
    return {"msg": f"Edit schema for category {id}"} 