# 🚀 API Endpoints Documentation

## 📋 **Overview**

This document provides comprehensive API endpoint documentation for the Multi-Tenant PIM System. All endpoints require authentication via Bearer token unless specified otherwise.

**Base URL**: `http://localhost:8004/api/v1`

**Authentication**: `Authorization: Bearer <access_token>`

---

## 🔐 **Authentication Endpoints**

### **Hybrid Authentication System**
The system supports both local and Supabase authentication:

- **Local Authentication**: Superadmin users with local password hashing
- **Supabase Authentication**: Regular users with Supabase integration
- **Automatic User Sync**: Users from Supabase are automatically created in local database

### **Login Flow**
1. **Check Local Database**: First checks if user exists locally
2. **Supabase Authentication**: If not found locally, tries Supabase authentication
3. **Auto-Create User**: If Supabase authentication succeeds, creates user locally
4. **Return Token**: Provides access token for API access

### **POST** `/auth/signup`
**Create a new user account**

**Request Body:**
```json
{
  "email": "user@example.com",           // Required: Valid email address
  "password": "securepassword123",       // Required: Minimum 8 characters
  "company_name": "My Company Inc."      // Required: Company/tenant name
}
```

**Response (200):**
```json
{
  "msg": "Signup successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "1",
    "email": "user@example.com",
    "name": "user@example.com",
    "role": "tenant_user",
    "isSetupComplete": true,
    "companyId": "1",
    "first_name": null,
    "last_name": null,
    "is_active": true,
    "is_blocked": false,
    "tenant_id": 1,
    "tenant": {
      "id": 1,
      "company_name": "My Company Inc.",
      "logo_url": null
    }
  }
}
```

### **POST** `/auth/login`
**Login with email and password**

**Supports both local and Supabase users automatically.**

**Request Body:**
```json
{
  "email": "user@example.com",           // Required: Valid email address
  "password": "securepassword123"        // Required: User password
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "1",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "tenant_user",
    "isSetupComplete": true,
    "companyId": "1",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_blocked": false,
    "tenant_id": 1,
    "tenant": {
      "id": 1,
      "company_name": "My Company Inc.",
      "logo_url": "https://example.com/logo.png"
    }
  }
}
```

**Special Cases:**
- **Supabase Users**: If user exists in Supabase but not locally, they are automatically created in local database
- **Default Tenant**: New Supabase users get assigned to "Default Company" tenant
- **Backward Compatibility**: Existing local users continue to work as before

### **GET** `/auth/me`
**Get current user details**

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "tenant_user",
  "tenant": {
    "id": 1,
    "company_name": "My Company Inc.",
    "logo_url": "https://example.com/logo.png",
    "created_at": "2024-01-01T00:00:00"
  },
  "is_system_user": false
}
```

### **POST** `/auth/logout`
**Logout user (client-side token removal)**

**Response (200):**
```json
{
  "msg": "Logout successful"
}
```

### **GET** `/auth/providers`
**Get available social login providers**

**Response (200):**
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

---

## 🏢 **Tenant Management**

### **GET** `/tenant/me`
**Get current user's tenant details**

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "company_name": "My Company Inc.",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2024-01-01T00:00:00",
  "is_system_user": false
}
```

### **POST** `/tenant`
**Create a new tenant (admin only)**

**Request Body:**
```json
{
  "company_name": "New Company Inc.",    // Required: Company name
  "logo_url": "https://example.com/logo.png"  // Optional: Logo URL
}
```

**Response (200):**
```json
{
  "id": 2,
  "company_name": "New Company Inc.",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2024-01-01T00:00:00"
}
```

### **PATCH** `/tenant/{id}`
**Update tenant details**

**Request Body:**
```json
{
  "company_name": "Updated Company Name",  // Optional: New company name
  "logo_url": "https://new-logo.com/logo.png"  // Optional: New logo URL
}
```

---

## 👥 **User Management**

