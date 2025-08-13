# 🚀 API Endpoints Documentation

## 📋 **Overview**

This document provides comprehensive API endpoint documentation for the Multi-Tenant PIM System. All endpoints require authentication via Bearer token unless specified otherwise.

**Base URL**: `http://localhost:8000/api/v1` (Development) / `http://your-domain:8004/api/v1` (Production)

**Authentication**: `Authorization: Bearer <access_token>`

---

## 📄 **Pagination System**

### **Standard Pagination Parameters**
All list endpoints now support comprehensive pagination with the following parameters:

- **`page`**: Page number (starts from 1, default: 1)
- **`page_size`**: Number of items per page (configurable limits, default: 100)

### **Pagination Response Format**
All paginated endpoints return a standardized response structure:

```json
{
  "data": [...],  // Array of items for the current page
  "pagination": {
    "page": 1,                    // Current page number
    "page_size": 100,             // Items per page
    "total_pages": 5,             // Total number of pages
    "total_items": 450,           // Total count of all items
    "has_next": true,             // Whether next page exists
    "has_previous": false,        // Whether previous page exists
    "next_page": 2,               // Next page number (null if no next page)
    "previous_page": null         // Previous page number (null if no previous page)
  },
  "total_count": 450              // Total count (for backward compatibility)
}
```

### **Backward Compatibility**
For existing integrations, the old `skip` and `limit` parameters are still supported but deprecated:
- **`skip`**: Number of records to skip (deprecated, use `page` and `page_size`)
- **`limit`**: Maximum number of records to return (deprecated, use `page_size`)

### **Page Size Limits**
Different endpoints have different maximum page size limits:
- **Products**: Max 500 items per page
- **Users**: Max 500 items per page  
- **Tenants**: Max 500 items per page
- **Audit Logs**: Max 1000 items per page
- **Superadmin Users**: Max 1000 items per page

### **Example Usage**
```bash
# Get first page with 50 items
GET /api/v1/products?page=1&page_size=50

# Get second page with 25 items
GET /api/v1/products?page=2&page_size=25

# Get third page with 100 items (default page_size)
GET /api/v1/products?page=3
```

---

## 🔐 **Authentication Endpoints**

### **JWT-Based Authentication System**
The system uses a custom JWT (JSON Web Token) authentication system:

- **Local Database**: All user data stored in SQLite database
- **JWT Tokens**: Secure access tokens with configurable expiration
- **Password Hashing**: Bcrypt-based password security
- **Role-Based Access**: Superadmin, tenant_admin, and analyst roles

### **Authentication Flow**
1. **User Registration**: Creates account with email/password
2. **User Login**: Validates credentials and returns JWT token
3. **Token Usage**: Include token in Authorization header for protected endpoints
4. **Token Refresh**: Use refresh endpoint to get new tokens

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
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "2",
    "email": "user@example.com",
    "name": "User",
    "role": "tenant_admin",
    "isSetupComplete": true,
    "companyId": "1",
    "first_name": "",
    "last_name": "",
    "is_active": true,
    "is_blocked": false,
    "tenant_id": 1,
    "tenant": {
      "id": "1",
      "name": "My Company Inc.",
      "is_active": true
    }
  }
}
```

**Error Responses:**
- **400**: Email already registered
- **500**: Failed to create user

### **POST** `/auth/login`
**Login with email and password**

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
    "id": "2",
    "email": "user@example.com",
    "name": "User",
    "role": "tenant_admin",
    "isSetupComplete": true,
    "companyId": "1",
    "first_name": "",
    "last_name": "",
    "is_active": true,
    "is_blocked": false,
    "tenant_id": 1,
    "tenant": {
      "id": "1",
      "name": "My Company Inc.",
      "is_active": true
    }
  }
}
```

**Error Responses:**
- **401**: Invalid login credentials
- **403**: User account deactivated or blocked
- **500**: Login failed

### **GET** `/auth/me`
**Get current user details**

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 2,
  "email": "user@example.com",
  "name": "User",
  "role": "tenant_admin",
  "isSetupComplete": true,
  "companyId": "1",
  "first_name": "",
  "last_name": "",
  "is_active": true,
  "is_blocked": false,
  "tenant_id": 1,
  "tenant": {
    "id": "1",
    "name": "My Company Inc.",
    "is_active": true
  }
}
```

**Special Cases:**
- **Superadmin Users**: No tenant association, `companyId` is empty string
- **Analyst Users**: No tenant association, `companyId` is empty string
- **Tenant Users**: Full tenant information included

### **POST** `/auth/logout`
**Logout user (client-side token removal)**

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

**Note**: This endpoint doesn't invalidate the token server-side. The client should remove the token from storage.

### **POST** `/auth/refresh`
**Refresh access token**

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

**Note**: Use this endpoint to get a new token before the current one expires.

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
  "logo_url": null,
  "created_at": "2024-01-01T00:00:00"
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

### **GET** `/tenants`
**List all tenants with pagination (superadmin and analyst only)**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page`: Page number (starts from 1, default: 1)
- `page_size`: Number of items per page (max 500, default: 100)

