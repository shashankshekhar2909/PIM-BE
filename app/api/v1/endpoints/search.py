from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, String, and_
from app.core.dependencies import get_db, get_current_user
from app.models.product import Product, ProductAdditionalData, FieldConfiguration
from app.models.user import User
from typing import List, Dict, Any, Optional

router = APIRouter()

@router.get("")
def search_products(
    q: Optional[str] = Query(None, description="General search query across all searchable fields"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    # Field-specific search parameters
    sku_id: Optional[str] = Query(None, description="Search in SKU ID field"),
    price: Optional[float] = Query(None, description="Search by exact price"),
    price_min: Optional[float] = Query(None, description="Minimum price filter"),
    price_max: Optional[float] = Query(None, description="Maximum price filter"),
    manufacturer: Optional[str] = Query(None, description="Search in manufacturer field"),
    supplier: Optional[str] = Query(None, description="Search in supplier field"),
    brand: Optional[str] = Query(None, description="Search in brand field (additional data)"),
    # Dynamic field search (for additional data fields)
    field_name: Optional[str] = Query(None, description="Search in specific additional data field"),
    field_value: Optional[str] = Query(None, description="Value to search for in the specified field"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search products with field-specific query parameters.
    
    Supports:
    - General search across all searchable fields (q parameter)
    - Field-specific search (sku_id, manufacturer, supplier, brand, etc.)
    - Price range filtering (price_min, price_max)
    - Dynamic field search (field_name + field_value)
    - Category filtering
    
    Only searches in fields marked as searchable in field configurations.
    """
    query = db.query(Product).filter(Product.tenant_id == current_user.tenant_id)
    
    # Apply category filter
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    # Get searchable field configurations
    searchable_configs = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id,
        FieldConfiguration.is_searchable == True
    ).all()
    
    searchable_fields = [config.field_name for config in searchable_configs]
    
    if not searchable_fields:
        # If no searchable fields configured, return empty results
        return {
            "products": [],
            "total_count": 0,
            "skip": skip,
            "limit": limit,
            "query": q,
            "searchable_fields": [],
            "field_filters": {}
        }
    
    # Build search conditions
    search_conditions = []
    field_filters = {}
    
    # Field-specific search conditions
    if sku_id and 'sku_id' in searchable_fields:
        search_conditions.append(Product.sku_id.ilike(f"%{sku_id}%"))
        field_filters["sku_id"] = sku_id
    
    if manufacturer and 'manufacturer' in searchable_fields:
        search_conditions.append(Product.manufacturer.ilike(f"%{manufacturer}%"))
        field_filters["manufacturer"] = manufacturer
    
    if supplier and 'supplier' in searchable_fields:
        search_conditions.append(Product.supplier.ilike(f"%{supplier}%"))
        field_filters["supplier"] = supplier
    
    # Price filtering
    if price is not None and 'price' in searchable_fields:
        search_conditions.append(Product.price == price)
        field_filters["price"] = price
    
    if price_min is not None and 'price' in searchable_fields:
        search_conditions.append(Product.price >= price_min)
        field_filters["price_min"] = price_min
    
    if price_max is not None and 'price' in searchable_fields:
        search_conditions.append(Product.price <= price_max)
        field_filters["price_max"] = price_max
    
    # Brand search (additional data field)
    if brand and 'brand' in searchable_fields:
        brand_query = db.query(ProductAdditionalData.product_id).filter(
            ProductAdditionalData.field_name == 'brand',
            ProductAdditionalData.field_value.ilike(f"%{brand}%")
        ).distinct()
        brand_product_ids = [row[0] for row in brand_query.all()]
        if brand_product_ids:
            search_conditions.append(Product.id.in_(brand_product_ids))
        field_filters["brand"] = brand
    
    # Dynamic field search
    if field_name and field_value and field_name in searchable_fields:
        dynamic_query = db.query(ProductAdditionalData.product_id).filter(
            ProductAdditionalData.field_name == field_name,
            ProductAdditionalData.field_value.ilike(f"%{field_value}%")
        ).distinct()
        dynamic_product_ids = [row[0] for row in dynamic_query.all()]
        if dynamic_product_ids:
            search_conditions.append(Product.id.in_(dynamic_product_ids))
        field_filters[f"{field_name}"] = field_value
    
    # General search query (if no field-specific searches)
    if q and not any([sku_id, manufacturer, supplier, brand, field_name, price, price_min, price_max]):
        search_term = f"%{q}%"
        
        # Search in standard fields if they're searchable
        if 'sku_id' in searchable_fields:
            search_conditions.append(Product.sku_id.ilike(search_term))
        if 'price' in searchable_fields:
            # Handle numeric search for price
            try:
                price_value = float(q)
                search_conditions.append(Product.price == price_value)
            except ValueError:
                # If not a number, search as string
                search_conditions.append(Product.price.cast(String).ilike(search_term))
        if 'manufacturer' in searchable_fields:
            search_conditions.append(Product.manufacturer.ilike(search_term))
        if 'supplier' in searchable_fields:
            search_conditions.append(Product.supplier.ilike(search_term))
        if 'image_url' in searchable_fields:
            search_conditions.append(Product.image_url.ilike(search_term))
        if 'category_id' in searchable_fields:
            try:
                category_value = int(q)
                search_conditions.append(Product.category_id == category_value)
            except ValueError:
                # If not a number, skip category search
                pass
        
        # Search in additional data if fields are searchable
        if searchable_fields:
            # Get products with matching additional data
            additional_data_query = db.query(ProductAdditionalData.product_id).filter(
                ProductAdditionalData.field_name.in_(searchable_fields),
                ProductAdditionalData.field_value.ilike(search_term)
            ).distinct()
            
            product_ids_with_matching_data = [row[0] for row in additional_data_query.all()]
            if product_ids_with_matching_data:
                search_conditions.append(Product.id.in_(product_ids_with_matching_data))
    
    # Apply search conditions
    if search_conditions:
        query = query.filter(or_(*search_conditions))
    else:
        # If no search conditions, return empty results
        return {
            "products": [],
            "total_count": 0,
            "skip": skip,
            "limit": limit,
            "query": q,
            "searchable_fields": searchable_fields,
            "field_filters": field_filters
        }
    
    # Apply pagination
    total_count = query.count()
    products = query.offset(skip).limit(limit).all()
    
    return {
        "products": [
            {
                "id": p.id,
                "sku_id": p.sku_id,
                "category_id": p.category_id,
                "price": p.price,
                "manufacturer": p.manufacturer,
                "supplier": p.supplier,
                "image_url": p.image_url,
                "additional_data_count": len(p.additional_data)
            }
            for p in products
        ],
        "total_count": total_count,
        "skip": skip,
        "limit": limit,
        "query": q,
        "searchable_fields": searchable_fields,
        "field_filters": field_filters
    }

@router.post("/index/init")
def init_index():
    """
    Initialize search index (no-op for simple search implementation).
    """
    return {"msg": "Search index initialized (simple search implementation)"}

@router.post("/reindex")
def reindex():
    """
    Reindex search data (no-op for simple search implementation).
    """
    return {"msg": "Search reindexed (simple search implementation)"} 