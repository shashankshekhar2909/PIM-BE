import csv
import io
import pandas as pd
from typing import List, Dict, Any, Tuple
from fastapi import UploadFile, HTTPException
from app.core.ai_service import GeminiAIService
import logging

class AICSVProcessor:
    """AI-enhanced CSV processor for product data."""
    
    def __init__(self):
        try:
            self.ai_service = GeminiAIService()
            self.ai_available = True
        except Exception as e:
            logging.warning(f"AI service not available: {str(e)}")
            self.ai_available = False
    
    def analyze_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Analyze file content using AI to determine if it's product data and normalize fields.
        
        Args:
            file: Uploaded file (CSV or Excel)
        
        Returns:
            Analysis results with field mappings
        """
        try:
            # Reset file pointer to beginning
            file.file.seek(0)
            
            # Read file content
            if file.filename.endswith('.csv'):
                content = file.file.read().decode('utf-8')
                df = pd.read_csv(io.StringIO(content))
            elif file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file.file)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or Excel file.")
            
            # Get headers and sample data
            headers = df.columns.tolist()
            sample_data = df.head(5).values.tolist()
            
            # Try AI analysis first, fallback to basic analysis if it fails
            analysis = None
            if self.ai_available:
                try:
                    analysis = self.ai_service.analyze_file_content(headers, sample_data)
                    logging.info("AI analysis completed successfully")
                except Exception as e:
                    logging.info(f"AI analysis not available, using fallback: {str(e)}")
                    analysis = self._fallback_analysis(headers, sample_data)
            else:
                logging.info("AI service not available, using fallback analysis")
                analysis = self._fallback_analysis(headers, sample_data)
            
            return {
                "file_name": file.filename,
                "total_rows": len(df),
                "headers": headers,
                "analysis": analysis,
                "sample_data": sample_data
            }
            
        except Exception as e:
            logging.error(f"File analysis error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")
    
    def _fallback_analysis(self, headers: List[str], sample_data: List[List[str]]) -> Dict[str, Any]:
        """Fallback analysis when AI is not available."""
        # Standard product fields
        standard_fields = {
            'sku_id', 'sku', 'product_id', 'product_id', 'id',
            'price', 'cost', 'amount', 'value',
            'manufacturer', 'brand', 'maker', 'company',
            'supplier', 'vendor', 'distributor',
            'image_url', 'image', 'photo', 'picture',
            'category_id', 'category', 'cat_id'
        }
        
        # Analyze headers
        field_mappings = []
        standard_fields_found = []
        additional_fields_found = []
        
        for header in headers:
            header_lower = header.lower().strip()
            normalized_name = header_lower.replace(' ', '_').replace('-', '_').replace('.', '_')
            
            # Check if it's a standard field
            is_standard = any(field in header_lower for field in standard_fields)
            
            # Determine field type based on header name
            field_type = self._detect_field_type(header_lower)
            
            if is_standard:
                standard_fields_found.append(normalized_name)
            else:
                additional_fields_found.append(normalized_name)
            
            field_mappings.append({
                "original_field_name": header,
                "normalized_field_name": normalized_name,
                "field_label": header.replace('_', ' ').title(),
                "field_type": field_type,
                "is_standard_field": is_standard,
                "description": f"Field: {header}"
            })
        
        # Determine if it's product data
        is_product_data = len(standard_fields_found) > 0
        confidence = min(0.8, len(standard_fields_found) / len(headers)) if headers else 0.0
        
        return {
            "is_product_data": is_product_data,
            "confidence": confidence,
            "field_mappings": field_mappings,
            "standard_fields_found": standard_fields_found,
            "additional_fields_found": additional_fields_found,
            "recommendations": [
                "Using fallback analysis - AI service not available",
                "Review field mappings manually for accuracy",
                "Consider updating field types based on actual data"
            ]
        }
    
    def _detect_field_type(self, header_lower: str) -> str:
        """
        Detect field type based on header name.
        
        Args:
            header_lower: Lowercase header name
            
        Returns:
            Detected field type (string, number, boolean, date)
        """
        # Price-related fields
        if any(word in header_lower for word in ['price', 'cost', 'amount', 'value', 'rate']):
            return "number"
        
        # Date-related fields
        if any(word in header_lower for word in ['date', 'created', 'updated', 'expiry', 'expiration']):
            return "date"
        
        # Boolean fields
        if any(word in header_lower for word in ['is_', 'has_', 'active', 'enabled', 'available']):
            return "boolean"
        
        # ID fields
        if any(word in header_lower for word in ['id', 'sku', 'code']):
            return "string"
        
        # Default to string
        return "string"
    
    def process_file_with_mappings(self, file: UploadFile, field_mappings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process file using provided field mappings.
        
        Args:
            file: Uploaded file
            field_mappings: List of field mappings from AI analysis
        
        Returns:
            Processed product data
        """
        try:
            # Reset file pointer to beginning
            file.file.seek(0)
            
            # Read file content
            if file.filename.endswith('.csv'):
                content = file.file.read().decode('utf-8')
                df = pd.read_csv(io.StringIO(content))
            elif file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file.file)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format")
            
            # Create mapping dictionary
            field_map = {mapping['original_field_name']: mapping for mapping in field_mappings}
            
            # Process each row
            products = []
            for index, row in df.iterrows():
                product_data = {
                    "index": index,
                    "sku_id": None,
                    "category_id": None,
                    "price": None,
                    "manufacturer": None,
                    "supplier": None,
                    "image_url": None,
                    "additional_data": [],
                    "validation_status": "valid",
                    "validation_errors": [],
                    "is_edited": False
                }
                
                # Process each column
                for col_name, value in row.items():
                    if pd.isna(value):
                        continue
                    
                    # Get field mapping
                    mapping = field_map.get(col_name)
                    if not mapping:
                        continue
                    
                    normalized_name = mapping['normalized_field_name']
                    field_type = mapping['field_type']
                    is_standard = mapping.get('is_standard_field', False)
                    
                    # Convert value based on field type
                    processed_value = self._convert_value(value, field_type)
                    
                    # Handle standard fields
                    if is_standard and normalized_name in product_data:
                        product_data[normalized_name] = processed_value
                    else:
                        # Handle additional data
                        product_data['additional_data'].append({
                            "field_name": normalized_name,
                            "field_label": mapping['field_label'],
                            "field_value": str(processed_value),
                            "field_type": field_type
                        })
                
                # Validate required fields
                if not product_data['sku_id']:
                    product_data['validation_status'] = 'error'
                    product_data['validation_errors'].append("SKU ID is required")
                
                products.append(product_data)
            
            return products
            
        except Exception as e:
            logging.error(f"File processing error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")
    
    def _convert_value(self, value: Any, field_type: str) -> Any:
        """Convert value to appropriate type."""
        if pd.isna(value):
            return None
        
        try:
            if field_type == 'number':
                return float(value) if value else None
            elif field_type == 'boolean':
                if isinstance(value, str):
                    return value.lower() in ['true', '1', 'yes', 'y']
                return bool(value)
            elif field_type == 'date':
                # Handle date conversion if needed
                return str(value)
            else:
                return str(value).strip() if value else None
        except (ValueError, TypeError):
            return str(value).strip() if value else None
    
    def validate_processed_data(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate processed product data using AI.
        
        Args:
            products: List of processed product data
        
        Returns:
            Validation results
        """
        try:
            if self.ai_available:
                validation_results = self.ai_service.validate_product_data(products)
            else:
                validation_results = self._fallback_validation(products)
            return validation_results
        except Exception as e:
            logging.error(f"Data validation error: {str(e)}")
            return {
                "validation_results": [],
                "overall_quality": "unknown",
                "recommendations": ["AI validation failed, please review data manually"]
            }
    
    def _fallback_validation(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback validation when AI is not available."""
        validation_results = []
        
        for product in products:
            issues = []
            warnings = []
            
            # Check for required fields
            if not product.get('sku_id'):
                issues.append("Missing SKU ID")
            
            # Check for data quality issues
            if product.get('price') is not None and product['price'] < 0:
                issues.append("Negative price")
            
            validation_results.append({
                "row_index": product.get('index', 0),
                "sku_id": product.get('sku_id', 'Unknown'),
                "issues": issues,
                "warnings": warnings,
                "is_valid": len(issues) == 0
            })
        
        return {
            "validation_results": validation_results,
            "overall_quality": "fair",
            "recommendations": [
                "AI validation not available, using basic validation",
                "Review data manually for quality issues"
            ]
        } 