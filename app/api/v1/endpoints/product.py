from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, String, func, and_
from app.core.dependencies import get_db, get_current_user
from app.models.product import Product, ProductAdditionalData, FieldMapping, FieldConfiguration
from app.models.user import User
from app.utils.ai_csv_utils import AICSVProcessor
from typing import List, Dict, Any, Set, Optional
import json
from app.models.category import Category
from app.models.misc import Favorite, CompareList
from app.models.tenant import Tenant

router = APIRouter()

# Maximum product limit for this version
MAX_PRODUCTS_LIMIT = 500

def get_actual_fields_for_tenant(db: Session, tenant_id: int) -> Set[str]:
    """
    Get all actual fields that exist in the tenant's product data.
    
    Args:
        db: Database session
        tenant_id: Tenant ID
    
    Returns:
        Set of field names that actually exist in the tenant's data
    """
    actual_fields = set()
    
    # Get standard fields that exist in products
    products = db.query(Product).filter(Product.tenant_id == tenant_id).all()
    
    for product in products:
        # Add standard fields that have values
        if product.sku_id:
            actual_fields.add('sku_id')
        if product.price is not None:
            actual_fields.add('price')
        if product.manufacturer:
            actual_fields.add('manufacturer')
        if product.supplier:
            actual_fields.add('supplier')
        if product.image_url:
            actual_fields.add('image_url')
        if product.category_id:
            actual_fields.add('category_id')
    
    # Get additional data fields that exist in products
    if products:
        additional_data_fields = db.query(ProductAdditionalData.field_name).filter(
            ProductAdditionalData.product_id.in_([p.id for p in products])
        ).distinct().all()
        
        for field in additional_data_fields:
            actual_fields.add(field[0])
    
    return actual_fields

@router.post("/upload/analyze")
async def analyze_and_load_product_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze uploaded file using AI and load product data for editing.
    This endpoint only analyzes and loads data for editing - no data is saved to database.
    
    Features:
    - AI-powered file analysis and field normalization
    - Automatic data validation and quality assessment
    - Product limit enforcement (max 500 products)
    - Field mapping and additional data handling
    - Data returned for editing only (not saved to database)
    """
    try:
        processor = AICSVProcessor()
        
        # Step 1: Analyze the file using AI
        analysis_result = processor.analyze_file(file)
        
        # Step 2: Process file with AI mappings
        products_data = processor.process_file_with_mappings(file, analysis_result['analysis'].get('field_mappings', []))
        
        # Step 3: Enforce product limit
        if len(products_data) > MAX_PRODUCTS_LIMIT:
            raise HTTPException(
                status_code=400, 
                detail=f"Product limit exceeded. Maximum {MAX_PRODUCTS_LIMIT} products allowed. Found {len(products_data)} products."
            )
        
        # Step 4: Validate processed data (no database operations)
        validation_results = processor.validate_processed_data(products_data)
        
        return {
            "msg": f"Successfully analyzed and loaded {len(products_data)} products for editing (AI-enhanced)",
            "file_name": analysis_result['file_name'],
            "total_rows": analysis_result['total_rows'],
            "headers": analysis_result['headers'],
            "products": products_data,
            "total_count": len(products_data),
            "valid_count": len([p for p in products_data if p['validation_status'] == 'valid']),
            "error_count": len([p for p in products_data if p['validation_status'] == 'error']),
            "warning_count": len([p for p in products_data if p['validation_status'] == 'warning']),
            "field_mappings": analysis_result['analysis'].get('field_mappings', []),
            "validation_results": validation_results,
            "analysis": analysis_result['analysis']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis and loading failed: {str(e)}")

@router.post("/upload")
async def upload_and_save_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload product CSV/Excel file and save to database using AI processing.
    This endpoint combines AI analysis, data processing, and saving in a single step.
    
    Features:
    - AI-powered file analysis and field normalization
    - Automatic data validation and quality assessment
    - Product limit enforcement (max 500 products)
    - Direct saving to database
    - Additional data handling
    
    Expected CSV columns:
    - sku_id (required)
    - category_id (optional)
    - price (optional)
    - manufacturer (optional)
    - supplier (optional)
    - image_url (optional)
    - Any additional fields (handled automatically by AI)
    """
    try:
        processor = AICSVProcessor()
        
        # Step 1: Analyze the file using AI
        analysis_result = processor.analyze_file(file)
        
        # Step 2: Process file with AI mappings
        products_data = processor.process_file_with_mappings(file, analysis_result['analysis'].get('field_mappings', []))
        
        # Step 3: Enforce product limit
        if len(products_data) > MAX_PRODUCTS_LIMIT:
            raise HTTPException(
                status_code=400, 
                detail=f"Product limit exceeded. Maximum {MAX_PRODUCTS_LIMIT} products allowed. Found {len(products_data)} products."
            )
        
        # Step 4: Store field mappings in database
        field_mappings = analysis_result['analysis'].get('field_mappings', [])
        stored_mappings = []
        
        for mapping in field_mappings:
            field_mapping = FieldMapping(
                tenant_id=current_user.tenant_id,
                original_field_name=mapping['original_field_name'],
                normalized_field_name=mapping['normalized_field_name'],
                field_label=mapping['field_label'],
                field_type=mapping['field_type'],
                is_standard_field=1 if mapping.get('is_standard_field', False) else 0
            )
            db.add(field_mapping)
            stored_mappings.append(field_mapping)
        
        # Step 5: Save products to database
        created_products = []
        errors = []
        
        for product_data in products_data:
            try:
                # Validate required fields
                if not product_data.get('sku_id'):
                    errors.append(f"Product at index {product_data.get('index', 'unknown')}: SKU ID is required")
                    continue
                
                # Check if product already exists
                existing_product = db.query(Product).filter(
                    Product.sku_id == product_data['sku_id'],
                    Product.tenant_id == current_user.tenant_id
                ).first()
                
                if existing_product:
                    errors.append(f"Product with SKU {product_data['sku_id']} already exists")
                    continue
                
                # Create product
                product = Product(
                    sku_id=product_data['sku_id'],
                    category_id=product_data.get('category_id'),
                    price=product_data.get('price'),
                    manufacturer=product_data.get('manufacturer', ''),
                    supplier=product_data.get('supplier', ''),
                    image_url=product_data.get('image_url', ''),
                    tenant_id=current_user.tenant_id
                )
                db.add(product)
                db.flush()  # Get the product ID
                
                # Save additional data
                additional_data = product_data.get('additional_data', [])
                for additional_item in additional_data:
                    additional_data_obj = ProductAdditionalData(
                        product_id=product.id,
                        field_name=additional_item['field_name'],
                        field_label=additional_item['field_label'],
                        field_value=additional_item['field_value'],
                        field_type=additional_item['field_type']
                    )
                    db.add(additional_data_obj)
                
                created_products.append(product)
                
            except Exception as e:
                errors.append(f"Error creating product {product_data.get('sku_id', 'unknown')}: {str(e)}")
        
        if errors:
            db.rollback()
            return {
                "msg": f"Failed to save {len(errors)} products",
                "errors": errors,
                "created_count": 0,
                "total_count": len(products_data)
            }
        
        db.commit()
        
        # Return created products
        return {
            "msg": f"Successfully uploaded and saved {len(created_products)} products (AI-enhanced)",
            "file_name": analysis_result['file_name'],
            "total_rows": analysis_result['total_rows'],
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
                for p in created_products
            ],
            "created_count": len(created_products),
            "total_count": len(products_data),
            "field_mappings": [
                {
                    "id": m.id,
                    "original_field_name": m.original_field_name,
                    "normalized_field_name": m.normalized_field_name,
                    "field_label": m.field_label,
                    "field_type": m.field_type,
                    "is_standard_field": bool(m.is_standard_field)
                }
                for m in stored_mappings
            ],
            "analysis": analysis_result['analysis']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading and saving products: {str(e)}")

