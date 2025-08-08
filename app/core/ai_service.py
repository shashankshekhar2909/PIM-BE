import requests
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

class GeminiAIService:
    """AI service for file analysis and field normalization using Google Gemini."""
    
    def __init__(self, api_key: str = "AIzaSyCezud7CjyXwl8LVnbWwrHkNuJ95fQWe6U"):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    def _make_request(self, prompt: str) -> str:
        """Make a request to Gemini API."""
        try:
            headers = {
                "Content-Type": "application/json",
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 1,
                    "topP": 1,
                    "maxOutputTokens": 2048,
                }
            }
            
            url = f"{self.base_url}?key={self.api_key}"
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "candidates" in result and result["candidates"]:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise Exception("No response from Gemini API")
                
        except Exception as e:
            logging.error(f"Gemini API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
    
    def analyze_file_content(self, headers: List[str], sample_data: List[List[str]]) -> Dict[str, Any]:
        """
        Analyze file content to determine if it's product data and normalize field names.
        
        Args:
            headers: List of column headers from the file
            sample_data: Sample rows from the file (first 5 rows)
        
        Returns:
            Dict containing analysis results
        """
        prompt = f"""
        Analyze this CSV file to determine if it contains product data and normalize the field names.

        Headers: {headers}
        Sample Data (first 5 rows):
        {sample_data}

        Please provide a JSON response with the following structure:
        {{
            "is_product_data": true/false,
            "confidence": 0.0-1.0,
            "field_mappings": [
                {{
                    "original_field_name": "original column name",
                    "normalized_field_name": "normalized field name (snake_case)",
                    "field_label": "Human readable label",
                    "field_type": "string|number|boolean|date",
                    "is_standard_field": true/false,
                    "description": "Brief description of what this field represents"
                }}
            ],
            "standard_fields_found": ["sku_id", "price", "manufacturer", etc.],
            "additional_fields_found": ["brand", "warranty", etc.],
            "recommendations": [
                "Any recommendations for data processing"
            ]
        }}

        Guidelines:
        1. Standard product fields: sku_id, price, manufacturer, supplier, image_url, category_id
        2. Normalize field names to snake_case
        3. Create human-readable labels
        4. Determine appropriate field types
        5. Identify if it's product data based on presence of SKU, product identifiers, or product-related fields
        6. Confidence should be high if SKU/product identifiers are present, lower if ambiguous

        Return only the JSON response, no additional text.
        """
        
        try:
            response_text = self._make_request(prompt)
            
            # Try to extract JSON from the response
            json_str = self._extract_json_from_response(response_text)
            
            if json_str:
                result = json.loads(json_str)
                return result
            else:
                raise Exception("Could not extract JSON from AI response")
            
        except json.JSONDecodeError as e:
            logging.warning(f"Failed to parse Gemini response as JSON: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to parse AI response")
        except Exception as e:
            logging.warning(f"AI analysis failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """
        Extract JSON from AI response, handling various formats.
        
        Args:
            response_text: Raw response from AI service
            
        Returns:
            Extracted JSON string or None if extraction fails
        """
        try:
            # Try to find JSON in code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                if json_end > json_start:
                    return response_text[json_start:json_end].strip()
            
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                if json_end > json_start:
                    return response_text[json_start:json_end].strip()
            
            # Try to find JSON object directly
            start_brace = response_text.find("{")
            end_brace = response_text.rfind("}")
            
            if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
                json_str = response_text[start_brace:end_brace + 1]
                # Validate it's actually JSON
                json.loads(json_str)  # This will raise JSONDecodeError if invalid
                return json_str
            
            # If no JSON found, return None
            return None
            
        except Exception:
            return None
    
    def normalize_field_names(self, headers: List[str]) -> List[Dict[str, Any]]:
        """
        Normalize field names using AI.
        
        Args:
            headers: List of original field names
        
        Returns:
            List of field mappings
        """
        prompt = f"""
        Normalize these field names for a product database.

        Original field names: {headers}

        Please provide a JSON response with the following structure:
        {{
            "field_mappings": [
                {{
                    "original_field_name": "original name",
                    "normalized_field_name": "normalized name (snake_case)",
                    "field_label": "Human readable label",
                    "field_type": "string|number|boolean|date",
                    "is_standard_field": true/false,
                    "description": "Brief description"
                }}
            ]
        }}

        Guidelines:
        1. Standard product fields: sku_id, price, manufacturer, supplier, image_url, category_id
        2. Normalize to snake_case (e.g., "Product Name" -> "product_name")
        3. Create clear, human-readable labels
        4. Determine appropriate data types
        5. Mark standard fields appropriately

        Return only the JSON response.
        """
        
        try:
            response_text = self._make_request(prompt)
            
            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()
            
            result = json.loads(json_str)
            return result.get("field_mappings", [])
            
        except Exception as e:
            logging.error(f"Field normalization error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Field normalization failed: {str(e)}")
    
    def validate_product_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate product data using AI.
        
        Args:
            data: List of product data dictionaries
        
        Returns:
            Validation results
        """
        sample_data = data[:3] if len(data) > 3 else data
        
        prompt = f"""
        Validate this product data for consistency and quality.

        Sample data: {json.dumps(sample_data, indent=2)}

        Please provide a JSON response with the following structure:
        {{
            "validation_results": [
                {{
                    "row_index": 0,
                    "sku_id": "SKU001",
                    "issues": ["Issue description"],
                    "warnings": ["Warning description"],
                    "is_valid": true/false
                }}
            ],
            "overall_quality": "good|fair|poor",
            "recommendations": [
                "Recommendations for data quality improvement"
            ]
        }}

        Check for:
        1. Missing required fields (SKU ID)
        2. Invalid data types (price should be numeric)
        3. Inconsistent formatting
        4. Duplicate SKUs
        5. Data quality issues

        Return only the JSON response.
        """
        
        try:
            response_text = self._make_request(prompt)
            
            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()
            
            result = json.loads(json_str)
            return result
            
        except Exception as e:
            logging.error(f"Data validation error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Data validation failed: {str(e)}") 