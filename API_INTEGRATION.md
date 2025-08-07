# 🚀 PIM System API Integration Guide

This comprehensive guide covers everything you need to integrate with the Multi-Tenant Product Information Management (PIM) System API, including authentication, data uploads, and testing.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Authentication](#-authentication)
- [API Endpoints](#-api-endpoints)
- [CSV Upload Testing](#-csv-upload-testing)
- [Sample Data](#-sample-data)
- [Error Handling](#-error-handling)
- [Troubleshooting](#-troubleshooting)

## ✅ **Complete! Supabase Authentication Working**

Your PIM system now has **fully functional Supabase authentication**! Here's what's working:

### 🎯 **Successfully Implemented**

1. **✅ Supabase Integration**
   - Supabase client properly configured
   - Environment variables loaded correctly
   - Authentication service working

2. **✅ Authentication Endpoints**
   - `POST /api/v1/auth/signup` - Email signup ✅
   - `POST /api/v1/auth/login` - Email login ✅
   - `GET /api/v1/auth/providers` - Social providers ✅
   - `POST /api/v1/auth/signup/social` - Social signup ✅
   - `POST /api/v1/auth/login/social` - Social login ✅

3. **✅ Core Features**
   - CSV upload for categories and products ✅
   - Data management and CRUD operations ✅
   - File processing and validation ✅
   - Database operations ✅

### 🔧 **Current Configuration**

Your `.env` file is configured with:
```bash
SUPABASE_URL=https://hhxuxthwvpeplhtprnhf.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhoeHV4dGh3dnBlcGxodHBybmhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NjE3MjQsImV4cCI6MjA3MDAzNzcyNH0.1f9e_bPsbLtV9BiSrSO2IvHEf0ePSC8j1Ki_S2I-j_Y
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

### 🎯 **Quick Start**

### 1. Environment Setup

Your `.env` file is already configured! Just add your service role key:

```bash
# Get your service role key from:
# https://app.supabase.com/project/hhxuxthwvpeplhtprnhf/settings/api
SUPABASE_SERVICE_ROLE_KEY=your-actual-service-role-key-here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Server

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

### 4. Test the Integration

```bash
# Test signup (use real email addresses, not @example.com)
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@gmail.com", "password": "password123", "company_name": "Your Company"}'

# Test login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@gmail.com", "password": "password123"}'

# Test providers
curl -X GET "http://localhost:8000/api/v1/auth/providers"
```

### 📧 **Email Confirmation**

**Important**: Supabase may require email confirmation for new users. If login fails after signup:

1. **Check your email** for a confirmation link from Supabase
2. **Click the confirmation link** to verify your email
3. **Try logging in again** after confirmation

### 🔧 **Troubleshooting**

#### Common Issues

1. **"Email address is invalid"**
   - Use real email addresses (Gmail, Outlook, etc.)
   - Avoid `@example.com` or disposable email domains

2. **"Login failed" after signup**
   - Check if email confirmation is required
   - Verify email in Supabase dashboard
   - Try logging in again after email confirmation

3. **"Supabase authentication is not configured"**
   - Ensure `.env` file exists in project root
   - Check that `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set
   - Restart the server after updating `.env`

4. **"Failed to create user"**
   - Check Supabase project settings
   - Verify email authentication is enabled
   - Check if user already exists

#### Getting Service Role Key

1. Go to: https://app.supabase.com/project/hhxuxthwvpeplhtprnhf/settings/api
2. Copy the **"service_role" key** (NOT the anon key)
3. Update your `.env` file:
   ```bash
   SUPABASE_SERVICE_ROLE_KEY=your-actual-service-role-key-here
   ```
4. Restart the server

### 🎯 **Next Steps**

1. **Add Service Role Key**: Get it from Supabase dashboard
2. **Test Email Confirmation**: Check if emails are being sent
3. **Configure Social Login**: Set up Google, GitHub, Facebook providers
4. **Test Full Flow**: Signup → Email confirmation → Login → Use API

## 🔐 Authentication

### Supabase Setup

1. **Get Supabase Credentials**
   - Go to: https://app.supabase.com
   - Select your project: `https://hhxuxthwvpeplhtprnhf.supabase.co`
   - Navigate to **Settings > API**
   - Copy the **"anon/public" key** and **"service_role" key**

2. **Configure Authentication**
   - Go to Authentication > Settings
   - Enable email authentication
   - Configure social providers (Google, GitHub, Facebook) if needed

### Graceful Degradation

The application is designed to work **with or without** Supabase configuration:

- ✅ **With Supabase**: Full authentication features (signup, login, social login)
- ✅ **Without Supabase**: Core functionality works (CSV uploads, data management)
- ✅ **Mixed Mode**: Start without Supabase, add it later for authentication

#### When Supabase is Not Configured

If you try to use authentication endpoints without Supabase configuration, you'll get a helpful error message:

```json
{
  "detail": "Supabase authentication is not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
}
```

#### Core Features That Work Without Supabase

- ✅ CSV upload for categories and products
- ✅ Data management and CRUD operations
- ✅ File processing and validation
- ✅ Database operations
- ✅ API endpoints (except authentication)

### Authentication Endpoints

#### POST /api/v1/auth/signup
**Email signup with Supabase**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "strongpassword",
    "company_name": "Acme Inc"
  }'
```

**Response:**
```json
{
  "msg": "Signup successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "tenant_id": 1,
    "role": "admin"
  },
  "access_token": "jwt.token.here",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/login
**Email login with Supabase**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "strongpassword"
  }'
```

**Response:**
```json
{
  "access_token": "jwt.token.here",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "tenant_id": 1,
    "role": "admin"
  }
}
```

#### POST /api/v1/auth/signup/social
**Social signup (Google, GitHub, Facebook)**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup/social" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google",
    "access_token": "oauth_access_token_here",
    "company_name": "Acme Inc"
  }'
```

#### GET /api/v1/auth/me
**Get current user details**

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "admin",
  "tenant": {
    "id": 1,
    "company_name": "Acme Inc",
    "logo_url": "https://example.com/logo.png",
    "created_at": "2024-07-06T12:00:00Z"
  }
}
```

#### GET /api/v1/auth/providers
**Get available social providers**

```bash
curl -X GET "http://localhost:8000/api/v1/auth/providers"
```

**Response:**
```json
{
  "providers": [
    {
      "name": "google",
      "display_name": "Google",
      "icon": "google"
    },
    {
      "name": "github",
      "display_name": "GitHub",
      "icon": "github"
    },
    {
      "name": "facebook",
      "display_name": "Facebook",
      "icon": "facebook"
    }
  ]
}
```

## 📊 API Endpoints

### Categories

#### POST /api/v1/categories/upload
**Upload category CSV file**

```bash
curl -X POST "http://localhost:8000/api/v1/categories/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/categories_minimal.csv"
```

**Response:**
```json
{
  "msg": "Successfully uploaded 5 categories",
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "description": "Electronic devices and accessories",
      "schema_json": {}
    }
  ]
}
```

#### GET /api/v1/categories
**List all categories**

```bash
curl -X GET "http://localhost:8000/api/v1/categories"
```

#### GET /api/v1/categories/{id}/schema
**Get category schema**

```bash
curl -X GET "http://localhost:8000/api/v1/categories/1/schema"
```

### Products

#### POST /api/v1/products/upload
**Upload product CSV file**

```bash
curl -X POST "http://localhost:8000/api/v1/products/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/products_minimal.csv"
```

**Response:**
```json
{
  "msg": "Successfully uploaded 5 products",
  "products": [
    {
      "id": 1,
      "sku_id": "SKU001",
      "category_id": 1,
      "price": 299.99,
      "manufacturer": "Sony",
      "supplier": "Electronics Supplier",
      "image_url": null,
      "additional_data_count": 2
    }
  ]
}
```

#### GET /api/v1/products
**List products with filters**

```bash
curl -X GET "http://localhost:8000/api/v1/products?category_id=1&search=sony"
```

#### GET /api/v1/products/{id}
**Get specific product**

```bash
curl -X GET "http://localhost:8000/api/v1/products/1"
```

#### PUT /api/v1/products/{id}
**Update product**

```bash
curl -X PUT "http://localhost:8000/api/v1/products/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 189.99
  }'