@router.get("")
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(100, ge=1, le=500, description="Number of items per page (max 500)"),
    skip: int = Query(None, description="Number of records to skip (deprecated, use page and page_size)"),
    limit: int = Query(None, description="Maximum number of records to return (deprecated, use page and page_size)"),
    category_id: int = None,
    search: str = None,
    primary_only: bool = False,
    secondary_only: bool = False,
    field_type: str = None,  # "primary", "secondary", "all", or None for all
    # Field-specific search parameters (support comma-separated values)
    sku_id: str = None,
    price: float = None,
    price_min: float = None,
    price_max: float = None,
    manufacturer: str = None,  # Comma-separated values: "Adidas,Apple,Bosch"
    supplier: str = None,      # Comma-separated values: "Supplier1,Supplier2"
    brand: str = None,         # Comma-separated values: "Brand1,Brand2"
    # Dynamic field search (for additional data fields)
    field_name: str = None,
    field_value: str = None    # Comma-separated values: "Value1,Value2"
):
    """
    List products for the current user's tenant.
    Supports pagination, category filtering, search, field type filtering, and field-specific search.
    
    Args:
        page: Page number (starts from 1)
        page_size: Number of items per page (max 500)
        skip: Number of records to skip (deprecated, use page and page_size)
        limit: Maximum number of records to return (deprecated, use page and page_size)
        category_id: Filter by category ID
        search: General search term (only searches in searchable fields)
        primary_only: If true, only return products with primary fields (deprecated, use field_type="primary")
        secondary_only: If true, only return products with secondary fields (deprecated, use field_type="secondary")
        field_type: Filter by field type - "primary", "secondary", "all", or None for all fields
        sku_id: Search in SKU ID field (comma-separated values supported)
        price: Search by exact price
        price_min: Minimum price filter
        price_max: Maximum price filter
        manufacturer: Search in manufacturer field (comma-separated values: "Adidas,Apple,Bosch")
        supplier: Search in supplier field (comma-separated values: "Supplier1,Supplier2")
        brand: Search in brand field (comma-separated values: "Brand1,Brand2")
        field_name: Search in specific additional data field
        field_value: Value to search for in the specified field (comma-separated values: "Value1,Value2")
    """
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
    
    # Validate field_type parameter
    if field_type and field_type.lower() not in ["primary", "secondary", "all"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid field_type. Must be one of: 'primary', 'secondary', 'all'"
        )
    
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
    
    # Build search conditions - use AND logic for multiple filters
    search_conditions = []
    
    # Helper function to handle comma-separated values
    def split_comma_values(value):
        """Split comma-separated values and return list of trimmed values"""
        if not value:
            return []
        return [v.strip() for v in value.split(',') if v.strip()]
    
    # Field-specific search conditions with support for multiple values
    if sku_id and 'sku_id' in searchable_fields:
        sku_values = split_comma_values(sku_id)
        if sku_values:
            sku_conditions = [Product.sku_id.ilike(f"%{val}%") for val in sku_values]
            from sqlalchemy import or_
            search_conditions.append(or_(*sku_conditions))
    
    if manufacturer and 'manufacturer' in searchable_fields:
        manufacturer_values = split_comma_values(manufacturer)
        if manufacturer_values:
            manufacturer_conditions = [Product.manufacturer.ilike(f"%{val}%") for val in manufacturer_values]
            from sqlalchemy import or_
            search_conditions.append(or_(*manufacturer_conditions))
    
    if supplier and 'supplier' in searchable_fields:
        supplier_values = split_comma_values(supplier)
        if supplier_values:
            supplier_conditions = [Product.supplier.ilike(f"%{val}%") for val in supplier_values]
            from sqlalchemy import or_
            search_conditions.append(or_(*supplier_conditions))
    
    # Price filtering
    if price is not None and 'price' in searchable_fields:
        search_conditions.append(Product.price == price)
    
    if price_min is not None and 'price' in searchable_fields:
        search_conditions.append(Product.price >= price_min)
    
    if price_max is not None and 'price' in searchable_fields:
        search_conditions.append(Product.price <= price_max)
    
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
    
    # General search query (if no field-specific searches)
    if search and not any([sku_id, manufacturer, supplier, brand, field_name, price, price_min, price_max]):
        search_term = f"%{search}%"
        
        # Search in standard fields if they're searchable
        general_search_conditions = []
        
        if 'sku_id' in searchable_fields:
            general_search_conditions.append(Product.sku_id.ilike(search_term))
        if 'price' in searchable_fields:
            # Handle numeric search for price
            try:
                price_value = float(search)
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
                category_value = int(search)
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
        from sqlalchemy import and_
        query = query.filter(and_(*search_conditions))
    else:
        # If search was provided but no searchable fields configured, return empty results
        if search and not searchable_fields:
            return {
                "products": [],
                "total_count": 0,
                "skip": skip,
                "limit": limit,
                "searchable_fields": [],
                "message": "No searchable fields configured"
            }
        # If search conditions were provided but none matched, return empty results
        elif any([search, sku_id, manufacturer, supplier, brand, field_name, price, price_min, price_max]) and not search_conditions:
            return {
                "products": [],
                "total_count": 0,
                "skip": skip,
                "limit": limit,
                "searchable_fields": searchable_fields,
                "message": "No products found matching the search criteria"
            }
    
    # Apply field type filtering
    if field_type or primary_only or secondary_only:
        # Determine field type to filter by
        if field_type:
            filter_type = field_type.lower()
        elif primary_only:
            filter_type = "primary"
        elif secondary_only:
            filter_type = "secondary"
        else:
            filter_type = "all"
        
        if filter_type in ["primary", "secondary"]:
            # Get field configurations for the specified type
            field_configs = db.query(FieldConfiguration).filter(
                FieldConfiguration.tenant_id == current_user.tenant_id,
                FieldConfiguration.is_primary == (filter_type == "primary"),
                FieldConfiguration.is_secondary == (filter_type == "secondary")
            ).all()
            
            field_names = [config.field_name for config in field_configs]
            
            if field_names:
                # Filter products that have values in the specified field type
                field_conditions = []
                
                # Check standard fields
                if 'sku_id' in field_names:
                    field_conditions.append(Product.sku_id.isnot(None))
                if 'price' in field_names:
                    field_conditions.append(Product.price.isnot(None))
                if 'manufacturer' in field_names:
                    field_conditions.append(Product.manufacturer.isnot(None))
                if 'supplier' in field_names:
                    field_conditions.append(Product.supplier.isnot(None))
                
                # Check additional data fields
                if field_names:
                    additional_field_query = db.query(ProductAdditionalData.product_id).filter(
                        ProductAdditionalData.field_name.in_(field_names),
                        ProductAdditionalData.field_value.isnot(None)
                    ).distinct()
                    
                    product_ids_with_field_data = [row[0] for row in additional_field_query.all()]
                    if product_ids_with_field_data:
                        field_conditions.append(Product.id.in_(product_ids_with_field_data))
                
                if field_conditions:
                    from sqlalchemy import or_
                    query = query.filter(or_(*field_conditions))
        elif filter_type == "all":
            # For "all" type, we don't apply any field type filtering - return all products
            pass
    
    # Apply pagination
    total_count = query.count()
    products = query.offset(actual_skip).limit(actual_limit).all()
    
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
        "limit": actual_limit,
        "field_type": field_type or ("primary" if primary_only else "secondary" if secondary_only else "all")
    }

