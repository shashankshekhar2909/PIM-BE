# Multi-Tenant Product Information Management (PIM) System Backend

This is a FastAPI backend for a scalable, multi-tenant Product Information Management (PIM) system, using SQLite for development and Supabase for authentication. It supports modular, extensible APIs for user, tenant, category, product, and search management.

## Features
- Multi-tenant onboarding & isolation
- Category & schema management
- Dynamic attribute configuration
- Product CRUD operations
- CSV/XLSX bulk upload and edit
- Typesense-powered search (stub)
- LLM-powered product assistant (stub)
- Asset/media management (stub)
- Role-based access control
- Audit trail and versioning (stub)
- **Supabase Authentication** with social login support

## 🚀 AI-Enhanced Product Upload

The PIM system now features **AI-powered product upload** with the following capabilities:

### Key Features

- 🤖 **AI-Powered Analysis**: Automatic file type detection and field normalization using Google Gemini AI
- 📊 **Data Validation**: Comprehensive data quality assessment and validation
- 🗂️ **Field Mapping**: Automatic field name normalization and type inference
- 📏 **Product Limits**: Maximum 500 products per upload (enforced)
- 🔄 **Additional Data**: Automatic handling of extra fields in separate table
- ✅ **Error Handling**: Detailed error reporting and validation status
- ⚙️ **Field Configuration**: Manage which fields are searchable, editable, primary, secondary, and have search indexes

### API Endpoints

#### POST `/api/v1/products/upload/analyze`
**Analyze and load product data for editing (NO database save)**

- Uploads CSV/Excel file
- AI-powered analysis and field normalization
- Returns formatted data for editing
- Enforces 500 product limit
- Includes validation results and field mappings
- **Does NOT save anything to database** - purely for analysis and editing

#### POST `/api/v1/products/upload`
**Upload and save products directly to database**

- Uploads CSV/Excel file
- AI-powered analysis and processing
- Direct saving to database
- Enforces 500 product limit
- Returns created products with additional data count
- **Saves data to database immediately**

### Field Configuration

The system provides comprehensive field configuration management to control how fields are used in your catalog. **Field configurations are real-time data-driven** - only fields that actually exist in the tenant's product data are shown and can be configured.

#### GET `/api/v1/products/fields/configuration`
**Get all field configurations for the current tenant (real-time data only)**

- Returns only fields that exist in the tenant's product data
- Includes searchable, editable, primary, secondary options
- Automatically discovers new fields when products are uploaded
- Real-time updates based on actual data

#### POST `/api/v1/products/fields/configuration`
**Set field configurations for the current tenant (real-time data only)**

- Set multiple field configurations at once
- Only allows configuration of fields that exist in the data
- Configure searchable, editable, primary, secondary options
- Set display order and descriptions

#### PUT `/api/v1/products/fields/configuration/{field_name}`
**Update a specific field configuration (real-time data only)**

- Update individual field configuration settings
- Only allows updating fields that exist in the data
- Modify searchable, editable, primary, secondary options

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

### Field Configuration Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `is_searchable` | boolean | Can this field be searched? (implies search index) | false |
| `is_editable` | boolean | Can this field be edited? | true |
| `is_primary` | boolean | Is this a primary field (e.g., sku_id)? | false |
| `is_secondary` | boolean | Is this a secondary field (e.g., price, manufacturer)? | false |
| `display_order` | integer | Order for displaying fields in UI | 0 |
| `description` | string | Human-readable description of the field | "" |

### Search and Filtering Features

The system now supports advanced search and filtering based on field configurations:

#### Search in Searchable Fields Only
```bash
# Search only in fields marked as searchable
curl -X GET "http://localhost:8000/api/v1/products?search=sony" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Filter by Field Type
```bash
# Return only products with primary fields
curl -X GET "http://localhost:8000/api/v1/products?field_type=primary" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Return only products with secondary fields
curl -X GET "http://localhost:8000/api/v1/products?field_type=secondary" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Return all products (default)
curl -X GET "http://localhost:8000/api/v1/products?field_type=all" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Combined Search and Filtering
```bash
# Search in searchable fields and filter by primary fields
curl -X GET "http://localhost:8000/api/v1/products?search=sony&field_type=primary" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search in searchable fields and filter by secondary fields
curl -X GET "http://localhost:8000/api/v1/products?search=sony&field_type=secondary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Editable Field Validation

When updating products, only fields marked as `is_editable: true` can be modified. The system will return an error if you try to update non-editable fields.

### Example Usage

```bash
# Step 1: Analyze and load for editing (no database save)
curl -X POST "http://localhost:8000/api/v1/products/upload/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@products.csv"

# Step 2: Upload and save directly to database
curl -X POST "http://localhost:8000/api/v1/products/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@products.csv"
```

### Workflow

1. **Analyze Step** (`/upload/analyze`): 
   - Upload file for analysis
   - AI processes and validates data
   - Returns data for editing/review
   - No database changes

2. **Save Step** (`/upload`):
   - Upload file for immediate processing
   - AI analyzes and saves to database
   - Returns created products
   - Database is updated

### Supported File Formats

- CSV files (`.csv`)
- Excel files (`.xlsx`, `.xls`)

### Data Requirements

**Required Fields:**
- `sku_id` - Unique product identifier

**Optional Fields:**
- `category_id` - Product category
- `price` - Product price
- `manufacturer` - Product manufacturer
- `supplier` - Product supplier
- `image_url` - Product image URL
- Any additional fields (handled automatically by AI)

## Setup

### 1. Environment Configuration

Create a `.env` file in the project root with the following variables:

```bash
# Supabase Configuration
SUPABASE_URL=https://hhxuxthwvpeplhtprnhf.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Existing Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./pim.db
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Supabase Setup

1. **Get Supabase Credentials**
   - Go to your Supabase dashboard: https://app.supabase.com
   - Select your project: `https://hhxuxthwvpeplhtprnhf.supabase.co`
   - Navigate to Settings > API
   - Copy the "anon/public" key and "service_role" key

2. **Configure Authentication**
   - Go to Authentication > Settings
   - Enable email authentication
   - Configure social providers (Google, GitHub, Facebook) if needed

3. **Test Authentication**
   - Use the `/api/v1/auth/signup` endpoint to create a new user
   - Use the `/api/v1/auth/login` endpoint to authenticate
   - Check `/api/v1/auth/providers` for available social login options

## Project Structure
- `app/` - Main application code
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation
- `SUPABASE_SETUP.md` - Detailed Supabase setup guide 