### **GET** `/users`
**List all users in current tenant**

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "role": "tenant_user",
    "tenant_id": 1
  },
  {
    "id": 2,
    "email": "admin@example.com",
    "role": "tenant_admin",
    "tenant_id": 1
  }
]
```

### **GET** `/users/{id}`
**Get user details by ID**

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "tenant_user",
  "tenant": {
    "id": 1,
    "company_name": "My Company Inc.",
    "logo_url": "https://example.com/logo.png",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### **PATCH** `/users/{id}/role`
**Update user role (admin only)**

**Request Body:**
```json
{
  "role": "tenant_admin"  // Required: "admin", "editor", "viewer"
}
```

---

## 📦 **Product Management**

### **GET** `/products`
**List products with filters**

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100)
- `category_id` (int, optional): Filter by category ID
- `search` (string, optional): General search term
- `primary_only` (bool, optional): Only primary fields
- `secondary_only` (bool, optional): Only secondary fields
- `field_type` (string, optional): "primary", "secondary", "all"
- `sku_id` (string, optional): Search in SKU ID (comma-separated)
- `price` (float, optional): Exact price search
- `price_min` (float, optional): Minimum price
- `price_max` (float, optional): Maximum price
- `manufacturer` (string, optional): Search manufacturer (comma-separated)
- `supplier` (string, optional): Search supplier (comma-separated)
- `brand` (string, optional): Search brand (comma-separated)
- `field_name` (string, optional): Search specific field
- `field_value` (string, optional): Search field value (comma-separated)

**Response (200):**
```json
{
  "products": [
    {
      "id": 1,
      "sku_id": "SKU001",
      "name": "Product Name",
      "price": 299.99,
      "manufacturer": "Sony",
      "supplier": "Electronics Supplier",
      "image_url": "https://example.com/image.jpg",
      "category_id": 1,
      "additional_data": [
        {
          "field_name": "color",
          "field_label": "Color",
          "field_value": "Black",
          "field_type": "string",
          "is_searchable": true,
          "is_editable": true,
          "is_primary": false,
          "is_secondary": true
        }
      ],
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 100
}
```

### **GET** `/products/{id}`
**Get specific product details**

**Response (200):**
```json
{
  "id": 1,
  "sku_id": "SKU001",
  "name": "Product Name",
  "price": 299.99,
  "manufacturer": "Sony",
  "supplier": "Electronics Supplier",
  "image_url": "https://example.com/image.jpg",
  "category_id": 1,
  "category": {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic devices"
  },
  "additional_data": [...],
  "field_configurations": [...],
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### **POST** `/products`
**Create a new product**

**Request Body:**
```json
{
  "sku_id": "SKU001",                    // Required: Unique SKU
  "name": "Product Name",                // Required: Product name
  "price": 299.99,                       // Required: Product price
  "manufacturer": "Sony",                // Optional: Manufacturer
  "supplier": "Electronics Supplier",    // Optional: Supplier
  "image_url": "https://example.com/image.jpg",  // Optional: Image URL
  "category_id": 1,                      // Optional: Category ID
  "additional_data": [                   // Optional: Additional fields
    {
      "field_name": "color",
      "field_label": "Color",
      "field_value": "Black",
      "field_type": "string"
    }
  ]
}
```

### **PUT** `/products/{id}`
**Update product**

**Request Body:** Same as POST but all fields optional

### **DELETE** `/products/{id}`
**Delete product**

**Response (200):**
```json
{
  "msg": "Product deleted successfully"
}
```

### **POST** `/products/upload/analyze`
**Analyze product file (AI-powered)**

**Request:** `multipart/form-data`
- `file` (file, required): CSV/Excel file

**Response (200):**
```json
{
  "analysis": {
    "total_rows": 100,
    "detected_fields": ["sku_id", "name", "price", "manufacturer"],
    "field_mappings": {...},
    "data_preview": [...],
    "recommendations": [...]
  }
}
```

### **POST** `/products/upload`
**Upload and save products**

**Request:** `multipart/form-data`
- `file` (file, required): CSV/Excel file

**Response (200):**
```json
{
  "msg": "Successfully uploaded 100 products",
  "products": [...]
}
```

---

## 🔍 **Search & Filters**

### **GET** `/products/search`
**Search products with advanced filters**

**Query Parameters:**
- `q` (string, optional): General search query
- `skip` (int, optional): Records to skip
- `limit` (int, optional): Records to return
- `category_id` (int, optional): Category filter
- `sku_id` (string, optional): SKU search (comma-separated)
- `price` (float, optional): Exact price
- `price_min` (float, optional): Min price
- `price_max` (float, optional): Max price
- `manufacturer` (string, optional): Manufacturer search (comma-separated)
- `supplier` (string, optional): Supplier search (comma-separated)
- `brand` (string, optional): Brand search (comma-separated)
- `field_name` (string, optional): Specific field search
- `field_value` (string, optional): Field value search (comma-separated)
- `field_type` (string, optional): Filter by field type (primary, secondary, all)

**Response (200):**
```json
{
  "products": [...],
  "total_count": 50,
  "skip": 0,
  "limit": 100,
  "query": "search term",
  "searchable_fields": ["manufacturer", "supplier", "brand"],
  "field_filters": {
    "price_min": 0,
    "price_max": 1000
  }
}
```

### **GET** `/products/filters/unique-data`
**Get unique filter data**

**Query Parameters:**
- `field_name` (string, optional): Specific field name

**Response (200):**
```json
{
  "field_name": "manufacturer",
  "unique_values": ["Sony", "Apple", "Samsung"],
  "counts": {
    "Sony": 25,
    "Apple": 30,
    "Samsung": 15
  }
}
```

### **GET** `/products/filters`
**Get all available filters for search functionality**

**Description:** Main filters endpoint that returns all unique filter data for building search interfaces and dropdowns.

**Response (200):**
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

### **GET** `/products/filters/brands`
**Get unique brands**

**Response (200):**
```json
{
  "brands": ["Sony", "Apple", "Samsung"],
  "counts": {
    "Sony": 25,
    "Apple": 30,
    "Samsung": 15
  }
}
```

### **GET** `/products/filters/manufacturers`
**Get unique manufacturers**

### **GET** `/products/filters/suppliers`
**Get unique suppliers**

### **GET** `/products/filters/categories`
**Get unique categories**

### **GET** `/products/filters/price-range`
**Get price range**

**Response (200):**
```json
{
  "min_price": 10.00,
  "max_price": 999.99,
  "price_ranges": [
    {"range": "0-50", "count": 25},
    {"range": "51-100", "count": 30},
    {"range": "101-500", "count": 20}
  ]
}
```

### **GET** `/products/filters/all`
**Get all filter data**

**Response (200):**
```json
{
  "brands": [...],
  "manufacturers": [...],
  "suppliers": [...],
  "categories": [...],
  "price_range": {...}
}
```

---

## ⚙️ **Field Configuration**

### **GET** `/products/fields/configuration`
**Get field configurations**

**Response (200):**
```json
{
  "fields": [
    {
      "field_name": "sku_id",
      "field_label": "SKU ID",
      "field_type": "string",
      "is_searchable": true,
      "is_editable": true,
      "is_primary": true,
      "is_secondary": false,
      "display_order": 1,
      "description": "Unique product identifier"
    }
  ]
}
```

### **POST** `/products/fields/configuration`
**Set field configurations**

**Request Body:**
```json
[
  {
    "field_name": "sku_id",              // Required: Field name
    "field_label": "SKU ID",             // Required: Display label
    "field_type": "string",              // Required: Field type
    "is_searchable": true,               // Optional: Searchable flag
    "is_editable": true,                 // Optional: Editable flag
    "is_primary": true,                  // Optional: Primary flag
    "is_secondary": false,               // Optional: Secondary flag
    "display_order": 1,                  // Optional: Display order
    "description": "Unique identifier"   // Optional: Field description
  }
]
```

### **PUT** `/products/fields/configuration/{field_name}`
**Update specific field configuration**

**Request Body:**
```json
{
  "field_label": "Updated SKU ID",
  "is_searchable": false,
  "is_editable": true,
  "is_primary": true,
  "is_secondary": false,
  "display_order": 2,
  "description": "Updated description"
}
```

---

## 📂 **Category Management**

### **GET** `/categories`
**List categories**

**Query Parameters:**
- `skip` (int, optional): Records to skip
- `limit` (int, optional): Records to return
- `search` (string, optional): Search term

**Response (200):**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "description": "Electronic devices",
      "schema_json": {}
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 100
}
```

### **POST** `/categories`
**Create category**

**Request Body:**
```json
{
  "name": "Electronics",                 // Required: Category name
  "description": "Electronic devices",   // Optional: Description
  "schema_json": {}                      // Optional: JSON schema
}
```

### **GET** `/categories/{id}`
**Get category details**

### **PUT** `/categories/{id}`
**Update category**

### **DELETE** `/categories/{id}`
**Delete category**

---

## 📊 **Progress & Onboarding**

### **GET** `/progress/overview`
**Get progress overview**

**Response (200):**
```json
{
  "tenant_id": 1,
  "total_steps": 5,
  "completed_steps": 3,
  "progress_percentage": 60,
  "steps": [
    {
      "step_key": "company_info",
      "title": "Company Info",
      "description": "Basic information",
      "is_completed": true,
      "order": 1,
      "category": "setup",
      "icon": "🏢"
    },
    {
      "step_key": "csv_upload",
      "title": "CSV Upload & Validation",
      "description": "Product data",
      "is_completed": true,
      "order": 2,
      "category": "data",
      "icon": "📊"
    },
    {
      "step_key": "field_setup",
      "title": "Field Setup",
      "description": "Configure fields",
      "is_completed": false,
      "order": 3,
      "category": "configuration",
      "icon": "⚙️"
    },
    {
      "step_key": "preview",
      "title": "Preview",
      "description": "Sample SKU",
      "is_completed": false,
      "order": 4,
      "category": "review",
      "icon": "👁️"
    },
    {
      "step_key": "complete",
      "title": "Complete",
      "description": "Finish setup",
      "is_completed": false,
      "order": 5,
      "category": "completion",
      "icon": "✅"
    }
  ],
  "is_system_user": false
}
```

### **GET** `/progress/steps`
**Get all onboarding steps**

### **POST** `/progress/steps/{step_key}/complete`
**Complete a step**

**Request Body:**
```json
{
  "company_name": "My Company",          // For company_info step
  "logo_url": "https://example.com/logo.png"  // Optional
}
```

---

## 👑 **Superadmin Endpoints**

### **GET** `/superadmin/dashboard`
**Get superadmin dashboard**

**Response (200):**
```json
{
  "statistics": {
    "total_users": 150,
    "total_tenants": 25,
    "total_products": 5000,
    "total_categories": 100
  },
  "recent_activity": [...],
  "system_health": {
    "status": "healthy",
    "uptime": "99.9%"
  }
}
```

### **GET** `/superadmin/users`
**List all users**

**Query Parameters:**
- `skip` (int, optional): Records to skip
- `limit` (int, optional): Records to return
- `role` (string, optional): Filter by role
- `tenant_id` (int, optional): Filter by tenant
- `is_active` (bool, optional): Filter by active status
- `is_blocked` (bool, optional): Filter by blocked status
- `search` (string, optional): Search term

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "tenant_user",
      "tenant_id": 1,
      "is_active": true,
      "is_blocked": false,
      "last_login": "2024-01-01T00:00:00",
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total_count": 150,
  "skip": 0,
  "limit": 100
}
```

### **POST** `/superadmin/users`
**Create user**

**Request Body:**
```json
{
  "email": "newuser@example.com",        // Required: Email
  "password": "securepassword123",       // Required: Password
  "first_name": "John",                  // Optional: First name
  "last_name": "Doe",                    // Optional: Last name
  "role": "tenant_user",                 // Required: Role
  "tenant_id": 1,                        // Optional: Tenant ID
  "is_active": true,                     // Optional: Active status
  "notes": "User notes"                  // Optional: Admin notes
}
```

### **PUT** `/superadmin/users/{id}`
**Update user**

### **POST** `/superadmin/users/{id}/block`
**Block user**

**Request Body:**
```json
{
  "reason": "Violation of terms"         // Required: Block reason
}
```

### **POST** `/superadmin/users/{id}/unblock`
**Unblock user**

### **POST** `/superadmin/users/{id}/reset-password`
**Reset user password**

**Request Body:**
```json
{
  "new_password": "newsecurepassword123"  // Required: New password
}
```

### **GET** `/superadmin/tenants`
**List all tenants**

### **GET** `/superadmin/tenants/{id}`
**Get tenant details**

### **PUT** `/superadmin/tenants/{id}`
**Update tenant**

### **GET** `/superadmin/products`
**List all products**

### **GET** `/superadmin/audit-logs`
**Get audit logs**

**Query Parameters:**
- `skip` (int, optional): Records to skip
- `limit` (int, optional): Records to return
- `user_id` (int, optional): Filter by user
- `action` (string, optional): Filter by action
- `resource_type` (string, optional): Filter by resource type
- `start_date` (string, optional): Start date filter
- `end_date` (string, optional): End date filter

---

## 🎯 **Error Responses**

### **400 Bad Request**
```json
{
  "detail": "Invalid request data"
}
```

### **401 Unauthorized**
```json
{
  "detail": "Could not validate credentials"
}
```

### **403 Forbidden**
```json
{
  "detail": "Access denied"
}
```

### **404 Not Found**
```json
{
  "detail": "Resource not found"
}
```

### **500 Internal Server Error**
```json
{
  "detail": "Internal server error"
}
```

---

## 📝 **Notes**

1. **Authentication**: All endpoints require Bearer token authentication except `/auth/signup` and `/auth/login`
2. **Pagination**: Use `skip` and `limit` parameters for paginated responses
3. **Search**: Most endpoints support search functionality
4. **Filtering**: Use query parameters for filtering data
5. **File Uploads**: Use `multipart/form-data` for file uploads
6. **Comma-separated Values**: Multiple values can be passed as comma-separated strings
7. **Field Configuration**: Dynamic field configuration is supported for products
8. **Superadmin Access**: Superadmin endpoints require superadmin role
9. **Tenant Isolation**: Regular users can only access their own tenant data
10. **Audit Logging**: All superadmin actions are logged for audit purposes

---

## 🚀 **Quick Start**

1. **Signup/Login**: Use `/auth/signup` or `/auth/login` to get access token
2. **Set Authorization Header**: Include `Authorization: Bearer <token>` in all requests
3. **Explore Endpoints**: Start with `/auth/me` to get user details
4. **Upload Data**: Use upload endpoints for bulk data import
5. **Configure Fields**: Set up field configurations for search and display
6. **Search & Filter**: Use search endpoints for data discovery

---

**✅ Ready for UI Development!** 