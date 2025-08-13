# 🚀 API Endpoints Documentation

## 📋 **Overview**

This document provides comprehensive API endpoint documentation for the Multi-Tenant PIM System. All endpoints require authentication via Bearer token unless specified otherwise.

**Base URL**: `http://localhost:8000/api/v1` (Development) / `http://your-domain:8004/api/v1` (Production)

**Authentication**: `Authorization: Bearer <access_token>`

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

### **GET** `/product`
**Get all products for current tenant**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum items to return (default: 100)
- `category_id`: Filter by category ID (optional)

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Product Name",
    "description": "Product description",
    "price": 99.99,
    "category_id": 1,
    "tenant_id": 1
  }
]
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
**Get all users (superadmin only)**

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "email": "admin@pim.com",
    "role": "superadmin",
    "is_active": true,
    "tenant_id": null
  }
]
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
```json
{
  "detail": "Error message description"
}
```

### **Common HTTP Status Codes**
- **200**: Success
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (missing or invalid token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **500**: Internal Server Error

---

## 🔒 **Security Notes**

### **Token Management**
- **Expiration**: Tokens expire after 30 minutes by default
- **Refresh**: Use `/auth/refresh` to get new tokens
- **Storage**: Store tokens securely (httpOnly cookies recommended)
- **Transmission**: Always use HTTPS in production

### **Password Requirements**
- **Minimum Length**: 8 characters
- **Hashing**: Bcrypt with salt
- **Validation**: Server-side password strength validation

### **Role-Based Access Control**
- **Superadmin**: Full system access
- **Analyst**: Read access to all data
- **Tenant Admin**: Full access to tenant data
- **Tenant User**: Limited access to tenant data

---

## 📱 **Client Integration Examples**

### **JavaScript/TypeScript**
```typescript
// Login
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const { access_token } = await loginResponse.json();

// Use token for authenticated requests
const userResponse = await fetch('/api/v1/auth/me', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

### **Python**
```python
import requests

# Login
login_data = {
    'email': 'user@example.com',
    'password': 'password123'
}
login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
access_token = login_response.json()['access_token']

# Use token for authenticated requests
headers = {'Authorization': f'Bearer {access_token}'}
user_response = requests.get('http://localhost:8000/api/v1/auth/me', headers=headers)
```

### **cURL**
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Use token
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  "http://localhost:8000/api/v1/auth/me"
```

---

## 📞 **Support & Troubleshooting**

### **Common Issues**
1. **Token Expired**: Use `/auth/refresh` to get new token
2. **Invalid Credentials**: Check email/password combination
3. **Permission Denied**: Verify user role and permissions
4. **Database Errors**: Check database connection and schema

### **Getting Help**
- **Logs**: Check application logs for detailed error information
- **Database**: Verify database file exists and is accessible
- **Network**: Ensure proper port configuration and firewall settings

---

**Last Updated**: January 2025  
**Version**: 2.0 (JWT-based authentication)  
**Maintainer**: PIM System Team 