```

### Tenant Management

#### POST /api/v1/tenant
**Create a new tenant (admin only)**

```bash
curl -X POST "http://localhost:8000/api/v1/tenant" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "company_name": "Acme Inc",
    "logo_url": "https://example.com/logo.png"
  }'
```

**Response:**
```json
{
  "id": 1,
  "company_name": "Acme Inc",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2024-07-06T12:00:00Z"
}
```

**Note**: Users can only create one tenant. If a user already has a tenant, this endpoint will return an error.

#### GET /api/v1/tenant/me
**Get current user's tenant details**

```bash
curl -X GET "http://localhost:8000/api/v1/tenant/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "company_name": "Acme Inc",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2024-07-06T12:00:00Z"
}
```

#### PATCH /api/v1/tenant/{id}
**Update tenant details (admin only)**

```bash
curl -X PATCH "http://localhost:8000/api/v1/tenant/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "company_name": "Updated Company Name",
    "logo_url": "https://example.com/new-logo.png"
  }'
```

### Field Configuration

The system provides field configuration management to control which fields are searchable, editable, primary, secondary, and have search indexes. **Field configurations are real-time data-driven** - only fields that actually exist in the tenant's product data are shown and can be configured.

#### GET /api/v1/products/fields/configuration
**Get all field configurations for the current tenant (real-time data only)**

```bash
curl -X GET "http://localhost:8000/api/v1/products/fields/configuration" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "msg": "Successfully retrieved 5 field configurations (real-time data)",
  "field_configurations": [
    {
      "id": 1,
      "field_name": "sku_id",
      "field_label": "Stock Keeping Unit ID",
      "field_type": "string",
      "is_searchable": true,
      "is_editable": true,
      "is_primary": true,
      "is_secondary": false,
      "display_order": 1,
      "description": "Unique product identifier",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "field_name": "price",
      "field_label": "Price",
      "field_type": "number",
      "is_searchable": true,
      "is_editable": true,
      "is_primary": false,
      "is_secondary": true,
      "display_order": 2,
      "description": "Product price",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 3,
      "field_name": "brand",
      "field_label": "Brand Name",
      "field_type": "string",
      "is_searchable": true,
      "is_editable": true,
      "is_primary": false,
      "is_secondary": true,
      "display_order": 3,
      "description": "Product brand name",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 5,
  "actual_fields_count": 5
}
```

#### POST /api/v1/products/fields/configuration
**Set field configurations for the current tenant (real-time data only)**

```bash
curl -X POST "http://localhost:8000/api/v1/products/fields/configuration" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '[
    {
      "field_name": "brand",
      "field_label": "Brand Name",
      "field_type": "string",
      "is_searchable": true,
      "is_editable": true,
      "is_primary": false,
      "is_secondary": true,
      "display_order": 3,
      "description": "Product brand name"
    },
    {
      "field_name": "warranty",
      "field_label": "Warranty Period",
      "field_type": "string",
      "is_searchable": false,
      "is_editable": true,
      "is_primary": false,
      "is_secondary": false,
      "display_order": 4,
      "description": "Product warranty period"
    }
  ]'
```

**Response:**
```json
{
  "msg": "Successfully set 2 field configurations (real-time data)",
  "created_count": 1,
  "updated_count": 1,
  "total_count": 2,
  "actual_fields_count": 5,
  "field_configurations": [
    {
      "id": 3,
      "field_name": "brand",
      "field_label": "Brand Name",
      "field_type": "string",
      "is_searchable": true,
      "is_editable": true,
      "is_primary": false,
      "is_secondary": true,
      "display_order": 3,
      "description": "Product brand name"
    },
    {
      "id": 4,
      "field_name": "warranty",
      "field_label": "Warranty Period",
      "field_type": "string",
      "is_searchable": false,
      "is_editable": true,
      "is_primary": false,
      "is_secondary": false,
      "display_order": 4,
      "description": "Product warranty period"
    }
  ]
}
```

#### PUT /api/v1/products/fields/configuration/{field_name}
**Update a specific field configuration (real-time data only)**

```bash
curl -X PUT "http://localhost:8000/api/v1/products/fields/configuration/brand" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "is_searchable": true,
    "is_editable": true,
    "is_primary": false,
    "is_secondary": true,
    "display_order": 2,
    "description": "Product brand name (updated)"
  }'
