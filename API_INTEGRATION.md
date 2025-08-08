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
- [Superadmin Management](#-superadmin-management)

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

Supports direct URL pasting for logo:
- Accepts any valid URL pointing to an image
- Common formats: .jpg, .jpeg, .png, .gif, .svg, .webp, .bmp, .tiff
- Also accepts URLs with image-related keywords in the path

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

Supports direct URL pasting for logo:
- Accepts any valid URL pointing to an image
- Common formats: .jpg, .jpeg, .png, .gif, .svg, .webp, .bmp, .tiff
- Also accepts URLs with image-related keywords in the path
- Empty string or null removes the logo

```bash
curl -X PATCH "http://localhost:8000/api/v1/tenant/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "company_name": "Updated Company Name",
    "logo_url": "https://example.com/new-logo.png"
  }'
```

**Response:**
```json
{
  "id": 1,
  "company_name": "Updated Company Name",
  "logo_url": "https://example.com/new-logo.png",
  "created_at": "2024-07-06T12:00:00Z"
}
```

#### POST /api/v1/tenant/{id}/logo/validate
**Validate a logo URL before saving it**

This endpoint helps frontend validate URLs before submitting.

```bash
curl -X POST "http://localhost:8000/api/v1/tenant/1/logo/validate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "logo_url": "https://example.com/logo.png"
  }'
```

**Response:**
```json
{
  "valid": true,
  "message": "Valid logo URL",
  "logo_url": "https://example.com/logo.png"
}
```

**Invalid URL Response:**
```json
{
  "valid": false,
  "message": "Invalid logo URL. Please provide a valid URL pointing to an image file.",
  "logo_url": null
}
```

### Onboarding & Settings

#### GET /api/v1/progress/steps
**Get all onboarding steps with progress**

```bash
curl -X GET "http://localhost:8000/api/v1/progress/steps" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "tenant_id": 1,
  "steps": [
    {
      "step_key": "company_setup",
      "title": "Company Setup",
      "description": "Basic company information and branding",
      "order": 1,
      "is_required": true,
      "category": "setup",
      "icon": "🏢",
      "estimated_time": 5,
      "is_completed": true,
      "completed_at": "2024-01-15T10:30:00Z",
      "data": {
        "company_name": "Acme Inc",
        "logo_url": "https://example.com/logo.png"
      }
    }
  ],
  "total_steps": 6,
  "completed_steps": 1,
  "progress_percentage": 16.7
}
```

#### POST /api/v1/progress/steps/company_setup/complete
**Complete company setup during onboarding**

Supports direct URL pasting for logo:
- Accepts any valid URL pointing to an image
- Common formats: .jpg, .jpeg, .png, .gif, .svg, .webp, .bmp, .tiff
- Also accepts URLs with image-related keywords in the path

```bash
curl -X POST "http://localhost:8000/api/v1/progress/steps/company_setup/complete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "company_name": "My Company",
    "logo_url": "https://example.com/logo.png"
  }'
```

**Response:**
```json
{
  "step_key": "company_setup",
  "is_completed": true,
  "completed_at": "2024-01-15T10:30:00Z",
  "data": {
    "company_name": "My Company",
    "logo_url": "https://example.com/logo.png"
  }
}
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

### Superadmin Management

The system provides comprehensive superadmin functionality for managing users, tenants, products, and audit logs across the entire platform.

#### Role-Based Access Control

**User Roles:**
- **superadmin**: Full access to all data and functionality
- **analyst**: View-only access to all data (no editing)
- **tenant_admin**: Admin access to their own tenant
- **tenant_user**: Standard user access to their own tenant

#### GET /api/v1/superadmin/dashboard
**Get superadmin dashboard statistics**

```bash
curl -X GET "http://localhost:8000/api/v1/superadmin/dashboard" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "statistics": {
    "total_users": 150,
    "total_tenants": 25,
    "total_products": 1250,
    "total_categories": 45,
    "blocked_users": 3
  },
  "users_by_role": {
    "superadmin": 2,
    "analyst": 5,
    "tenant_admin": 25,
    "tenant_user": 118
  },
  "recent_activity": [
    {
      "id": 1234,
      "user_email": "admin@example.com",
      "action": "create",
      "resource_type": "user",
      "resource_name": "newuser@example.com",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### GET /api/v1/superadmin/users
**List all users (superadmin and analyst only)**

```bash
curl -X GET "http://localhost:8000/api/v1/superadmin/users?role=tenant_user&is_active=true&search=john" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Query Parameters:**
- `role`: Filter by user role (superadmin, analyst, tenant_admin, tenant_user)
- `tenant_id`: Filter by tenant ID
- `is_active`: Filter by active status (true/false)
- `is_blocked`: Filter by blocked status (true/false)
- `search`: Search in email, first_name, last_name
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum number of records to return

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "role": "tenant_user",
      "tenant_id": 1,
      "tenant_name": "Acme Inc",
      "is_active": true,
      "is_blocked": false,
      "last_login": "2024-01-15T09:30:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T09:30:00Z",
      "created_by": 1,
      "notes": "Active user"
    }
  ],
  "total_count": 150,
  "skip": 0,
  "limit": 100
}
```

#### GET /api/v1/superadmin/users/{user_id}
**Get detailed user information**

```bash
curl -X GET "http://localhost:8000/api/v1/superadmin/users/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "role": "tenant_user",
  "tenant_id": 1,
  "tenant_name": "Acme Inc",
  "is_active": true,
  "is_blocked": false,
  "last_login": "2024-01-15T09:30:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T09:30:00Z",
  "created_by": 1,
  "notes": "Active user",
  "audit_logs_count": 45
}
```

#### POST /api/v1/superadmin/users
**Create a new user (superadmin only)**

```bash
curl -X POST "http://localhost:8000/api/v1/superadmin/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "email": "newuser@example.com",
    "role": "tenant_user",
    "first_name": "Jane",
    "last_name": "Smith",
    "tenant_id": 1,
    "is_active": true,
    "notes": "New user for Acme Inc"
  }'
```

**Required Fields:**
- `email`: User email address
- `role`: User role (superadmin, analyst, tenant_admin, tenant_user)

**Optional Fields:**
- `first_name`: User's first name
- `last_name`: User's last name
- `tenant_id`: Tenant ID (required for tenant_admin and tenant_user roles)
- `is_active`: Whether user is active (default: true)
- `is_blocked`: Whether user is blocked (default: false)
- `notes`: Admin notes about the user

#### PUT /api/v1/superadmin/users/{user_id}
**Update user (superadmin only)**

```bash
curl -X PUT "http://localhost:8000/api/v1/superadmin/users/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "first_name": "John Updated",
    "role": "tenant_admin",
    "is_active": true,
    "notes": "Promoted to tenant admin"
  }'
```

#### POST /api/v1/superadmin/users/{user_id}/block
**Block a user (superadmin only)**

```bash
curl -X POST "http://localhost:8000/api/v1/superadmin/users/1/block" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '"User violated terms of service"'
```

**Response:**
```json
{
  "message": "User john@example.com has been blocked",
  "reason": "User violated terms of service"
}
```

#### POST /api/v1/superadmin/users/{user_id}/unblock
**Unblock a user (superadmin only)**

```bash
curl -X POST "http://localhost:8000/api/v1/superadmin/users/1/unblock" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '"User appeal approved"'
```

#### POST /api/v1/superadmin/users/{user_id}/reset-password
**Reset user password (superadmin only)**

```bash
curl -X POST "http://localhost:8000/api/v1/superadmin/users/1/reset-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '"newpassword123"'
```

#### GET /api/v1/superadmin/tenants
**List all tenants (superadmin and analyst only)**

```bash
curl -X GET "http://localhost:8000/api/v1/superadmin/tenants?search=acme" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "tenants": [
    {
      "id": 1,
      "company_name": "Acme Inc",
      "logo_url": "https://example.com/logo.png",
      "created_at": "2024-01-01T00:00:00Z",
      "users_count": 15,
      "products_count": 250
    }
  ],
  "total_count": 25,
  "skip": 0,
  "limit": 100
}
```

#### GET /api/v1/superadmin/tenants/{tenant_id}
**Get detailed tenant information**

```bash
curl -X GET "http://localhost:8000/api/v1/superadmin/tenants/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "company_name": "Acme Inc",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2024-01-01T00:00:00Z",
  "users": [
    {
      "id": 1,
      "email": "john@example.com",
      "full_name": "John Doe",
      "role": "tenant_admin",
      "is_active": true,
      "is_blocked": false,
      "last_login": "2024-01-15T09:30:00Z"
    }
  ],
  "products_count": 250,
  "users_count": 15
}
```

#### PUT /api/v1/superadmin/tenants/{tenant_id}
**Update tenant (superadmin only)**

```bash
curl -X PUT "http://localhost:8000/api/v1/superadmin/tenants/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "company_name": "Acme Corporation",
    "logo_url": "https://example.com/new-logo.png"
  }'
```

#### GET /api/v1/superadmin/products
**List all products (superadmin and analyst only)**

```bash
curl -X GET "http://localhost:8000/api/v1/superadmin/products?tenant_id=1&search=sony" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Query Parameters:**
- `tenant_id`: Filter by tenant ID
- `search`: Search in sku_id, manufacturer, supplier
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum number of records to return

**Response:**
```json
{
  "products": [
    {
      "id": 1,
      "sku_id": "SKU001",
      "tenant_id": 1,
      "tenant_name": "Acme Inc",
      "category_id": 1,
      "price": 299.99,
      "manufacturer": "Sony",
      "supplier": "Electronics Supplier",
      "image_url": "https://example.com/product.jpg",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T09:30:00Z"
    }
  ],
  "total_count": 1250,
  "skip": 0,
  "limit": 100
}
```

#### GET /api/v1/superadmin/audit-logs
**Get audit logs (superadmin and analyst only)**

```bash
curl -X GET "http://localhost:8000/api/v1/superadmin/audit-logs?user_id=1&action=create&resource_type=user&start_date=2024-01-01T00:00:00Z" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Query Parameters:**
- `user_id`: Filter by user ID
- `action`: Filter by action (create, read, update, delete, login, logout, block, unblock)
- `resource_type`: Filter by resource type (user, tenant, product, category)
- `start_date`: Filter by start date (ISO format)
- `end_date`: Filter by end date (ISO format)
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum number of records to return

**Response:**
```json
{
  "audit_logs": [
    {
      "id": 1234,
      "user_id": 1,
      "user_email": "admin@example.com",
      "action": "create",
      "resource_type": "user",
      "resource_id": 150,
      "resource_name": "newuser@example.com",
      "details": "Created user with role: tenant_user",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "metadata": {
        "total_count": 150,
        "skip": 0,
        "limit": 100
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 5000,
  "skip": 0,
  "limit": 100
}
```

### Audit Logging

The system automatically logs all user actions for audit purposes:

#### Logged Actions
- **User Management**: create, read, update, delete, block, unblock, reset_password
- **Tenant Management**: create, read, update, delete
- **Product Management**: create, read, update, delete
- **Authentication**: login, logout
- **System Access**: dashboard access, audit log access

#### Audit Log Fields
- **user_id**: ID of the user performing the action
- **action**: Type of action performed
- **resource_type**: Type of resource affected
- **resource_id**: ID of the affected resource
- **resource_name**: Name/identifier of the affected resource
- **details**: Additional details about the action
- **ip_address**: IP address of the user
- **user_agent**: User agent string
- **metadata**: Additional metadata as JSON
- **created_at**: Timestamp of the action

### Role Permissions

#### Superadmin
- ✅ **Full Access**: All data and functionality
- ✅ **User Management**: Create, read, update, delete, block, unblock users
- ✅ **Tenant Management**: View and update all tenants
- ✅ **Product Management**: View and manage all products
- ✅ **Audit Logs**: Full access to audit logs
- ✅ **System Administration**: Dashboard, statistics, system settings

#### Analyst
- ✅ **Read-Only Access**: View all data (no editing)
- ✅ **User Viewing**: View all users and their details
- ✅ **Tenant Viewing**: View all tenants and their details
- ✅ **Product Viewing**: View all products across tenants
- ✅ **Audit Logs**: View audit logs
- ✅ **Dashboard**: Access to dashboard statistics
- ❌ **No Editing**: Cannot modify any data

#### Tenant Admin
- ✅ **Tenant Management**: Full access to their own tenant
- ✅ **User Management**: Manage users within their tenant
- ✅ **Product Management**: Full access to products in their tenant
- ✅ **Category Management**: Manage categories in their tenant
- ❌ **Cross-Tenant Access**: Cannot access other tenants

#### Tenant User
- ✅ **Product Access**: View and manage products in their tenant
- ✅ **Category Access**: View categories in their tenant
- ✅ **Search**: Search within their tenant's data
- ❌ **User Management**: Cannot manage users
- ❌ **Tenant Management**: Cannot modify tenant settings