@router.get("/search")
def search_products(
    q: Optional[str] = Query(None, alias="query", description="General search query across all searchable fields"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(100, ge=1, le=500, description="Number of items per page (max 500)"),
    skip: int = Query(None, description="Number of records to skip (deprecated, use page and page_size)"),
    limit: int = Query(None, description="Maximum number of records to return (deprecated, use page and page_size)"),
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
    - Pagination with page and page_size parameters
    
    Only searches in fields marked as searchable in field configurations.
    """
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
    
    # If no searchable fields configured and no search query provided, return empty results
    if not searchable_fields and not any([q, sku_id, manufacturer, supplier, brand, field_name, price, price_min, price_max]):
        return {
            "products": [],
            "total_count": 0,
            "skip": actual_skip,
            "limit": actual_limit,
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
        from sqlalchemy import and_
        query = query.filter(and_(*search_conditions))
    else:
        # If no search conditions and no searchable fields, return empty results
        if not searchable_fields:
            return {
                "products": [],
                "total_count": 0,
                "skip": actual_skip,
                "limit": actual_limit,
                "query": q,
                "searchable_fields": [],
                "field_filters": {},
                "message": "No searchable fields configured"
            }
        # If search conditions were provided but none matched, return empty results
        elif any([q, sku_id, manufacturer, supplier, brand, field_name, price, price_min, price_max]):
            return {
                "products": [],
                "total_count": 0,
                "skip": actual_skip,
                "limit": actual_limit,
                "query": q,
                "searchable_fields": searchable_fields,
                "field_filters": field_filters,
                "message": "No products found matching the search criteria"
            }
    
    # Apply pagination
    total_count = query.count()
    products = query.offset(actual_skip).limit(actual_limit).all()
    
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
        "limit": actual_limit,
        "query": q,
        "searchable_fields": searchable_fields,
        "field_filters": field_filters
    }

@router.get("/filters")
def get_filters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all available filters for search functionality.
    This is the main filters endpoint that returns all unique filter data.
    Alias for /filters/all for frontend compatibility.
    """
    # Get searchable field configurations
    searchable_configs = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id,
        FieldConfiguration.is_searchable == True
    ).all()
    
    searchable_fields = [config.field_name for config in searchable_configs]
    
    if not searchable_fields:
        return {
            "filters": {},
            "searchable_fields": [],
            "total_filters": 0
        }
    
    filters = {}
    
    # Get unique values for standard fields
    if 'sku_id' in searchable_fields:
        sku_ids = db.query(Product.sku_id).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.sku_id.isnot(None),
            Product.sku_id != ""
        ).distinct().all()
        filters['sku_id'] = sorted([item[0] for item in sku_ids if item[0]])
    
    if 'manufacturer' in searchable_fields:
        manufacturers = db.query(Product.manufacturer).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.manufacturer.isnot(None),
            Product.manufacturer != ""
        ).distinct().all()
        filters['manufacturer'] = sorted([item[0] for item in manufacturers if item[0]])
    
    if 'supplier' in searchable_fields:
        suppliers = db.query(Product.supplier).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.supplier.isnot(None),
            Product.supplier != ""
        ).distinct().all()
        filters['supplier'] = sorted([item[0] for item in suppliers if item[0]])
    
    if 'price' in searchable_fields:
        prices = db.query(Product.price).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.price.isnot(None)
        ).distinct().all()
        filters['price'] = sorted([float(item[0]) for item in prices if item[0] is not None])
        
        # Also get price range
        price_stats = db.query(
            func.min(Product.price),
            func.max(Product.price)
        ).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.price.isnot(None)
        ).first()
        
        min_price = float(price_stats[0]) if price_stats[0] is not None else 0
        max_price = float(price_stats[1]) if price_stats[1] is not None else 0
        
        filters['price_range'] = {
            "min": min_price,
            "max": max_price,
            "currency": "USD"
        }
    
    if 'category_id' in searchable_fields:
        category_ids = db.query(Product.category_id).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.category_id.isnot(None)
        ).distinct().all()
        filters['category_id'] = [item[0] for item in category_ids if item[0]]
        
        # Also get category names
        if category_ids:
            category_names = db.query(Category.id, Category.name, Category.description).filter(
                Category.id.in_([item[0] for item in category_ids if item[0]])
            ).all()
            filters['categories'] = sorted(
                [{"id": cat[0], "name": cat[1], "description": cat[2]} for cat in category_names],
                key=lambda x: x['name']
            )
    
    # Get unique values for additional data fields
    additional_fields = [field for field in searchable_fields if field not in ['sku_id', 'manufacturer', 'supplier', 'price', 'category_id', 'image_url']]
    
    for field_name in additional_fields:
        field_values = db.query(ProductAdditionalData.field_value).filter(
            ProductAdditionalData.field_name == field_name,
            ProductAdditionalData.product_id.in_(
                db.query(Product.id).filter(Product.tenant_id == current_user.tenant_id)
            ),
            ProductAdditionalData.field_value.isnot(None),
            ProductAdditionalData.field_value != ""
        ).distinct().all()
        
        filters[field_name] = sorted([item[0] for item in field_values if item[0]])
    
    return {
        "filters": filters,
        "searchable_fields": searchable_fields,
        "total_filters": len(filters),
        "field_counts": {
            field: len(values) if isinstance(values, list) else 1
            for field, values in filters.items()
        }
    }

