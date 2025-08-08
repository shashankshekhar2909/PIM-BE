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
    q: Optional[str] = Query(None, alias="query", description="General search query across all searchable fields"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    # Field-specific search parameters (support comma-separated values)
    sku_id: Optional[str] = Query(None, description="Search in SKU ID field (comma-separated values: 'SKU1,SKU2')"),
    price: Optional[float] = Query(None, description="Search by exact price"),
    price_min: Optional[float] = Query(None, description="Minimum price filter"),
    price_max: Optional[float] = Query(None, description="Maximum price filter"),
    manufacturer: Optional[str] = Query(None, description="Search in manufacturer field (comma-separated values: 'Adidas,Apple,Bosch')"),
    supplier: Optional[str] = Query(None, description="Search in supplier field (comma-separated values: 'Supplier1,Supplier2')"),
    brand: Optional[str] = Query(None, description="Search in brand field (comma-separated values: 'Brand1,Brand2')"),
    # Dynamic field search (for additional data fields)
    field_name: Optional[str] = Query(None, description="Search in specific additional data field"),
    field_value: Optional[str] = Query(None, description="Value to search for in the specified field (comma-separated values: 'Value1,Value2')"),
    field_type: Optional[str] = Query(None, description="Filter by field type (primary, secondary, all)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search products with field-specific query parameters.
    
    Supports:
    - General search across all searchable fields (q or query parameter)
    - Field-specific search (sku_id, manufacturer, supplier, brand, etc.)
    - Multiple values per field using comma-separated values
    - Price range filtering (price_min, price_max)
    - Dynamic field search (field_name + field_value)
    - Category filtering
    - Field type filtering (primary, secondary, all)
    
    Only searches in fields marked as searchable in field configurations.
    """
    query = db.query(Product).filter(Product.tenant_id == current_user.tenant_id)
    
    # Apply category filter
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    # Get searchable field configurations
    searchable_configs_query = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id,
        FieldConfiguration.is_searchable == True
    )
    
    # Apply field type filter if specified
    if field_type and field_type.lower() in ['primary', 'secondary', 'all']:
        if field_type.lower() == 'primary':
            searchable_configs_query = searchable_configs_query.filter(FieldConfiguration.is_primary == True)
        elif field_type.lower() == 'secondary':
            searchable_configs_query = searchable_configs_query.filter(FieldConfiguration.is_secondary == True)
        # For 'all', no additional filter needed
    
    searchable_configs = searchable_configs_query.all()
    searchable_fields = [config.field_name for config in searchable_configs]
    
    # If no searchable fields configured and no search query provided, return empty results
    if not searchable_fields and not any([q, sku_id, manufacturer, supplier, brand, field_name, price, price_min, price_max]):
        return {
            "products": [],
            "total_count": 0,
            "skip": skip,
            "limit": limit,
            "query": q,
            "searchable_fields": [],
            "field_filters": {},
            "message": "No searchable fields configured"
        }
    
    # Build search conditions - use AND logic for multiple filters
    search_conditions = []
    field_filters = {}
    
    # Helper function to handle comma-separated values
    def split_comma_values(value):
        """Split comma-separated values and return list of trimmed values"""
        if not value or value.strip() == "":
            return []
        return [v.strip() for v in value.split(',') if v.strip()]
    
    # Helper function to validate numeric values
    def validate_numeric(value, field_name):
        """Validate and return numeric value, or None if invalid"""
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    # Field-specific search conditions with support for multiple values
    if sku_id and 'sku_id' in searchable_fields:
        sku_values = split_comma_values(sku_id)
        if sku_values:
            sku_conditions = [Product.sku_id.ilike(f"%{val}%") for val in sku_values]
            search_conditions.append(or_(*sku_conditions))
            field_filters["sku_id"] = sku_values
    
    if manufacturer and 'manufacturer' in searchable_fields:
        manufacturer_values = split_comma_values(manufacturer)
        if manufacturer_values:
            manufacturer_conditions = [Product.manufacturer.ilike(f"%{val}%") for val in manufacturer_values]
            search_conditions.append(or_(*manufacturer_conditions))
            field_filters["manufacturer"] = manufacturer_values
    
    if supplier and 'supplier' in searchable_fields:
        supplier_values = split_comma_values(supplier)
        if supplier_values:
            supplier_conditions = [Product.supplier.ilike(f"%{val}%") for val in supplier_values]
            search_conditions.append(or_(*supplier_conditions))
            field_filters["supplier"] = supplier_values
    
    # Price filtering
    validated_price = validate_numeric(price, "price")
    validated_price_min = validate_numeric(price_min, "price_min")
    validated_price_max = validate_numeric(price_max, "price_max")
    
    if validated_price is not None and 'price' in searchable_fields:
        search_conditions.append(Product.price == validated_price)
        field_filters["price"] = validated_price
    
    if validated_price_min is not None and 'price' in searchable_fields:
        search_conditions.append(Product.price >= validated_price_min)
        field_filters["price_min"] = validated_price_min
    
    if validated_price_max is not None and 'price' in searchable_fields:
        search_conditions.append(Product.price <= validated_price_max)
        field_filters["price_max"] = validated_price_max
    
    # Brand search (additional data field) - support multiple values
    if brand and 'brand' in searchable_fields:
        brand_values = split_comma_values(brand)
        if brand_values:
            brand_conditions = []
            for brand_val in brand_values:
                brand_query = db.query(ProductAdditionalData.product_id).filter(
                    ProductAdditionalData.field_name == 'brand',
                    ProductAdditionalData.field_value.ilike(f"%{brand_val}%")
                ).distinct()
                brand_product_ids = [row[0] for row in brand_query.all()]
                if brand_product_ids:
                    brand_conditions.extend(brand_product_ids)
            
            if brand_conditions:
                search_conditions.append(Product.id.in_(brand_conditions))
            field_filters["brand"] = brand_values
    
    # Dynamic field search - support multiple values
    if field_name and field_value and field_name in searchable_fields:
        field_values = split_comma_values(field_value)
        if field_values:
            field_conditions = []
            for field_val in field_values:
                dynamic_query = db.query(ProductAdditionalData.product_id).filter(
                    ProductAdditionalData.field_name == field_name,
                    ProductAdditionalData.field_value.ilike(f"%{field_val}%")
                ).distinct()
                dynamic_product_ids = [row[0] for row in dynamic_query.all()]
                if dynamic_product_ids:
                    field_conditions.extend(dynamic_product_ids)
            
            if field_conditions:
                search_conditions.append(Product.id.in_(field_conditions))
            field_filters[f"{field_name}"] = field_values
    
    # General search query (if no field-specific searches)
    if q and not any([sku_id, manufacturer, supplier, brand, field_name, price, price_min, price_max]):
        search_term = f"%{q}%"
        
        # Search in standard fields if they're searchable
        general_search_conditions = []
        
        if 'sku_id' in searchable_fields:
            general_search_conditions.append(Product.sku_id.ilike(search_term))
        if 'price' in searchable_fields:
            # Handle numeric search for price
            try:
                price_value = float(q)
                general_search_conditions.append(Product.price == price_value)
            except ValueError:
                # If not a number, search as string
                general_search_conditions.append(Product.price.cast(String).ilike(search_term))
        if 'manufacturer' in searchable_fields:
            general_search_conditions.append(Product.manufacturer.ilike(search_term))
        if 'supplier' in searchable_fields:
            general_search_conditions.append(Product.supplier.ilike(search_term))
        if 'image_url' in searchable_fields:
            general_search_conditions.append(Product.image_url.ilike(search_term))
        if 'category_id' in searchable_fields:
            try:
                category_value = int(q)
                general_search_conditions.append(Product.category_id == category_value)
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
                general_search_conditions.append(Product.id.in_(product_ids_with_matching_data))
        
        # For general search, use OR logic within the search term
        if general_search_conditions:
            search_conditions.append(or_(*general_search_conditions))
    
    # Apply search conditions using AND logic for multiple filters
    if search_conditions:
        query = query.filter(and_(*search_conditions))
    else:
        # If no search conditions and no searchable fields, return empty results
        if not searchable_fields:
            return {
                "products": [],
                "total_count": 0,
                "skip": skip,
                "limit": limit,
                "query": q,
                "searchable_fields": [],
                "field_filters": field_filters,
                "message": "No searchable fields configured"
            }
        # If search conditions were provided but none matched, return empty results
        elif any([q, sku_id, manufacturer, supplier, brand, field_name, price, price_min, price_max]):
            return {
                "products": [],
                "total_count": 0,
                "skip": skip,
                "limit": limit,
                "query": q,
                "searchable_fields": searchable_fields,
                "field_filters": field_filters,
                "message": "No products found matching the search criteria"
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