**Response (200):**
```json
{
  "tenants": [
    {
      "id": 1,
      "company_name": "Company A Inc.",
      "logo_url": "https://example.com/logo1.png",
      "created_at": "2024-01-01T00:00:00"
    },
    {
      "id": 2,
      "company_name": "Company B Inc.",
      "logo_url": null,
      "created_at": "2024-01-02T00:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_pages": 1,
    "total_items": 2,
    "has_next": false,
    "has_previous": false,
    "next_page": null,
    "previous_page": null
  },
  "total_count": 2
}
```

---

## 👥 **User Management**

### **GET** `/user/me`
**Get current user profile**

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 2,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "tenant_admin",
  "is_active": true,
  "is_blocked": false,
  "tenant_id": 1
}
```

### **POST** `/user/change-password`
**Change current user's own password**

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "current_password": "oldpassword123",  // Required: Current password
  "new_password": "newpassword123"       // Required: New password (min 8 chars)
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully",
  "user_id": 2,
  "email": "user@example.com"
}
```

### **POST** `/user/{id}/change-password`
**Change any user's password (Superadmin only)**

**Headers:** `Authorization: Bearer <token>` (Superadmin required)

**Request Body:**
```json
{
  "new_password": "newpassword123"       // Required: New password (min 8 chars)
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully for user user@example.com",
  "user_id": 2,
  "email": "user@example.com",
  "changed_by": "admin@pim.com"
}
```

### **PUT** `/user/me`
**Update current user profile**

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "first_name": "John",                  // Optional: First name
  "last_name": "Doe",                    // Optional: Last name
  "password": "newpassword123"           // Optional: New password
}
```

**Response (200):**
```json
{
  "id": 2,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "tenant_admin",
  "is_active": true,
  "is_blocked": false,
  "tenant_id": 1
}
```

### **GET** `/users`
**List all users in current tenant with pagination**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page`: Page number (starts from 1, default: 1)
- `page_size`: Number of items per page (max 500, default: 100)

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "email": "user1@example.com",
      "role": "tenant_admin",
      "tenant_id": 1
    },
    {
      "id": 2,
      "email": "user2@example.com",
      "role": "tenant_user",
      "tenant_id": 1
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_pages": 1,
    "total_items": 2,
    "has_next": false,
    "has_previous": false,
    "next_page": null,
    "previous_page": null
  },
  "total_count": 2
}
```

**Note:** Superadmin and analyst users can see all users across all tenants.

---

## 🔍 **Search Endpoints**

### **GET** `/search`
**Search across products, categories, and users**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `q`: Search query string (required)
- `type`: Search type - "products", "categories", "users", or "all" (default: "all")
- `limit`: Maximum results (default: 20)

**Response (200):**
```json
{
  "query": "laptop",
  "results": {
    "products": [
      {
        "id": 1,
        "name": "Gaming Laptop",
        "description": "High-performance gaming laptop",
        "category": "Electronics"
      }
    ],
    "categories": [],
    "users": []
  }
}
```

---

## 📊 **Product Management**

### **GET** `/products`
**Get all products for current tenant with pagination**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page`: Page number (starts from 1, default: 1)
- `page_size`: Number of items per page (max 500, default: 100)
- `skip`: Number of items to skip (deprecated, use page and page_size)
- `limit`: Maximum items to return (deprecated, use page_size)
- `category_id`: Filter by category ID (optional)
- `search`: General search term (optional)
- `field_type`: Filter by field type - "primary", "secondary", "all" (optional)
- `sku_id`: Search in SKU ID field (comma-separated values supported)
- `price`: Search by exact price
- `price_min`: Minimum price filter
- `price_max`: Maximum price filter
- `manufacturer`: Search in manufacturer field (comma-separated values supported)
- `supplier`: Search in supplier field (comma-separated values supported)
- `brand`: Search in brand field (comma-separated values supported)
- `field_name`: Search in specific additional data field
- `field_value`: Value to search for in the specified field

**Response (200):**
```json
{
  "products": [
    {
      "id": 1,
      "sku_id": "SKU001",
      "category_id": 1,
      "price": 99.99,
      "manufacturer": "Brand Name",
      "supplier": "Supplier Name",
      "image_url": "https://example.com/image.jpg",
      "additional_data_count": 5
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_pages": 5,
    "total_items": 450,
    "has_next": true,
    "has_previous": false,
    "next_page": 2,
    "previous_page": null
  },
  "total_count": 450,
  "skip": 0,
  "limit": 100,
  "field_type": "all"
}
```

