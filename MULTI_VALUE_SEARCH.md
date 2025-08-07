# Multi-Value Search and Filtering

This document describes the enhanced search and filtering capabilities that support multiple values for fields.

## 🎯 **New Features**

### **1. Comma-Separated Values Support**
All search and filter endpoints now support **comma-separated values** for multiple fields:

- ✅ **Manufacturer**: `manufacturer=Adidas,Apple,Bosch,Hasbro,Home Depot`
- ✅ **Supplier**: `supplier=Supplier1,Supplier2,Supplier3`
- ✅ **Brand**: `brand=Brand1,Brand2,Brand3`
- ✅ **SKU ID**: `sku_id=SKU1,SKU2,SKU3`
- ✅ **Dynamic Fields**: `field_name=color&field_value=Red,Blue,Green`

### **2. Enhanced Search Logic**
- **OR logic within fields**: Multiple values for the same field use OR logic
- **AND logic across fields**: Different fields use AND logic
- **Case-insensitive matching**: All searches are case-insensitive
- **Partial matching**: Uses `LIKE` queries for flexible matching

## 🚀 **Usage Examples**

### **1. Multiple Manufacturers**
```bash
# Get products from Adidas, Apple, Bosch, Hasbro, or Home Depot
GET /api/v1/products?manufacturer=Adidas,Apple,Bosch,Hasbro,Home Depot

# Expected: Returns products from ANY of these manufacturers
```

### **2. Multiple Suppliers**
```bash
# Get products from multiple suppliers
GET /api/v1/products?supplier=Supplier1,Supplier2,Supplier3

# Expected: Returns products from ANY of these suppliers
```

### **3. Multiple Brands**
```bash
# Get products with multiple brands
GET /api/v1/products?brand=Nike,Adidas,Puma

# Expected: Returns products with ANY of these brands
```

### **4. Combined Filters**
```bash
# Get Adidas/Apple products with price ≤ 1000
GET /api/v1/products?manufacturer=Adidas,Apple&price_max=1000

# Expected: Returns products that are (Adidas OR Apple) AND price ≤ 1000
```

### **5. Multiple SKU IDs**
```bash
# Get products with specific SKU IDs
GET /api/v1/products?sku_id=SKU001,SKU002,SKU003

# Expected: Returns products with ANY of these SKU IDs
```

### **6. Dynamic Field Search**
```bash
# Get products with multiple colors
GET /api/v1/products?field_name=color&field_value=Red,Blue,Green

# Expected: Returns products with ANY of these colors
```

## 🔍 **Search Endpoint Examples**

### **1. Search with Multiple Manufacturers**
```bash
GET /api/v1/search?manufacturer=Adidas,Apple,Bosch,Hasbro,Home Depot
```

**Response:**
```json
{
  "products": [
    {
      "id": 1,
      "sku_id": "ADIDAS-001",
      "manufacturer": "Adidas",
      "price": 99.99,
      "supplier": "Sports Supplier",
      "additional_data_count": 3
    },
    {
      "id": 2,
      "sku_id": "APPLE-001",
      "manufacturer": "Apple",
      "price": 999.99,
      "supplier": "Tech Supplier",
      "additional_data_count": 2
    }
  ],
  "total_count": 2,
  "skip": 0,
  "limit": 100,
  "query": null,
  "searchable_fields": ["sku_id", "manufacturer", "supplier", "price"],
  "field_filters": {
    "manufacturer": ["Adidas", "Apple", "Bosch", "Hasbro", "Home Depot"]
  }
}
```

### **2. Combined Search with Multiple Values**
```bash
GET /api/v1/search?manufacturer=Adidas,Apple&price_max=1000&supplier=Supplier1,Supplier2
```

**Response:**
```json
{
  "products": [
    {
      "id": 1,
      "sku_id": "ADIDAS-001",
      "manufacturer": "Adidas",
      "price": 99.99,
      "supplier": "Supplier1",
      "additional_data_count": 3
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 100,
  "query": null,
  "searchable_fields": ["sku_id", "manufacturer", "supplier", "price"],
  "field_filters": {
    "manufacturer": ["Adidas", "Apple"],
    "price_max": 1000,
    "supplier": ["Supplier1", "Supplier2"]
  }
}
```

## 🎯 **Key Benefits**

### **1. Flexible Filtering**
- ✅ **Multiple values per field**: Search for multiple manufacturers, suppliers, brands, etc.
- ✅ **Combined filters**: Mix multiple values with other filters
- ✅ **Case-insensitive**: Works regardless of case
- ✅ **Partial matching**: Finds partial matches (e.g., "Adi" matches "Adidas")

### **2. Improved User Experience**
- ✅ **Single request**: Get multiple manufacturers in one API call
- ✅ **Reduced API calls**: No need for multiple requests
- ✅ **Better performance**: Efficient database queries
- ✅ **Consistent results**: Same logic across all endpoints

### **3. Developer-Friendly**
- ✅ **Simple syntax**: Just use comma-separated values
- ✅ **Backward compatible**: Existing single-value queries still work
- ✅ **Clear documentation**: Well-documented parameters
- ✅ **Consistent API**: Same pattern across all endpoints

## 🔧 **Technical Implementation**

### **1. Value Parsing**
```python
def split_comma_values(value):
    """Split comma-separated values and return list of trimmed values"""
    if not value:
        return []
    return [v.strip() for v in value.split(',') if v.strip()]
```

### **2. Search Logic**
```python
# For multiple values in the same field (OR logic)
if manufacturer_values:
    manufacturer_conditions = [Product.manufacturer.ilike(f"%{val}%") for val in manufacturer_values]
    search_conditions.append(or_(*manufacturer_conditions))

# For different fields (AND logic)
if search_conditions:
    query = query.filter(and_(*search_conditions))
```

### **3. Field Filters Response**
```python
# Return the actual values used in the search
field_filters["manufacturer"] = manufacturer_values
```

## 🎉 **Success Indicators**

✅ **Multiple manufacturers**: `manufacturer=Adidas,Apple,Bosch,Hasbro,Home Depot` returns products from any of these manufacturers

✅ **Combined filters**: `manufacturer=Adidas,Apple&price_max=1000` returns products that are (Adidas OR Apple) AND price ≤ 1000

✅ **Dynamic fields**: `field_name=color&field_value=Red,Blue,Green` returns products with any of these colors

✅ **Backward compatibility**: Single values still work as before

✅ **Performance**: Efficient queries with proper indexing

## 🚀 **Ready to Use**

Your PIM system now supports **advanced multi-value search and filtering** with:

- ✅ **Comma-separated values** for all searchable fields
- ✅ **Flexible matching** (case-insensitive, partial matching)
- ✅ **Combined filters** (AND logic across fields, OR logic within fields)
- ✅ **Consistent API** across all endpoints
- ✅ **Backward compatibility** with existing queries

**Start using it now!** 🎯 