```

**Response:**
```json
{
  "msg": "Successfully updated field configuration for brand (real-time data)",
  "field_configuration": {
    "id": 3,
    "field_name": "brand",
    "field_label": "Brand Name",
    "field_type": "string",
    "is_searchable": true,
    "is_editable": true,
    "is_primary": false,
    "is_secondary": true,
    "display_order": 2,
    "description": "Product brand name (updated)",
    "updated_at": "2024-01-15T11:00:00Z"
  },
  "actual_fields_count": 5
}
```

### Field Configuration Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `is_searchable` | boolean | Can this field be searched? (implies search index) | false |
| `is_editable` | boolean | Can this field be edited? | true |
| `is_primary` | boolean | Is this a primary field (e.g., sku_id)? | false |
| `is_secondary` | boolean | Is this a secondary field (e.g., price, manufacturer)? | false |
| `display_order` | integer | Order for displaying fields in UI | 0 |
| `description` | string | Human-readable description of the field | "" |

### Real-Time Data-Driven Configuration

**Key Features:**
- ✅ **Only Actual Fields**: Only fields that exist in the tenant's product data are shown
- ✅ **Real-Time Updates**: Field configurations update automatically when new fields are added to products
- ✅ **Data Validation**: Cannot configure fields that don't exist in the tenant's data
- ✅ **Automatic Discovery**: New fields are automatically discovered when products are uploaded
- ✅ **Tenant Isolation**: Each tenant only sees their own actual fields

**How It Works:**
1. **Field Discovery**: System scans all products in the tenant's data
2. **Standard Fields**: Checks for `sku_id`, `price`, `manufacturer`, `supplier`, `image_url`, `category_id`
3. **Additional Data**: Scans `product_additional_data` table for custom fields
4. **Configuration**: Only shows and allows configuration of fields that actually exist
5. **Automatic Updates**: When new products are uploaded, new fields are automatically discovered

**Example:**
- If a tenant has products with fields: `sku_id`, `price`, `brand`, `warranty`
- Only these 4 fields will appear in field configurations
- Cannot configure fields like `color` or `size` if they don't exist in the data

### Field Types

- **string**: Text fields (e.g., brand, manufacturer)
- **number**: Numeric fields (e.g., price, weight)
- **boolean**: True/false fields (e.g., in_stock, featured)
- **date**: Date fields (e.g., expiry_date, created_at)

### Search and Filtering

The system now supports **advanced field-specific search** with comprehensive search capabilities:

#### 🔍 **Enhanced Search Features**

1. **General Search**
   - Search across all searchable fields with a single query
   - Example: `?search=sony` searches in all searchable fields

2. **Field-Specific Search**
   - **SKU ID**: `?sku_id=SKU001`
   - **Manufacturer**: `?manufacturer=Sony`
   - **Supplier**: `?supplier=Electronics`
   - **Brand**: `?brand=PlayStation` (additional data field)
   - **Price**: `?price=299.99` (exact price)
   - **Price Range**: `?price_min=100&price_max=500`
   - **Dynamic Fields**: `?field_name=color&field_value=red`

3. **Combined Search**
   - Multiple field-specific parameters in a single request
   - Example: `?manufacturer=Sony&price_min=200&price_max=400`

4. **Dedicated Search Endpoint**
   - `GET /api/v1/search` - Specialized search endpoint
   - Supports all field-specific parameters
   - Returns search metadata and field filters

#### Search in Searchable Fields Only
```bash
# General search across all searchable fields
curl -X GET "http://localhost:8000/api/v1/products?search=sony" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Field-Specific Search Parameters
```bash
# Search by SKU ID
curl -X GET "http://localhost:8000/api/v1/products?sku_id=SKU001" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Search by manufacturer
curl -X GET "http://localhost:8000/api/v1/products?manufacturer=Sony" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Search by supplier
curl -X GET "http://localhost:8000/api/v1/products?supplier=Electronics" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Search by brand (additional data field)
curl -X GET "http://localhost:8000/api/v1/products?brand=Sony" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Search by exact price
curl -X GET "http://localhost:8000/api/v1/products?price=299.99" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Search by price range
curl -X GET "http://localhost:8000/api/v1/products?price_min=100&price_max=500" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Dynamic field search (for additional data fields)
curl -X GET "http://localhost:8000/api/v1/products?field_name=color&field_value=red" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Combined Field-Specific Search
```bash
# Search by manufacturer and price range
curl -X GET "http://localhost:8000/api/v1/products?manufacturer=Sony&price_min=200&price_max=400" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Search by brand and category
curl -X GET "http://localhost:8000/api/v1/products?brand=Sony&category_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Search by multiple fields
curl -X GET "http://localhost:8000/api/v1/products?manufacturer=Sony&supplier=Electronics&price_min=100" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Search Endpoint (Dedicated Search)
```bash
# General search across all searchable fields
curl -X GET "http://localhost:8000/api/v1/search?q=sony" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Field-specific search using the search endpoint
curl -X GET "http://localhost:8000/api/v1/search?manufacturer=Sony&brand=PlayStation" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Price range search
curl -X GET "http://localhost:8000/api/v1/search?price_min=100&price_max=500" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Dynamic field search
curl -X GET "http://localhost:8000/api/v1/search?field_name=color&field_value=black" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Filter by Field Type
```bash
# Return only products with primary fields
curl -X GET "http://localhost:8000/api/v1/products?field_type=primary" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Return only products with secondary fields
curl -X GET "http://localhost:8000/api/v1/products?field_type=secondary" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Return all products (default)
curl -X GET "http://localhost:8000/api/v1/products?field_type=all" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Combined Search and Filtering
```bash
# Search in searchable fields and filter by primary fields
curl -X GET "http://localhost:8000/api/v1/products?search=sony&field_type=primary" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Field-specific search with field type filtering
curl -X GET "http://localhost:8000/api/v1/products?manufacturer=Sony&field_type=primary" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Search in searchable fields and filter by secondary fields
curl -X GET "http://localhost:8000/api/v1/products?search=sony&field_type=secondary" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Legacy Parameters (Deprecated)
```bash
# Legacy primary field filtering (use field_type=primary instead)
curl -X GET "http://localhost:8000/api/v1/products?primary_only=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Legacy secondary field filtering (use field_type=secondary instead)
curl -X GET "http://localhost:8000/api/v1/products?secondary_only=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 🔍 Filter Data Endpoints

The system provides dedicated endpoints to get unique filter data for building search interfaces and dropdowns.

#### Get All Filter Data
```bash
# Get all available filters in a single request
curl -X GET "http://localhost:8000/api/v1/products/filters/all" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "filters": {
    "manufacturer": ["Sony", "Samsung", "Apple"],
    "supplier": ["Electronics Supplier", "Tech Store"],
    "brand": ["PlayStation", "Galaxy", "iPhone"],
    "categories": [
      {
        "id": 1,
        "name": "Electronics",
        "description": "Electronic products"
      },
      {
        "id": 2,
        "name": "Gaming",
        "description": "Gaming products"
      }
    ],
    "price_range": {
      "min": 99.99,
      "max": 999.99,
      "currency": "USD"
    },
    "sku_id": ["SKU001", "SKU002", "SKU003"]
  },
  "searchable_fields": ["manufacturer", "supplier", "brand", "category_id", "price", "sku_id"],
  "total_filters": 6,
  "field_counts": {
    "manufacturer": 3,
    "supplier": 2,
    "brand": 3,
    "categories": 2,
    "price_range": 1,
    "sku_id": 3
  }
}
```