@router.get("/{id}")
def get_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific product by ID (tenant-scoped) with all fields and additional data.
    """
    product = db.query(Product).filter(
        Product.id == id,
        Product.tenant_id == current_user.tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get field configurations for this tenant
    field_configs = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id
    ).all()
    
    # Create a mapping of field names to configurations
    field_config_map = {config.field_name: config for config in field_configs}
    
    # Prepare additional data with field configurations
    additional_data = []
    for additional in product.additional_data:
        field_config = field_config_map.get(additional.field_name)
        additional_data.append({
            "id": additional.id,
            "field_name": additional.field_name,
            "field_label": additional.field_label,
            "field_value": additional.field_value,
            "field_type": additional.field_type,
            "is_searchable": field_config.is_searchable if field_config else False,
            "is_editable": field_config.is_editable if field_config else True,
            "is_primary": field_config.is_primary if field_config else False,
            "is_secondary": field_config.is_secondary if field_config else False,
            "created_at": additional.created_at,
            "updated_at": additional.updated_at
        })
    
    # Get category information if available
    category_info = None
    if product.category_id:
        category = db.query(Category).filter(Category.id == product.category_id).first()
        if category:
            category_info = {
                "id": category.id,
                "name": category.name,
                "description": category.description
            }
    
    return {
        "id": product.id,
        "sku_id": product.sku_id,
        "category_id": product.category_id,
        "category": category_info,
        "price": product.price,
        "manufacturer": product.manufacturer,
        "supplier": product.supplier,
        "image_url": product.image_url,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "additional_data": additional_data,
        "additional_data_count": len(additional_data),
        "field_configurations": {
            "sku_id": {
                "is_searchable": field_config_map.get('sku_id').is_searchable if field_config_map.get('sku_id') else False,
                "is_editable": field_config_map.get('sku_id').is_editable if field_config_map.get('sku_id') else True,
                "is_primary": field_config_map.get('sku_id').is_primary if field_config_map.get('sku_id') else False,
                "is_secondary": field_config_map.get('sku_id').is_secondary if field_config_map.get('sku_id') else False
            },
            "price": {
                "is_searchable": field_config_map.get('price').is_searchable if field_config_map.get('price') else False,
                "is_editable": field_config_map.get('price').is_editable if field_config_map.get('price') else True,
                "is_primary": field_config_map.get('price').is_primary if field_config_map.get('price') else False,
                "is_secondary": field_config_map.get('price').is_secondary if field_config_map.get('price') else False
            },
            "manufacturer": {
                "is_searchable": field_config_map.get('manufacturer').is_searchable if field_config_map.get('manufacturer') else False,
                "is_editable": field_config_map.get('manufacturer').is_editable if field_config_map.get('manufacturer') else True,
                "is_primary": field_config_map.get('manufacturer').is_primary if field_config_map.get('manufacturer') else False,
                "is_secondary": field_config_map.get('manufacturer').is_secondary if field_config_map.get('manufacturer') else False
            },
            "supplier": {
                "is_searchable": field_config_map.get('supplier').is_searchable if field_config_map.get('supplier') else False,
                "is_editable": field_config_map.get('supplier').is_editable if field_config_map.get('supplier') else True,
                "is_primary": field_config_map.get('supplier').is_primary if field_config_map.get('supplier') else False,
                "is_secondary": field_config_map.get('supplier').is_secondary if field_config_map.get('supplier') else False
            }
        }
    }

@router.put("/{id}")
def update_product(
    id: int,
    product_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific product by ID (tenant-scoped).
    Only editable fields can be updated.
    """
    product = db.query(Product).filter(
        Product.id == id,
        Product.tenant_id == current_user.tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get editable field configurations
    editable_configs = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id,
        FieldConfiguration.is_editable == True
    ).all()
    
    editable_fields = {config.field_name for config in editable_configs}
    
    # Validate that only editable fields are being updated
    non_editable_fields = []
    for field_name in product_data.keys():
        if field_name not in editable_fields and field_name not in ['id', 'tenant_id', 'created_at', 'updated_at']:
            non_editable_fields.append(field_name)
    
    if non_editable_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"The following fields are not editable: {', '.join(non_editable_fields)}"
        )
    
    # Update fields (only if they're editable)
    if 'sku_id' in product_data and 'sku_id' in editable_fields:
        # Check if SKU already exists for this tenant
        existing_product = db.query(Product).filter(
            Product.sku_id == product_data['sku_id'],
            Product.tenant_id == current_user.tenant_id,
            Product.id != id
        ).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="SKU ID already exists")
        product.sku_id = product_data['sku_id']
    
    if 'category_id' in product_data and 'category_id' in editable_fields:
        product.category_id = product_data['category_id']
    if 'price' in product_data and 'price' in editable_fields:
        product.price = product_data['price']
    if 'manufacturer' in product_data and 'manufacturer' in editable_fields:
        product.manufacturer = product_data['manufacturer']
    if 'supplier' in product_data and 'supplier' in editable_fields:
        product.supplier = product_data['supplier']
    if 'image_url' in product_data and 'image_url' in editable_fields:
        product.image_url = product_data['image_url']
    
    # Handle additional data updates
    if 'additional_data' in product_data:
        # Get editable additional data fields
        editable_additional_fields = [config.field_name for config in editable_configs if not config.field_name in ['sku_id', 'category_id', 'price', 'manufacturer', 'supplier', 'image_url']]
        
        for additional_item in product_data['additional_data']:
            field_name = additional_item.get('field_name')
            if field_name in editable_additional_fields:
                # Update or create additional data
                existing_additional = db.query(ProductAdditionalData).filter(
                    ProductAdditionalData.product_id == product.id,
                    ProductAdditionalData.field_name == field_name
                ).first()
                
                if existing_additional:
                    existing_additional.field_value = additional_item.get('field_value', '')
                    existing_additional.field_label = additional_item.get('field_label', existing_additional.field_label)
                    existing_additional.field_type = additional_item.get('field_type', existing_additional.field_type)
                else:
                    new_additional = ProductAdditionalData(
                        product_id=product.id,
                        field_name=field_name,
                        field_label=additional_item.get('field_label', field_name),
                        field_value=additional_item.get('field_value', ''),
                        field_type=additional_item.get('field_type', 'string')
                    )
                    db.add(new_additional)
    
    db.commit()
    db.refresh(product)
    
    return {
        "id": product.id,
        "sku_id": product.sku_id,
        "category_id": product.category_id,
        "price": product.price,
        "manufacturer": product.manufacturer,
        "supplier": product.supplier,
        "image_url": product.image_url,
        "additional_data_count": len(product.additional_data)
    }

@router.delete("/{id}")
def delete_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific product by ID (tenant-scoped).
    """
    product = db.query(Product).filter(
        Product.id == id,
        Product.tenant_id == current_user.tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    
    return {"msg": "Product deleted successfully"}

@router.post("/{id}/favorite")
def favorite_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a product to user's favorites (wishlist).
    """
    # Check if product exists and belongs to tenant
    product = db.query(Product).filter(
        Product.id == id,
        Product.tenant_id == current_user.tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if already favorited
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.product_id == id
    ).first()
    
    if existing_favorite:
        raise HTTPException(status_code=400, detail="Product already in favorites")
    
    # Add to favorites
    favorite = Favorite(
        user_id=current_user.id,
        product_id=id
    )
    db.add(favorite)
    db.commit()
    
    return {"msg": f"Product {id} added to favorites"}

