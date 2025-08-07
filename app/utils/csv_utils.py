import csv
import io
from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException

def parse_product_csv(file: UploadFile) -> List[Dict[str, Any]]:
    """
    Parse product CSV file and return list of product dictionaries.
    
    Expected columns:
    - sku_id (required)
    - category_id (optional)
    - price (optional)
    - manufacturer (optional)
    - supplier (optional)
    - image_url (optional)
    - Any dynamic fields (optional)
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read file content
        content = file.file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        products = []
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is headers
            try:
                # Validate required field
                if not row.get('sku_id'):
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Row {row_num}: sku_id is required"
                    )
                
                # Parse product data
                product_data = {
                    'sku_id': row['sku_id'].strip() if row['sku_id'] else '',
                    'additional_data': []
                }
                
                # Parse optional fields
                if row.get('category_id') and row['category_id'].strip():
                    try:
                        product_data['category_id'] = int(row['category_id'])
                    except ValueError:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Row {row_num}: category_id must be an integer"
                        )
                
                if row.get('price') and row['price'].strip():
                    try:
                        product_data['price'] = float(row['price'])
                    except ValueError:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Row {row_num}: price must be a number"
                        )
                
                if row.get('manufacturer') and row['manufacturer'].strip():
                    product_data['manufacturer'] = row['manufacturer'].strip()
                
                if row.get('supplier') and row['supplier'].strip():
                    product_data['supplier'] = row['supplier'].strip()
                
                if row.get('image_url') and row['image_url'].strip():
                    product_data['image_url'] = row['image_url'].strip()
                
                # Parse additional fields (any column not in standard fields)
                standard_fields = {'sku_id', 'category_id', 'price', 'manufacturer', 'supplier', 'image_url'}
                for field, value in row.items():
                    if field not in standard_fields and value and value.strip():
                        product_data['additional_data'].append({
                            'field_name': field,
                            'field_label': field.replace('_', ' ').title(),
                            'field_value': value.strip(),
                            'field_type': 'string'
                        })
                
                products.append(product_data)
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Row {row_num}: Error parsing data - {str(e)}"
                )
        
        return products
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}")

def parse_category_csv(file: UploadFile) -> List[Dict[str, Any]]:
    """
    Parse category CSV file and return list of category dictionaries.
    
    Expected columns:
    - name (required)
    - description (optional)
    - schema_json (optional, JSON string)
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read file content
        content = file.file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        categories = []
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Validate required field
                if not row.get('name'):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Row {row_num}: name is required"
                    )
                
                category_data = {
                    'name': row['name'].strip(),
                    'description': row.get('description', '').strip(),
                    'schema_json': {}
                }
                
                # Parse schema_json if provided
                if row.get('schema_json'):
                    try:
                        import json
                        category_data['schema_json'] = json.loads(row['schema_json'])
                    except json.JSONDecodeError:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Row {row_num}: schema_json must be valid JSON"
                        )
                
                categories.append(category_data)
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Row {row_num}: Error parsing data - {str(e)}"
                )
        
        return categories
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}") 