#### Get Specific Field Filter Data
```bash
# Get unique data for a specific field
curl -X GET "http://localhost:8000/api/v1/products/filters/unique-data?field_name=brand" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "filters": {
    "brand": ["PlayStation", "Galaxy", "iPhone"]
  },
  "searchable_fields": ["brand"],
  "field_name": "brand"
}
```

#### Get Brand Names
```bash
# Get unique brand names for filtering
curl -X GET "http://localhost:8000/api/v1/products/filters/brands" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "brands": ["PlayStation", "Galaxy", "iPhone"],
  "total_count": 3
}
```

#### Get Manufacturer Names
```bash
# Get unique manufacturer names for filtering
curl -X GET "http://localhost:8000/api/v1/products/filters/manufacturers" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "manufacturers": ["Sony", "Samsung", "Apple"],
  "total_count": 3
}
```

#### Get Supplier Names
```bash
# Get unique supplier names for filtering
curl -X GET "http://localhost:8000/api/v1/products/filters/suppliers" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "suppliers": ["Electronics Supplier", "Tech Store"],
  "total_count": 2
}
```

#### Get Categories
```bash
# Get unique categories for filtering
curl -X GET "http://localhost:8000/api/v1/products/filters/categories" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "description": "Electronic products"
    },
    {
      "id": 2,
      "name": "Gaming",
      "description": "Gaming products"
    }
  ],
  "total_count": 2
}
```

#### Get Price Range
```bash
# Get price range for filtering
curl -X GET "http://localhost:8000/api/v1/products/filters/price-range" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "price_range": {
    "min": 99.99,
    "max": 999.99
  },
  "currency": "USD"
}
```

### 🎯 Filter Usage Examples

#### Building Search Interface
```bash
# Step 1: Get all available filters
curl -X GET "http://localhost:8000/api/v1/products/filters/all" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Step 2: Use filters in search
curl -X GET "http://localhost:8000/api/v1/products?brand=PlayStation&manufacturer=Sony" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Dynamic Filter Dropdowns
```bash
# Get brands for dropdown
curl -X GET "http://localhost:8000/api/v1/products/filters/brands" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get manufacturers for dropdown
curl -X GET "http://localhost:8000/api/v1/products/filters/manufacturers" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get categories for dropdown
curl -X GET "http://localhost:8000/api/v1/products/filters/categories" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Price Range Slider
```bash
# Get price range for slider component
curl -X GET "http://localhost:8000/api/v1/products/filters/price-range" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Use price range in search
curl -X GET "http://localhost:8000/api/v1/products?price_min=100&price_max=500" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Field Type Filtering Examples

#### Example 1: View Products with Primary Fields Only
```bash
curl -X GET "http://localhost:8000/api/v1/products?field_type=primary" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "products": [
    {
      "id": 1,
      "sku_id": "SKU001",
      "category_id": 1,
      "price": 299.99,
      "manufacturer": "Sony",
      "supplier": "Electronics Supplier",
      "image_url": "https://example.com/sony-tv.jpg",
      "additional_data_count": 2
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 100,
  "field_type": "primary"
}
```

#### Example 2: View Products with Secondary Fields Only
```bash
curl -X GET "http://localhost:8000/api/v1/products?field_type=secondary" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "products": [
    {
      "id": 2,
      "sku_id": "SKU002",
      "category_id": 1,
      "price": 199.99,
      "manufacturer": "Samsung",
      "supplier": "Electronics Supplier",
      "image_url": "https://example.com/samsung-phone.jpg",
      "additional_data_count": 1
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 100,
  "field_type": "secondary"
}
```

#### Example 3: View All Products (Default)
```bash
curl -X GET "http://localhost:8000/api/v1/products?field_type=all" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "products": [
    {
      "id": 1,
      "sku_id": "SKU001",
      "category_id": 1,
      "price": 299.99,
      "manufacturer": "Sony",
      "supplier": "Electronics Supplier",
      "image_url": "https://example.com/sony-tv.jpg",
      "additional_data_count": 2
    },
    {
      "id": 2,
      "sku_id": "SKU002",
      "category_id": 1,
      "price": 199.99,
      "manufacturer": "Samsung",
      "supplier": "Electronics Supplier",
      "image_url": "https://example.com/samsung-phone.jpg",
      "additional_data_count": 1
    }
  ],
  "total_count": 2,
  "skip": 0,
  "limit": 100,
  "field_type": "all"
}
```

#### Example 4: Combined Search and Field Type Filtering
```bash
curl -X GET "http://localhost:8000/api/v1/products?search=sony&field_type=primary" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "products": [
    {
      "id": 1,
      "sku_id": "SKU001",
      "category_id": 1,
      "price": 299.99,
      "manufacturer": "Sony",
      "supplier": "Electronics Supplier",
      "image_url": "https://example.com/sony-tv.jpg",
      "additional_data_count": 2
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 100,
  "field_type": "primary"
}
```

### Editable Field Validation

When updating products, only fields marked as `is_editable: true` can be modified:

```bash
# This will fail if 'brand' is not marked as editable
curl -X PUT "http://localhost:8000/api/v1/products/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "brand": "Sony"
  }'
```

**Error Response:**
```json
{
  "detail": "The following fields are not editable: brand"
}
```

## 📁 CSV Upload Testing

### AI-Enhanced Upload Process

The system now supports **AI-enhanced upload process** for better data management:

1. **Analyze & Load Data**: Upload CSV → AI analysis → Parse and format data → Display for editing (NO database save)
2. **Upload & Save Data**: Upload CSV → AI analysis → Direct saving to database

#### Product Upload Process

##### Step 1: Analyze and Load Product Data (No Database Save)
**POST /api/v1/products/upload/analyze**

This endpoint analyzes the file using AI and loads the data for editing, but **does not save anything to the database**. It's purely for analysis and data preparation.

```bash
curl -X POST "http://localhost:8000/api/v1/products/upload/analyze" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@sample_data/products_minimal.csv"
```

**Response:**
```json
{
  "msg": "Successfully analyzed and loaded 5 products for editing (AI-enhanced)",
  "file_name": "products_minimal.csv",
  "total_rows": 5,
  "headers": ["sku_id", "price", "manufacturer", "supplier"],
  "products": [
    {
      "index": 0,
      "sku_id": "SKU001",
      "category_id": 1,
      "price": 299.99,
      "manufacturer": "Sony",
      "supplier": "Electronics Supplier",
      "image_url": "",
      "additional_data": [],
      "validation_status": "valid",
      "validation_errors": [],
      "is_edited": false
    }
  ],
  "total_count": 5,
  "valid_count": 5,
  "error_count": 0,
  "warning_count": 0,
  "field_mappings": [
    {
      "original_field_name": "sku_id",
      "normalized_field_name": "sku_id",
      "field_label": "Stock Keeping Unit ID",
      "field_type": "string",
      "is_standard_field": true
    }
  ],
  "validation_results": {
    "overall_quality": "good",
    "recommendations": ["Data quality is excellent"]
  },
  "analysis": {
    "is_product_data": true,
    "confidence": 0.9,
    "standard_fields_found": ["sku_id", "price", "manufacturer"],
    "additional_fields_found": []
  }
}
```

**Note**: This step does NOT save any data to the database. It only analyzes and prepares the data for editing.

##### Step 2: Upload and Save Product Data (Database Save)
**POST /api/v1/products/upload**

This endpoint uploads the file, analyzes it with AI, and **saves the data directly to the database**. Use this when you want to immediately save the products.

```bash
curl -X POST "http://localhost:8000/api/v1/products/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@sample_data/products_minimal.csv"
```

**Response:**
```json
{
  "msg": "Successfully uploaded and saved 5 products (AI-enhanced)",
  "file_name": "products_minimal.csv",
  "total_rows": 5,
  "products": [
    {
      "id": 73,
      "sku_id": "SKU001",
      "category_id": 1,
      "price": 299.99,
      "manufacturer": "Sony",
      "supplier": "Electronics Supplier",
      "image_url": "",
      "additional_data_count": 0
    }
  ],
  "created_count": 5,
  "total_count": 5,
  "field_mappings": [
    {
      "id": 1,
      "original_field_name": "sku_id",
      "normalized_field_name": "sku_id",
      "field_label": "Stock Keeping Unit ID",
      "field_type": "string",
      "is_standard_field": true
    }
  ],
  "analysis": {
    "is_product_data": true,
    "confidence": 0.9,
    "standard_fields_found": ["sku_id", "price", "manufacturer"],
    "additional_fields_found": []
  }
}
```

#### Category Upload Process

##### Step 1: Load Category Data
**POST /api/v1/categories/upload/load**

```bash
curl -X POST "http://localhost:8000/api/v1/categories/upload/load" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@sample_data/categories_minimal.csv"
```

**Response:**
```json
{
  "msg": "Successfully loaded 5 categories for editing",
  "categories": [
    {
      "index": 0,
      "name": "Electronics",
      "description": "Electronic devices and accessories",
      "schema_json": {},
      "validation_status": "valid",
      "validation_errors": [],
      "is_edited": false
    }
  ],
  "total_count": 5,
  "valid_count": 5,
  "error_count": 0,
  "warning_count": 0
}
```

##### Step 2: Save Edited Category Data
**POST /api/v1/categories/upload/save**

```bash
curl -X POST "http://localhost:8000/api/v1/categories/upload/save" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '[
    {
      "index": 0,
      "name": "Electronics",
      "description": "Electronic devices and accessories (Enhanced)",
      "schema_json": {},
      "validation_status": "valid",
      "validation_errors": [],
      "is_edited": true
    }
  ]'