@router.delete("/{id}/favorite")
def unfavorite_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a product from user's favorites (wishlist).
    """
    # Check if product exists and belongs to tenant
    product = db.query(Product).filter(
        Product.id == id,
        Product.tenant_id == current_user.tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if favorited
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.product_id == id
    ).first()
    
    if not existing_favorite:
        raise HTTPException(status_code=400, detail="Product not in favorites")
    
    # Remove from favorites
    db.delete(existing_favorite)
    db.commit()
    
    return {"msg": f"Product {id} removed from favorites"}

@router.get("/favorites")
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Get user's favorite products (wishlist).
    """
    # Get favorite products
    favorites = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    # Get product details
    product_ids = [f.product_id for f in favorites]
    products = db.query(Product).filter(
        Product.id.in_(product_ids),
        Product.tenant_id == current_user.tenant_id
    ).all()
    
    # Create product map
    product_map = {p.id: p for p in products}
    
    return {
        "favorites": [
            {
                "id": f.id,
                "product_id": f.product_id,
                "created_at": f.created_at,
                "product": {
                    "id": product_map[f.product_id].id,
                    "sku_id": product_map[f.product_id].sku_id,
                    "category_id": product_map[f.product_id].category_id,
                    "price": product_map[f.product_id].price,
                    "manufacturer": product_map[f.product_id].manufacturer,
                    "supplier": product_map[f.product_id].supplier,
                    "image_url": product_map[f.product_id].image_url,
                    "additional_data_count": len(product_map[f.product_id].additional_data)
                } if f.product_id in product_map else None
            }
            for f in favorites if f.product_id in product_map
        ],
        "total_count": len(favorites),
        "skip": skip,
        "limit": limit
    }