### **POST** `/product`
**Create a new product**

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Product Name",                // Required: Product name
  "description": "Product description",   // Optional: Description
  "price": 99.99,                       // Required: Price
  "category_id": 1                      // Required: Category ID
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Product Name",
  "description": "Product description",
  "price": 99.99,
  "category_id": 1,
  "tenant_id": 1
}
```

---

## 📁 **Category Management**

### **GET** `/category`
**Get all categories for current tenant**

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic devices and accessories",
    "tenant_id": 1
  }
]
```

### **POST** `/category`
**Create a new category**

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Electronics",                 // Required: Category name
  "description": "Electronic devices"    // Optional: Description
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Electronics",
  "description": "Electronic devices",
  "tenant_id": 1
}
```

---

## 🤖 **AI Chat Endpoints**

### **POST** `/chat`
**Send a message to AI chat**

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "message": "What products do you have?",  // Required: User message
  "context": "product_inquiry"              // Optional: Context for AI
}
```

**Response (200):**
```json
{
  "response": "I can help you find products. We have various categories including electronics, clothing, and home goods.",
  "context": "product_inquiry",
  "timestamp": "2024-01-01T00:00:00"
}
```

---

## 📈 **Progress Tracking**

### **GET** `/progress`
**Get user progress and analytics**

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "user_id": 2,
  "total_products": 25,
  "total_categories": 5,
  "completion_rate": 85.5,
  "last_activity": "2024-01-01T00:00:00"
}
```

---

## 🔧 **System Administration**

### **GET** `/superadmin/users`
**Get all users with pagination (superadmin and analyst only)**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page`: Page number (starts from 1, default: 1)
- `page_size`: Number of items per page (max 1000, default: 100)
- `skip`: Number of records to skip (deprecated, use page and page_size)
- `limit`: Maximum number of records to return (deprecated, use page_size)
- `role`: Filter by user role (optional)
- `tenant_id`: Filter by tenant ID (optional)
- `is_active`: Filter by active status (optional)
- `is_blocked`: Filter by blocked status (optional)
- `search`: Search in email, first_name, last_name (optional)

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "email": "admin@pim.com",
      "first_name": "Admin",
      "last_name": "User",
      "role": "superadmin",
      "tenant_id": null,
      "is_active": true,
      "is_blocked": false,
      "created_at": "2024-01-01T00:00:00",
      "last_login": "2024-01-01T10:00:00",
      "audit_logs_count": 15
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_pages": 1,
    "total_items": 1,
    "has_next": false,
    "has_previous": false,
    "next_page": null,
    "previous_page": null
  },
  "total_count": 1,
  "skip": 0,
  "limit": 100
}
```

### **POST** `/superadmin/users`
**Create a new user (superadmin only)**

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "email": "analyst@pim.com",            // Required: Email address
  "password": "securepass123",           // Required: Password
  "role": "analyst",                     // Required: Role (analyst, tenant_admin)
  "tenant_id": 1                         // Optional: Tenant ID for tenant users
}
```

**Response (200):**
```json
{
  "id": 3,
  "email": "analyst@pim.com",
  "role": "analyst",
  "is_active": true,
  "tenant_id": null
}
```

### **GET** `/superadmin/audit-logs`
**Get audit logs with pagination (superadmin and analyst only)**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page`: Page number (starts from 1, default: 1)
- `page_size`: Number of items per page (max 1000, default: 100)
- `skip`: Number of records to skip (deprecated, use page and page_size)
- `limit`: Maximum number of records to return (deprecated, use page_size)
- `user_id`: Filter by user ID (optional)
- `action`: Filter by action type (optional)
- `resource_type`: Filter by resource type (optional)
- `start_date`: Filter by start date (ISO format, optional)
- `end_date`: Filter by end date (ISO format, optional)

**Response (200):**
```json
{
  "audit_logs": [
    {
      "id": 1,
      "user_id": 1,
      "user_email": "admin@pim.com",
      "action": "login",
      "resource_type": "auth",
      "resource_id": null,
      "resource_name": null,
      "details": "User logged in successfully",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "metadata": {"login_method": "password"},
      "created_at": "2024-01-01T10:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_pages": 5,
    "total_items": 450,
    "has_next": true,
    "has_previous": false,
    "next_page": 2,
    "previous_page": null
  },
  "total_count": 450,
  "skip": 0,
  "limit": 100
}
```

---

## 🚀 **Deployment Information**

### **Production Setup**
1. **Database**: SQLite database located at `data/pim.db`
2. **Port**: Application runs on port 8004 in production
3. **Admin User**: Default admin@pim.com / admin123 (change after first login)
4. **Environment**: Use `./full-deploy.sh` for production deployment

### **Development Setup**
1. **Database**: Use `./setup_dev_db.sh` for quick development setup
2. **Port**: Application runs on port 8000 in development
3. **Hot Reload**: Enabled with `--reload` flag

### **Environment Variables**
```bash
# Required
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional (for production)
DATABASE_URL=sqlite:///./data/pim.db
```

---

## 📝 **Error Handling**

### **Standard Error Response Format**
```
```