```

**Response:**
```json
{
  "msg": "Successfully saved 1 categories",
  "categories": [
    {
      "id": 40,
      "name": "Electronics",
      "description": "Electronic devices and accessories (Enhanced)",
      "schema_json": {}
    }
  ],
  "created_count": 1,
  "total_count": 1
}
```

### Benefits of Two-Step Upload

1. **🔍 Data Validation**: Validate data before saving to database
2. **✏️ Live Editing**: Edit data in real-time before saving
3. **🚨 Error Handling**: Identify and fix errors before saving
4. **📊 Data Preview**: Preview formatted data before committing
5. **🔄 Batch Operations**: Process multiple items efficiently
6. **💾 Selective Saving**: Save only edited or valid items

### Validation Features

- **Required Fields**: SKU ID for products, Name for categories
- **Data Types**: Price validation, category_id validation
- **Business Rules**: Negative price prevention, duplicate detection
- **Error Reporting**: Detailed error messages with row indices
- **Status Tracking**: Valid, warning, error status for each item

### Sample Files Location

All sample files are located in the `sample_data/` directory:

- `categories.csv` - Full categories with schema
- `categories_minimal.csv` - Simple categories without schema
- `products.csv` - Full products with dynamic fields
- `products_minimal.csv` - Simple products with basic fields

### CSV Format Specifications

#### Category CSV Format

**Minimal Format:**
```csv
name,description
Electronics,Electronic devices and accessories
Clothing,Apparel and fashion items
Home & Garden,Home improvement and garden products
```

**Full Format with Schema:**
```csv
name,description,schema_json
Electronics,Electronic devices and accessories,"{""fields"":[{""name"":""brand"",""type"":""string"",""required"":true},{""name"":""warranty"",""type"":""string"",""required"":false}]}"
Clothing,Apparel and fashion items,"{""fields"":[{""name"":""size"",""type"":""string"",""required"":true},{""name"":""color"",""type"":""string"",""required"":true}]}"
```

#### Product CSV Format

**Minimal Format:**
```csv
sku_id,category_id,price,manufacturer,supplier
SKU001,1,299.99,Sony,Electronics Supplier
SKU002,1,199.99,Samsung,Electronics Supplier
SKU003,2,49.99,Nike,Clothing Supplier
```

**Full Format with Dynamic Fields:**
```csv
sku_id,category_id,price,manufacturer,supplier,image_url,brand,warranty,power_consumption,size,color,material
SKU001,1,299.99,Sony,Electronics Supplier,https://example.com/sony-tv.jpg,Sony,2 years,150W,,,,
SKU002,1,199.99,Samsung,Electronics Supplier,https://example.com/samsung-phone.jpg,Samsung,1 year,25W,,,,
SKU003,2,49.99,Nike,Clothing Supplier,https://example.com/nike-shirt.jpg,,,M,Blue,Cotton,
```

### Testing Scenarios

#### 1. Basic Upload Test
```bash
# Upload minimal categories
curl -X POST "http://localhost:8000/api/v1/categories/upload" \
  -F "file=@sample_data/categories_minimal.csv"

# Upload minimal products
curl -X POST "http://localhost:8000/api/v1/products/upload" \
  -F "file=@sample_data/products_minimal.csv"