@router.post("/{id}/compare")
def compare_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a product to user's compare list.
    """
    # Check if product exists and belongs to tenant
    product = db.query(Product).filter(
        Product.id == id,
        Product.tenant_id == current_user.tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if already in compare list
    existing_compare = db.query(CompareList).filter(
        CompareList.user_id == current_user.id,
        CompareList.product_id == id
    ).first()
    
    if existing_compare:
        raise HTTPException(status_code=400, detail="Product already in compare list")
    
    # Check compare list limit (max 5 products)
    compare_count = db.query(CompareList).filter(
        CompareList.user_id == current_user.id
    ).count()
    
    if compare_count >= 5:
        raise HTTPException(status_code=400, detail="Compare list is full (max 5 products)")
    
    # Add to compare list
    compare_item = CompareList(
        user_id=current_user.id,
        product_id=id
    )
    db.add(compare_item)
    db.commit()
    
    return {"msg": f"Product {id} added to compare list"}

@router.delete("/{id}/compare")
def remove_from_compare(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a product from user's compare list.
    """
    # Check if product exists and belongs to tenant
    product = db.query(Product).filter(
        Product.id == id,
        Product.tenant_id == current_user.tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if in compare list
    existing_compare = db.query(CompareList).filter(
        CompareList.user_id == current_user.id,
        CompareList.product_id == id
    ).first()
    
    if not existing_compare:
        raise HTTPException(status_code=400, detail="Product not in compare list")
    
    # Remove from compare list
    db.delete(existing_compare)
    db.commit()
    
    return {"msg": f"Product {id} removed from compare list"}

@router.get("/compare")
def get_compare_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's compare list with full product details.
    """
    # Get compare list items
    compare_items = db.query(CompareList).filter(
        CompareList.user_id == current_user.id
    ).all()
    
    # Get product details
    product_ids = [c.product_id for c in compare_items]
    products = db.query(Product).filter(
        Product.id.in_(product_ids),
        Product.tenant_id == current_user.tenant_id
    ).all()
    
    # Create product map
    product_map = {p.id: p for p in products}
    
    # Get field configurations for additional data
    field_configs = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id
    ).all()
    field_config_map = {config.field_name: config for config in field_configs}
    
    return {
        "compare_list": [
            {
                "id": c.id,
                "product_id": c.product_id,
                "created_at": c.created_at,
                "product": {
                    "id": product_map[c.product_id].id,
                    "sku_id": product_map[c.product_id].sku_id,
                    "category_id": product_map[c.product_id].category_id,
                    "price": product_map[c.product_id].price,
                    "manufacturer": product_map[c.product_id].manufacturer,
                    "supplier": product_map[c.product_id].supplier,
                    "image_url": product_map[c.product_id].image_url,
                    "additional_data": [
                        {
                            "id": additional.id,
                            "field_name": additional.field_name,
                            "field_label": additional.field_label,
                            "field_value": additional.field_value,
                            "field_type": additional.field_type,
                            "is_searchable": field_config_map.get(additional.field_name).is_searchable if field_config_map.get(additional.field_name) else False,
                            "is_editable": field_config_map.get(additional.field_name).is_editable if field_config_map.get(additional.field_name) else True,
                            "is_primary": field_config_map.get(additional.field_name).is_primary if field_config_map.get(additional.field_name) else False,
                            "is_secondary": field_config_map.get(additional.field_name).is_secondary if field_config_map.get(additional.field_name) else False
                        }
                        for additional in product_map[c.product_id].additional_data
                    ],
                    "additional_data_count": len(product_map[c.product_id].additional_data)
                } if c.product_id in product_map else None
            }
            for c in compare_items if c.product_id in product_map
        ],
        "total_count": len(compare_items)
    }

@router.post("/{id}/report")
def report_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Report a product (tenant-scoped).
    TODO: Implement reporting functionality
    """
    product = db.query(Product).filter(
        Product.id == id,
        Product.tenant_id == current_user.tenant_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # TODO: Implement reporting functionality
    return {"msg": f"Product {id} reported"}

# Field Configuration Endpoints

@router.get("/fields/configuration")
def get_field_configurations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all field configurations for the current tenant.
    Returns only fields that actually exist in the tenant's product data.
    """
    try:
        # Get all actual fields from the tenant's product data
        actual_fields = get_actual_fields_for_tenant(db, current_user.tenant_id)
        
        # Get existing field configurations for actual fields only
        field_configs = db.query(FieldConfiguration).filter(
            FieldConfiguration.tenant_id == current_user.tenant_id,
            FieldConfiguration.field_name.in_(list(actual_fields))
        ).order_by(FieldConfiguration.display_order, FieldConfiguration.field_name).all()
        
        # Create a set of configured field names
        configured_fields = {config.field_name for config in field_configs}
        
        # Add default configurations for actual fields that don't have configs yet
        for field_name in actual_fields:
            if field_name not in configured_fields:
                # Get field mapping for additional context
                field_mapping = db.query(FieldMapping).filter(
                    FieldMapping.tenant_id == current_user.tenant_id,
                    FieldMapping.normalized_field_name == field_name
                ).first()
                
                # Determine field type and label
                if field_mapping:
                    field_type = field_mapping.field_type
                    field_label = field_mapping.field_label
                    is_standard_field = field_mapping.is_standard_field
                else:
                    # Default values for standard fields
                    field_type = "string"
                    field_label = field_name.replace('_', ' ').title()
                    is_standard_field = field_name in ['sku_id', 'price', 'manufacturer', 'supplier', 'image_url', 'category_id']
                
                # Create default configuration
                default_config = FieldConfiguration(
                    tenant_id=current_user.tenant_id,
                    field_name=field_name,
                    field_label=field_label,
                    field_type=field_type,
                    is_searchable=False,
                    is_editable=True,
                    is_primary=is_standard_field and field_name == 'sku_id',
                    is_secondary=is_standard_field and field_name in ['price', 'manufacturer', 'supplier'],
                    display_order=len(field_configs) + len([c for c in field_configs if c.field_name < field_name]),
                    description=f"Field: {field_label}"
                )
                db.add(default_config)
                field_configs.append(default_config)
        
        if actual_fields and not field_configs:
            db.commit()
        
        return {
            "msg": f"Successfully retrieved {len(field_configs)} field configurations (real-time data)",
            "field_configurations": [
                {
                    "id": config.id,
                    "field_name": config.field_name,
                    "field_label": config.field_label,
                    "field_type": config.field_type,
                    "is_searchable": config.is_searchable,
                    "is_editable": config.is_editable,
                    "is_primary": config.is_primary,
                    "is_secondary": config.is_secondary,
                    "display_order": config.display_order,
                    "description": config.description,
                    "created_at": config.created_at,
                    "updated_at": config.updated_at
                }
                for config in field_configs
            ],
            "total_count": len(field_configs),
            "actual_fields_count": len(actual_fields)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving field configurations: {str(e)}")

@router.post("/fields/configuration")
def set_field_configurations(
    configurations: List[Dict[str, Any]] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Set field configurations for the current tenant.
    This endpoint allows setting multiple field configurations at once.
    Only fields that actually exist in the tenant's product data can be configured.
    
    Expected structure:
    [
        {
            "field_name": "brand",
            "field_label": "Brand Name",
            "field_type": "string",
            "is_searchable": true,
            "is_editable": true,
            "is_primary": false,
            "is_secondary": true,
            "display_order": 1,
            "description": "Product brand name"
        }
    ]
    """
    try:
        # Get all actual fields from the tenant's product data
        actual_fields = get_actual_fields_for_tenant(db, current_user.tenant_id)
        
        created_configs = []
        updated_configs = []
        errors = []
        
        for config_data in configurations:
            try:
                # Validate required fields
                if not config_data.get('field_name'):
                    errors.append("Field name is required")
                    continue
                
                if not config_data.get('field_label'):
                    errors.append(f"Field label is required for field: {config_data['field_name']}")
                    continue
                
                # Check if field actually exists in tenant's data
                field_name = config_data['field_name']
                if field_name not in actual_fields:
                    errors.append(f"Field '{field_name}' does not exist in tenant's product data")
                    continue
                
                # Check if configuration already exists
                existing_config = db.query(FieldConfiguration).filter(
                    FieldConfiguration.field_name == field_name,
                    FieldConfiguration.tenant_id == current_user.tenant_id
                ).first()
                
                if existing_config:
                    # Update existing configuration
                    existing_config.field_label = config_data.get('field_label', existing_config.field_label)
                    existing_config.field_type = config_data.get('field_type', existing_config.field_type)
                    existing_config.is_searchable = config_data.get('is_searchable', existing_config.is_searchable)
                    existing_config.is_editable = config_data.get('is_editable', existing_config.is_editable)
                    existing_config.is_primary = config_data.get('is_primary', existing_config.is_primary)
                    existing_config.is_secondary = config_data.get('is_secondary', existing_config.is_secondary)
                    existing_config.display_order = config_data.get('display_order', existing_config.display_order)
                    existing_config.description = config_data.get('description', existing_config.description)
                    updated_configs.append(existing_config)
                else:
                    # Create new configuration
                    new_config = FieldConfiguration(
                        tenant_id=current_user.tenant_id,
                        field_name=field_name,
                        field_label=config_data['field_label'],
                        field_type=config_data.get('field_type', 'string'),
                        is_searchable=config_data.get('is_searchable', False),
                        is_editable=config_data.get('is_editable', True),
                        is_primary=config_data.get('is_primary', False),
                        is_secondary=config_data.get('is_secondary', False),
                        display_order=config_data.get('display_order', 0),
                        description=config_data.get('description', '')
                    )
                    db.add(new_config)
                    created_configs.append(new_config)
                
            except Exception as e:
                errors.append(f"Error processing configuration for field {config_data.get('field_name', 'unknown')}: {str(e)}")
        
        if errors:
            db.rollback()
            return {
                "msg": f"Failed to set {len(errors)} field configurations",
                "errors": errors,
                "created_count": 0,
                "updated_count": 0,
                "total_count": len(configurations),
                "actual_fields_count": len(actual_fields)
            }
        
        db.commit()
        
        return {
            "msg": f"Successfully set {len(created_configs) + len(updated_configs)} field configurations (real-time data)",
            "created_count": len(created_configs),
            "updated_count": len(updated_configs),
            "total_count": len(configurations),
            "actual_fields_count": len(actual_fields),
            "field_configurations": [
                {
                    "id": config.id,
                    "field_name": config.field_name,
                    "field_label": config.field_label,
                    "field_type": config.field_type,
                    "is_searchable": config.is_searchable,
                    "is_editable": config.is_editable,
                    "is_primary": config.is_primary,
                    "is_secondary": config.is_secondary,
                    "display_order": config.display_order,
                    "description": config.description
                }
                for config in created_configs + updated_configs
            ]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error setting field configurations: {str(e)}")

@router.put("/fields/configuration/{field_name}")
def update_field_configuration(
    field_name: str,
    configuration: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific field configuration for the current tenant.
    Only fields that actually exist in the tenant's product data can be updated.
    
    Expected structure:
    {
        "field_label": "Brand Name",
        "field_type": "string",
        "is_searchable": true,
        "is_editable": true,
        "is_primary": false,
        "is_secondary": true,
        "display_order": 1,
        "description": "Product brand name"
    }
    """
    try:
        # Get all actual fields from the tenant's product data
        actual_fields = get_actual_fields_for_tenant(db, current_user.tenant_id)
        
        # Check if field actually exists in tenant's data
        if field_name not in actual_fields:
            raise HTTPException(
                status_code=404, 
                detail=f"Field '{field_name}' does not exist in tenant's product data"
            )
        
        # Find the field configuration
        field_config = db.query(FieldConfiguration).filter(
            FieldConfiguration.field_name == field_name,
            FieldConfiguration.tenant_id == current_user.tenant_id
        ).first()
        
        if not field_config:
            raise HTTPException(status_code=404, detail=f"Field configuration not found for field: {field_name}")
        
        # Update the configuration
        if 'field_label' in configuration:
            field_config.field_label = configuration['field_label']
        if 'field_type' in configuration:
            field_config.field_type = configuration['field_type']
        if 'is_searchable' in configuration:
            field_config.is_searchable = configuration['is_searchable']
        if 'is_editable' in configuration:
            field_config.is_editable = configuration['is_editable']
        if 'is_primary' in configuration:
            field_config.is_primary = configuration['is_primary']
        if 'is_secondary' in configuration:
            field_config.is_secondary = configuration['is_secondary']
        if 'display_order' in configuration:
            field_config.display_order = configuration['display_order']
        if 'description' in configuration:
            field_config.description = configuration['description']
        
        db.commit()
        db.refresh(field_config)
        
        return {
            "msg": f"Successfully updated field configuration for {field_name} (real-time data)",
            "field_configuration": {
                "id": field_config.id,
                "field_name": field_config.field_name,
                "field_label": field_config.field_label,
                "field_type": field_config.field_type,
                "is_searchable": field_config.is_searchable,
                "is_editable": field_config.is_editable,
                "is_primary": field_config.is_primary,
                "is_secondary": field_config.is_secondary,
                "display_order": field_config.display_order,
                "description": field_config.description,
                "updated_at": field_config.updated_at
            },
            "actual_fields_count": len(actual_fields)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating field configuration: {str(e)}") 

@router.get("/filters/unique-data")
def get_unique_filter_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    field_name: str = None  # Optional: get data for specific field only
):
    """
    Get unique filter data for search functionality.
    Returns unique values for all searchable fields or a specific field.
    
    Args:
        field_name: Optional field name to get unique data for (e.g., 'brand', 'manufacturer', 'supplier')
    
    Returns:
        Dictionary with unique values for each searchable field
    """
    # Get searchable field configurations
    searchable_configs = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id,
        FieldConfiguration.is_searchable == True
    ).all()
    
    searchable_fields = [config.field_name for config in searchable_configs]
    
    if not searchable_fields:
        return {
            "filters": {},
            "searchable_fields": []
        }
    
    filters = {}
    
    # If specific field requested, only get data for that field
    if field_name:
        if field_name not in searchable_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Field '{field_name}' is not searchable or does not exist"
            )
        searchable_fields = [field_name]
    
    # Get unique values for standard fields
    if 'sku_id' in searchable_fields:
        sku_ids = db.query(Product.sku_id).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.sku_id.isnot(None),
            Product.sku_id != ""
        ).distinct().all()
        filters['sku_id'] = [item[0] for item in sku_ids if item[0]]
    
    if 'manufacturer' in searchable_fields:
        manufacturers = db.query(Product.manufacturer).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.manufacturer.isnot(None),
            Product.manufacturer != ""
        ).distinct().all()
        filters['manufacturer'] = [item[0] for item in manufacturers if item[0]]
    
    if 'supplier' in searchable_fields:
        suppliers = db.query(Product.supplier).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.supplier.isnot(None),
            Product.supplier != ""
        ).distinct().all()
        filters['supplier'] = [item[0] for item in suppliers if item[0]]
    
    if 'price' in searchable_fields:
        prices = db.query(Product.price).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.price.isnot(None)
        ).distinct().all()
        filters['price'] = sorted([float(item[0]) for item in prices if item[0] is not None])
    
    if 'category_id' in searchable_fields:
        category_ids = db.query(Product.category_id).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.category_id.isnot(None)
        ).distinct().all()
        filters['category_id'] = [item[0] for item in category_ids if item[0]]
        
        # Also get category names
        if category_ids:
            category_names = db.query(Category.id, Category.name).filter(
                Category.id.in_([item[0] for item in category_ids if item[0]])
            ).all()
            filters['categories'] = [{"id": cat[0], "name": cat[1]} for cat in category_names]
    
    # Get unique values for additional data fields
    additional_fields = [field for field in searchable_fields if field not in ['sku_id', 'manufacturer', 'supplier', 'price', 'category_id', 'image_url']]
    
    for field_name in additional_fields:
        field_values = db.query(ProductAdditionalData.field_value).filter(
            ProductAdditionalData.field_name == field_name,
            ProductAdditionalData.product_id.in_(
                db.query(Product.id).filter(Product.tenant_id == current_user.tenant_id)
            ),
            ProductAdditionalData.field_value.isnot(None),
            ProductAdditionalData.field_value != ""
        ).distinct().all()
        
        filters[field_name] = [item[0] for item in field_values if item[0]]
    
    return {
        "filters": filters,
        "searchable_fields": searchable_fields,
        "field_name": field_name if field_name else None
    }

@router.get("/filters/brands")
def get_unique_brands(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get unique brand names for filtering.
    This is a convenience endpoint specifically for brand filtering.
    """
    # Check if brand is searchable
    brand_config = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id,
        FieldConfiguration.field_name == 'brand',
        FieldConfiguration.is_searchable == True
    ).first()
    
    if not brand_config:
        return {
            "brands": [],
            "message": "Brand field is not searchable or not configured"
        }
    
    # Get unique brand values
    brand_values = db.query(ProductAdditionalData.field_value).filter(
        ProductAdditionalData.field_name == 'brand',
        ProductAdditionalData.product_id.in_(
            db.query(Product.id).filter(Product.tenant_id == current_user.tenant_id)
        ),
        ProductAdditionalData.field_value.isnot(None),
        ProductAdditionalData.field_value != ""
    ).distinct().all()
    
    brands = [item[0] for item in brand_values if item[0]]
    
    return {
        "brands": sorted(brands),
        "total_count": len(brands)
    }

@router.get("/filters/manufacturers")
def get_unique_manufacturers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get unique manufacturer names for filtering.
    This is a convenience endpoint specifically for manufacturer filtering.
    """
    # Check if manufacturer is searchable
    manufacturer_config = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id,
        FieldConfiguration.field_name == 'manufacturer',
        FieldConfiguration.is_searchable == True
    ).first()
    
    if not manufacturer_config:
        return {
            "manufacturers": [],
            "message": "Manufacturer field is not searchable or not configured"
        }
    
    # Get unique manufacturer values
    manufacturers = db.query(Product.manufacturer).filter(
        Product.tenant_id == current_user.tenant_id,
        Product.manufacturer.isnot(None),
        Product.manufacturer != ""
    ).distinct().all()
    
    manufacturer_list = [item[0] for item in manufacturers if item[0]]
    
    return {
        "manufacturers": sorted(manufacturer_list),
        "total_count": len(manufacturer_list)
    }

@router.get("/filters/suppliers")
def get_unique_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get unique supplier names for filtering.
    This is a convenience endpoint specifically for supplier filtering.
    """
    # Check if supplier is searchable
    supplier_config = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id,
        FieldConfiguration.field_name == 'supplier',
        FieldConfiguration.is_searchable == True
    ).first()
    
    if not supplier_config:
        return {
            "suppliers": [],
            "message": "Supplier field is not searchable or not configured"
        }
    
    # Get unique supplier values
    suppliers = db.query(Product.supplier).filter(
        Product.tenant_id == current_user.tenant_id,
        Product.supplier.isnot(None),
        Product.supplier != ""
    ).distinct().all()
    
    supplier_list = [item[0] for item in suppliers if item[0]]
    
    return {
        "suppliers": sorted(supplier_list),
        "total_count": len(supplier_list)
    }

@router.get("/filters/categories")
def get_unique_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get unique categories for filtering.
    This is a convenience endpoint specifically for category filtering.
    """
    # Check if category_id is searchable
    category_config = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id,
        FieldConfiguration.field_name == 'category_id',
        FieldConfiguration.is_searchable == True
    ).first()
    
    if not category_config:
        return {
            "categories": [],
            "message": "Category field is not searchable or not configured"
        }
    
    # Get unique categories
    categories = db.query(Category.id, Category.name, Category.description).filter(
        Category.id.in_(
            db.query(Product.category_id).filter(
                Product.tenant_id == current_user.tenant_id,
                Product.category_id.isnot(None)
            ).distinct()
        )
    ).all()
    
    category_list = [
        {
            "id": cat[0],
            "name": cat[1],
            "description": cat[2]
        }
        for cat in categories
    ]
    
    return {
        "categories": sorted(category_list, key=lambda x: x['name']),
        "total_count": len(category_list)
    }

@router.get("/filters/price-range")
def get_price_range(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get price range (min, max) for filtering.
    This is a convenience endpoint specifically for price range filtering.
    """
    # Check if price is searchable
    price_config = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id,
        FieldConfiguration.field_name == 'price',
        FieldConfiguration.is_searchable == True
    ).first()
    
    if not price_config:
        return {
            "price_range": {"min": 0, "max": 0},
            "message": "Price field is not searchable or not configured"
        }
    
    # Get price range
    price_stats = db.query(
        func.min(Product.price),
        func.max(Product.price)
    ).filter(
        Product.tenant_id == current_user.tenant_id,
        Product.price.isnot(None)
    ).first()
    
    min_price = float(price_stats[0]) if price_stats[0] is not None else 0
    max_price = float(price_stats[1]) if price_stats[1] is not None else 0
    
    return {
        "price_range": {
            "min": min_price,
            "max": max_price
        },
        "currency": "USD"  # Default currency
    } 

@router.get("/filters/all")
def get_all_filters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all available filters for search functionality.
    This endpoint returns all unique filter data in a single request.
    """
    # Get searchable field configurations
    searchable_configs = db.query(FieldConfiguration).filter(
        FieldConfiguration.tenant_id == current_user.tenant_id,
        FieldConfiguration.is_searchable == True
    ).all()
    
    searchable_fields = [config.field_name for config in searchable_configs]
    
    if not searchable_fields:
        return {
            "filters": {},
            "searchable_fields": [],
            "total_filters": 0
        }
    
    filters = {}
    
    # Get unique values for standard fields
    if 'sku_id' in searchable_fields:
        sku_ids = db.query(Product.sku_id).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.sku_id.isnot(None),
            Product.sku_id != ""
        ).distinct().all()
        filters['sku_id'] = sorted([item[0] for item in sku_ids if item[0]])
    
    if 'manufacturer' in searchable_fields:
        manufacturers = db.query(Product.manufacturer).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.manufacturer.isnot(None),
            Product.manufacturer != ""
        ).distinct().all()
        filters['manufacturer'] = sorted([item[0] for item in manufacturers if item[0]])
    
    if 'supplier' in searchable_fields:
        suppliers = db.query(Product.supplier).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.supplier.isnot(None),
            Product.supplier != ""
        ).distinct().all()
        filters['supplier'] = sorted([item[0] for item in suppliers if item[0]])
    
    if 'price' in searchable_fields:
        prices = db.query(Product.price).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.price.isnot(None)
        ).distinct().all()
        filters['price'] = sorted([float(item[0]) for item in prices if item[0] is not None])
        
        # Also get price range
        price_stats = db.query(
            func.min(Product.price),
            func.max(Product.price)
        ).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.price.isnot(None)
        ).first()
        
        min_price = float(price_stats[0]) if price_stats[0] is not None else 0
        max_price = float(price_stats[1]) if price_stats[1] is not None else 0
        
        filters['price_range'] = {
            "min": min_price,
            "max": max_price,
            "currency": "USD"
        }
    
    if 'category_id' in searchable_fields:
        category_ids = db.query(Product.category_id).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.category_id.isnot(None)
        ).distinct().all()
        filters['category_id'] = [item[0] for item in category_ids if item[0]]
        
        # Also get category names
        if category_ids:
            category_names = db.query(Category.id, Category.name, Category.description).filter(
                Category.id.in_([item[0] for item in category_ids if item[0]])
            ).all()
            filters['categories'] = sorted(
                [{"id": cat[0], "name": cat[1], "description": cat[2]} for cat in category_names],
                key=lambda x: x['name']
            )
    
    # Get unique values for additional data fields
    additional_fields = [field for field in searchable_fields if field not in ['sku_id', 'manufacturer', 'supplier', 'price', 'category_id', 'image_url']]
    
    for field_name in additional_fields:
        field_values = db.query(ProductAdditionalData.field_value).filter(
            ProductAdditionalData.field_name == field_name,
            ProductAdditionalData.product_id.in_(
                db.query(Product.id).filter(Product.tenant_id == current_user.tenant_id)
            ),
            ProductAdditionalData.field_value.isnot(None),
            ProductAdditionalData.field_value != ""
        ).distinct().all()
        
        filters[field_name] = sorted([item[0] for item in field_values if item[0]])
    
    return {
        "filters": filters,
        "searchable_fields": searchable_fields,
        "total_filters": len(filters),
        "field_counts": {
            field: len(values) if isinstance(values, list) else 1
            for field, values in filters.items()
        }
    } 

@router.delete("/admin/{id}")
def delete_product_admin(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete any product by ID (superadmin only).
    This endpoint allows superadmin users to delete products from any tenant.
    
    ⚠️  WARNING: This will permanently delete:
    - Product and all its data
    - All additional data fields
    - All favorites and compare list entries
    """
    # Only superadmin can delete any product
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Only superadmin users can delete any product")
    
    # Find the product to delete
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get product info for response
    product_info = {
        "id": product.id,
        "sku_id": product.sku_id,
        "manufacturer": product.manufacturer,
        "supplier": product.supplier,
        "tenant_id": product.tenant_id
    }
    
    # Get tenant info if available
    tenant = None
    if product.tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == product.tenant_id).first()
        if tenant:
            product_info["tenant_name"] = tenant.company_name
    
    # Delete the product (cascade will handle related data)
    db.delete(product)
    db.commit()
    
    return {
        "message": f"Product '{product_info['sku_id']}' deleted successfully",
        "deleted_product": product_info,
        "deleted_by": current_user.email
    }