```

#### 2. Full Feature Test
```bash
# Upload categories with schema
curl -X POST "http://localhost:8000/api/v1/categories/upload" \
  -F "file=@sample_data/categories.csv"

# Upload products with dynamic fields
curl -X POST "http://localhost:8000/api/v1/products/upload" \
  -F "file=@sample_data/products.csv"
```

#### 3. Error Testing
```bash
# Test with missing required field
echo "description" > invalid_categories.csv
echo "Test description" >> invalid_categories.csv
curl -X POST "http://localhost:8000/api/v1/categories/upload" \
  -F "file=@invalid_categories.csv"

# Test with invalid data type
echo "sku_id,category_id,price" > invalid_products.csv
echo "SKU001,not_a_number,invalid_price" >> invalid_products.csv
curl -X POST "http://localhost:8000/api/v1/products/upload" \
  -F "file=@invalid_products.csv"
```

## 📊 Sample Data

### Categories Sample Data

**categories_minimal.csv:**
```csv
name,description
Electronics,Electronic devices and accessories
Clothing,Apparel and fashion items
Home & Garden,Home improvement and garden products
Sports & Outdoors,Sports equipment and outdoor gear
Books & Media,Books movies and digital media
```

**categories.csv (with schemas):**
```csv
name,description,schema_json
Electronics,Electronic devices and accessories,"{""fields"":[{""name"":""brand"",""type"":""string"",""required"":true},{""name"":""warranty"",""type"":""string"",""required"":false},{""name"":""power_consumption"",""type"":""number"",""required"":false}]}"
Clothing,Apparel and fashion items,"{""fields"":[{""name"":""size"",""type"":""string"",""required"":true},{""name"":""color"",""type"":""string"",""required"":true},{""name"":""material"",""type"":""string"",""required"":false},{""name"":""care_instructions"",""type"":""string"",""required"":false}]}"
Home & Garden,Home improvement and garden products,"{""fields"":[{""name"":""dimensions"",""type"":""string"",""required"":false},{""name"":""weight"",""type"":""number"",""required"":false},{""name"":""assembly_required"",""type"":""boolean"",""required"":false}]}"
Sports & Outdoors,Sports equipment and outdoor gear,"{""fields"":[{""name"":""sport_type"",""type"":""string"",""required"":true},{""name"":""skill_level"",""type"":""string"",""required"":false},{""name"":""age_range"",""type"":""string"",""required"":false}]}"
Books & Media,Books movies and digital media,"{""fields"":[{""name"":""author"",""type"":""string"",""required"":false},{""name"":""publisher"",""type"":""string"",""required"":false},{""name"":""isbn"",""type"":""string"",""required"":false},{""name"":""format"",""type"":""string"",""required"":false}]}"
Automotive,Vehicle parts and accessories,"{""fields"":[{""name"":""vehicle_type"",""type"":""string"",""required"":true},{""name"":""compatibility"",""type"":""string"",""required"":false},{""name"":""installation_difficulty"",""type"":""string"",""required"":false}]}"
Health & Beauty,Health and beauty products,"{""fields"":[{""name"":""skin_type"",""type"":""string"",""required"":false},{""name"":""ingredients"",""type"":""string"",""required"":false},{""name"":""expiry_date"",""type"":""date"",""required"":false}]}"
Toys & Games,Toys and entertainment products,"{""fields"":[{""name"":""age_group"",""type"":""string"",""required"":true},{""name"":""battery_required"",""type"":""boolean"",""required"":false},{""name"":""number_of_players"",""type"":""number"",""required"":false}]}"
```

### Products Sample Data

**products_minimal.csv:**
```csv
sku_id,category_id,price,manufacturer,supplier
SKU001,1,299.99,Sony,Electronics Supplier
SKU002,1,199.99,Samsung,Electronics Supplier
SKU003,2,49.99,Nike,Clothing Supplier
SKU004,2,79.99,Adidas,Clothing Supplier
SKU005,3,149.99,IKEA,Home Supplier
```

**products.csv (with dynamic fields):**
```csv
sku_id,category_id,price,manufacturer,supplier,image_url,brand,warranty,power_consumption,size,color,material,sport_type,skill_level,author,publisher,vehicle_type,compatibility,skin_type,ingredients,age_group,battery_required,number_of_players
SKU001,1,299.99,Sony,Electronics Supplier,https://example.com/sony-tv.jpg,Sony,2 years,150W,,,,,,,,,,,,,
SKU002,1,199.99,Samsung,Electronics Supplier,https://example.com/samsung-phone.jpg,Samsung,1 year,25W,,,,,,,,,,,,,
SKU003,2,49.99,Nike,Clothing Supplier,https://example.com/nike-shirt.jpg,,,M,Blue,Cotton,,,,,,,,,,
SKU004,2,79.99,Adidas,Clothing Supplier,https://example.com/adidas-shoes.jpg,,,10,Black,Leather,,,,,,,,,,
SKU005,3,149.99,IKEA,Home Supplier,https://example.com/ikea-table.jpg,,,,"120x60x75cm",,Wood,,,,,,,,,,
SKU006,4,89.99,Wilson,Sports Supplier,https://example.com/wilson-racket.jpg,,,Tennis,Intermediate,,,,,,,,,,
SKU007,5,19.99,Penguin Books,Book Supplier,https://example.com/book-cover.jpg,,,,"The Great Gatsby",Penguin Books,,,,,,,,,,
SKU008,6,45.99,Bosch,Auto Supplier,https://example.com/bosch-brake.jpg,,,Car,"Toyota Camry 2018-2022",,,,,,,,,,
SKU009,7,29.99,Neutrogena,Beauty Supplier,https://example.com/neutrogena-cream.jpg,,,,"Normal to Dry","Water Glycerin Hyaluronic Acid",,,,,,,,,,
SKU010,8,39.99,Hasbro,Toy Supplier,https://example.com/monopoly.jpg,,,,"8-12 years",Yes,2-8,,,,,,,,,
SKU011,1,399.99,Apple,Electronics Supplier,https://example.com/apple-laptop.jpg,Apple,3 years,65W,,,,,,,,,,,,,
SKU012,2,129.99,Levi's,Clothing Supplier,https://example.com/levis-jeans.jpg,,,32x32,Blue,Denim,,,,,,,,,,
SKU013,3,89.99,Home Depot,Garden Supplier,https://example.com/garden-tools.jpg,,,,"Heavy Duty",Steel,,,,,,,,,,
SKU014,4,159.99,Nike,Sports Supplier,https://example.com/nike-shoes.jpg,,,Running,Advanced,,,,,,,,,,
SKU015,5,24.99,Random House,Book Supplier,https://example.com/book-cover2.jpg,,,,"1984",Random House,,,,,,,,,,
```

## ⚠️ Error Handling

### Common Error Responses

#### Missing Required Field
```json
{
  "detail": "Row 2: sku_id is required"
}
```

#### Invalid Data Type
```json
{
  "detail": "Row 2: category_id must be an integer"
}
```

#### Invalid JSON Schema
```json
{
  "detail": "Row 6: schema_json must be valid JSON"
}
```

#### File Format Error
```json
{
  "detail": "File must be a CSV"
}
```

#### Authentication Error
```json
{
  "detail": "Could not validate credentials"
}
```

### Error Codes

- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error (server error)

## 🔧 Troubleshooting

### Common Issues

1. **File Encoding**
   - Ensure CSV files are UTF-8 encoded
   - Use text editor to verify encoding

2. **Missing Headers**
   - CSV must have header row
   - Headers must match expected field names

3. **Invalid JSON**
   - Check schema_json format
   - Use JSON validator for complex schemas

4. **Data Types**
   - `category_id` must be integer
   - `price` must be number
   - Other fields are strings

5. **Category References**
   - Ensure categories exist before uploading products
   - Check category_id values

6. **Authentication Issues**
   - Verify Supabase credentials
   - Check token expiration
   - Ensure proper Authorization header

### Debug Tips

1. **Check File Format**
   ```bash
   # View CSV content
   cat sample_data/categories_minimal.csv
   ```

2. **Validate JSON**
   ```bash
   # Test JSON format
   echo '{"fields":[{"name":"test","type":"string","required":true}]}' | python3 -m json.tool
   ```

3. **Test with Minimal Data**
   - Start with minimal CSV files
   - Add complexity gradually

4. **Check Server Logs**
   - Monitor server output for errors
   - Check for detailed error messages

5. **Verify Supabase Connection**
   ```bash
   # Test Supabase connection
   python3 test_supabase.py
   ```

### Testing Tools

#### Automated Test Script
```bash
# Run comprehensive tests
python3 test_uploads.py
```

#### Manual Testing
```bash
# Test server health
curl -X GET "http://localhost:8000/docs"

# Test authentication
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "company_name": "Test Company"}'
```

## 🎉 Success Criteria

Your API integration is working correctly when:

1. ✅ **Authentication works** - Users can sign up, login, and access protected endpoints
2. ✅ **CSV uploads work** - Categories and products can be uploaded via CSV
3. ✅ **Data integrity** - Uploaded data is correctly stored and retrieved
4. ✅ **Error handling** - Invalid requests return appropriate error messages
5. ✅ **Tenant isolation** - Data is properly isolated by tenant
6. ✅ **Dynamic fields** - Non-standard CSV columns become dynamic fields
7. ✅ **Schema validation** - Category schemas are properly validated and stored

## 🚀 Next Steps

1. **Production Deployment**
   - Configure environment variables for production
   - Set up HTTPS and proper security headers
   - Implement rate limiting and monitoring

2. **Enhanced Features**
   - Add file storage for uploaded files
   - Implement progress tracking for large uploads
   - Add data validation rules and constraints

3. **Integration**
   - Connect with frontend applications
   - Implement webhook notifications
   - Add API versioning

4. **Monitoring**
   - Set up logging and error tracking
   - Implement performance monitoring
   - Add usage analytics

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Supabase Documentation**: https://supabase.com/docs
- **CSV Format Specification**: https://tools.ietf.org/html/rfc4180
- **JSON Schema**: https://json-schema.org/ 

### Tenant Management

#### POST /api/v1/tenant
**Create a new tenant (admin only)**

```bash
curl -X POST "http://localhost:8000/api/v1/tenant" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "company_name": "Acme Inc",
    "logo_url": "https://example.com/logo.png"
  }'
```

**Response:**
```json
{
  "id": 1,
  "company_name": "Acme Inc",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2024-07-06T12:00:00Z"
}
```

**Note**: Users can only create one tenant. If a user already has a tenant, this endpoint will return an error.

#### GET /api/v1/tenant/me
**Get current user's tenant details**

```bash
curl -X GET "http://localhost:8000/api/v1/tenant/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "company_name": "Acme Inc",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2024-07-06T12:00:00Z"
}
```

#### PATCH /api/v1/tenant/{id}
**Update tenant details (admin only)**

```bash
curl -X PATCH "http://localhost:8000/api/v1/tenant/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "company_name": "Updated Company Name",
    "logo_url": "https://example.com/new-logo.png"
  }'
```

## 🔧 **Error Handling & Troubleshooting**

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid credentials
- **403 Forbidden**: Access denied (insufficient permissions)
- **404 Not Found**: Resource not found
- **405 Method Not Allowed**: HTTP method not supported for this endpoint
- **500 Internal Server Error**: Server error

### Detailed Error Responses

#### Authentication Errors

**401 Unauthorized**
```json
{
  "detail": "Could not validate credentials"
}
```
**Solution**: Check your JWT token and make sure it's valid and not expired.

**401 Invalid Credentials**
```json
{
  "detail": "Invalid credentials"
}
```
**Solution**: Verify your email and password are correct.

#### Tenant Errors

**400 User already has a tenant**
```json
{
  "detail": "User already has a tenant"
}
```
**Solution**: Users can only have one tenant. Use PATCH to update existing tenant.

**403 Access denied**
```json
{
  "detail": "Access denied"
}
```
**Solution**: Make sure you're trying to access your own tenant or have admin permissions.

#### Supabase Errors

**503 Supabase not configured**
```json
{
  "detail": "Supabase authentication is not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
}
```
**Solution**: Configure Supabase credentials in your `.env` file.

**400 Email already registered**
```json
{
  "detail": "Email already registered"
}
```
**Solution**: Use a different email address or try logging in instead.

### JWT Token Issues

If you're experiencing JWT token verification errors:

1. **Check token format**: Make sure the token starts with `Bearer `
2. **Verify token expiration**: Tokens expire after 24 hours by default
3. **Check SECRET_KEY**: Ensure the same secret is used for creation and verification
4. **Token signature**: Verify the token hasn't been tampered with

### Debugging Steps

1. **Check server logs** for detailed error messages
2. **Verify environment variables** are loaded correctly
3. **Test with curl** to isolate frontend issues
4. **Check database connectivity** and user existence
5. **Verify Supabase configuration** and connectivity

### Getting Help

If you encounter issues:

1. **Check the logs**: Look for detailed error messages in the server output
2. **Test endpoints**: Use the provided curl examples to test functionality
3. **Verify configuration**: Ensure all environment variables are set correctly
4. **Check documentation**: Review the API_INTEGRATION.md for detailed information 

## 🔒 **Tenant Scoping & Security**

### Multi-Tenant Architecture

The PIM system is built with **multi-tenant architecture** where:

- **Each user belongs to a tenant** (company/organization)
- **All data is scoped to the user's tenant**
- **Users can only access their own tenant's data**
- **Complete data isolation between tenants**

### Tenant Scoping Implementation

#### Authentication & Authorization

All endpoints require authentication via JWT token:

```bash
# Example: All requests require Authorization header
curl -X GET "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Data Scoping

**Products:**
- ✅ List only current tenant's products
- ✅ Create products for current tenant only
- ✅ Update/delete only current tenant's products
- ✅ Search within current tenant's products

**Categories:**
- ✅ List only current tenant's categories
- ✅ Create categories for current tenant only
- ✅ Update/delete only current tenant's categories
- ✅ Schema management for current tenant only

**Tenants:**
- ✅ Users can only access their own tenant
- ✅ Admin users can manage their tenant
- ✅ Complete isolation between tenants

### Security Features

1. **🔐 Authentication Required**
   - All endpoints require valid JWT token
   - Token contains user and tenant information
   - Automatic token validation and expiration

2. **🏢 Tenant Isolation**
   - Data filtered by `tenant_id` on all queries
   - Users cannot access other tenants' data
   - Complete data separation

3. **🛡️ Authorization**
   - Role-based access control (admin, user)
   - Tenant-scoped permissions
   - Proper error handling for unauthorized access

4. **🔍 Data Validation**
   - Input validation on all endpoints
   - Business rule enforcement
   - Duplicate detection within tenant scope

### Example: Tenant-Scoped Operations

#### List Products (Tenant-Scoped)
```bash
curl -X GET "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "products": [
    {
      "id": 73,
      "sku_id": "SKU001",
      "category_id": 1,
      "price": 329.99,
      "manufacturer": "Sony (Updated)",
      "supplier": "Electronics Supplier",
      "image_url": "",
      "additional_data_count": 0
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 100
}
```

#### Search Products (Tenant-Scoped)
```bash
# General search across all searchable fields
curl -X GET "http://localhost:8000/api/v1/products?search=Sony" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "products": [
    {
      "id": 73,
      "sku_id": "SKU001",
      "manufacturer": "Sony (Updated)"
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 100
}
```

#### Dedicated Search Endpoint
```bash
# General search
curl -X GET "http://localhost:8000/api/v1/search?q=sony" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Field-specific search
curl -X GET "http://localhost:8000/api/v1/search?manufacturer=Sony&brand=PlayStation" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Price range search
curl -X GET "http://localhost:8000/api/v1/search?price_min=100&price_max=500" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Dynamic field search
curl -X GET "http://localhost:8000/api/v1/search?field_name=color&field_value=black" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Search Endpoint Response:**
```json
{
  "products": [
    {
      "id": 73,
      "sku_id": "SKU001",
      "category_id": 1,
      "price": 329.99,
      "manufacturer": "Sony",
      "supplier": "Electronics Supplier",
      "image_url": "https://example.com/sony-tv.jpg",
      "additional_data_count": 2
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 100,
  "query": "sony",
  "searchable_fields": ["sku_id", "manufacturer", "brand", "price"],
  "field_filters": {
    "manufacturer": "Sony",
    "brand": "PlayStation"
  }
}
```

#### Field-Specific Search Examples
```bash
# Search by SKU ID
curl -X GET "http://localhost:8000/api/v1/products?sku_id=SKU001" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search by manufacturer
curl -X GET "http://localhost:8000/api/v1/products?manufacturer=Sony" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search by brand (additional data field)
curl -X GET "http://localhost:8000/api/v1/products?brand=PlayStation" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search by price range
curl -X GET "http://localhost:8000/api/v1/products?price_min=200&price_max=400" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search by exact price
curl -X GET "http://localhost:8000/api/v1/products?price=299.99" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Dynamic field search
curl -X GET "http://localhost:8000/api/v1/products?field_name=color&field_value=red" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Create Category (Tenant-Scoped)
```bash
curl -X POST "http://localhost:8000/api/v1/categories" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "New Category",
    "description": "Category for current tenant only",
    "schema_json": {}
  }'
```

**Response:**
```json
{
  "id": 45,
  "name": "New Category",
  "description": "Category for current tenant only",
  "schema_json": {}
}
```

### Tenant Management

#### Get Current Tenant
```bash
curl -X GET "http://localhost:8000/api/v1/tenant/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "id": 9,
  "company_name": "Test Company 456",
  "logo_url": null,
  "created_at": "2025-08-06T08:22:56.996256"
}
```

#### Update Tenant
```bash
curl -X PATCH "http://localhost:8000/api/v1/tenant/9" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "company_name": "Updated Company Name",
    "logo_url": "https://example.com/logo.png"
  }'
```

### Error Handling

#### Unauthorized Access
```json
{
  "detail": "Could not validate credentials"
}
```

#### Resource Not Found (Tenant-Scoped)
```json
{
  "detail": "Product not found"
}
```

#### Duplicate Resource (Tenant-Scoped)
```json
{
  "detail": "SKU ID already exists"
}
```

### Testing Tenant Scoping

Use the provided test script to verify tenant scoping:

```bash
# Run tenant scoping tests
python3 test_tenant_scoping.py
```

This will verify:
- ✅ Products are tenant-scoped
- ✅ Categories are tenant-scoped
- ✅ Search is tenant-scoped
- ✅ CRUD operations are tenant-scoped
- ✅ Data isolation between tenants 

## 🤖 **AI-Enhanced Upload Process**

### Overview

The PIM system now includes **AI-powered file analysis** using Google Gemini to:

1. **🔍 Detect Product Data**: Automatically identify if uploaded files contain product information
2. **🗂️ Normalize Fields**: Convert field names to standardized format (snake_case)
3. **📊 Infer Data Types**: Automatically determine appropriate data types
4. **✅ Validate Data**: Assess data quality and provide recommendations
5. **🔄 Handle Additional Data**: Store extra fields in separate table
6. **📏 Enforce Limits**: Maximum 500 products per upload

### AI Service Configuration

The system uses **Google Gemini AI** for intelligent file processing:

```python
# API Key (configured in ai_service.py)
GEMINI_API_KEY = "AIzaSyCezud7CjyXwl8LVnbWwrHkNuJ95fQWe6U"
```

### AI-Enhanced Upload Endpoints

#### POST /api/v1/products/upload/analyze
**Analyze file content using AI and load for editing**

```
```