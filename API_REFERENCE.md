# Multi-Tenant PIM System API Reference

This document provides a comprehensive reference for all backend API endpoints, including sample input and output for UI/frontend integration.

---

## Auth

### POST /api/v1/auth/signup
**Input:**
```json
{
  "email": "user@example.com",
  "password": "strongpassword",
  "company_name": "Acme Inc"
}
```
**Output:**
```json
{
  "msg": "Signup successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "tenant_id": 1,
    "role": "admin"
  },
  "access_token": "jwt.token.here"
}
```

### POST /api/v1/auth/login
**Input:**
```json
{
  "email": "user@example.com",
  "password": "strongpassword"
}
```
**Output:**
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

### GET /api/v1/auth/me
**Headers:**  
`Authorization: Bearer <access_token>`
**Output:**
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

### POST /api/v1/auth/logout
**Headers:**  
`Authorization: Bearer <access_token>`
**Output:**
```json
{
  "msg": "Logout successful"
}
```

---

## Tenant & User

### GET /api/v1/tenant
**Headers:**  
`Authorization: Bearer <access_token>`
**Output:**
```json
[
  {
    "id": 1,
    "company_name": "Acme Inc",
    "logo_url": "https://example.com/logo.png",
    "created_at": "2024-07-06T12:00:00Z"
  },
  {
    "id": 2,
    "company_name": "Another Corp",
    "logo_url": null,
    "created_at": "2024-07-06T13:00:00Z"
  }
]
```

### GET /api/v1/tenant/me
**Headers:**  
`Authorization: Bearer <access_token>`
**Output:**
```json
{
  "id": 1,
  "company_name": "Acme Inc",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2024-07-06T12:00:00Z"
}
```

### POST /api/v1/tenant
**Input:**
```json
{
  "company_name": "Acme Inc",
  "logo_url": "https://example.com/logo.png"
}
```
**Output:**
```json
{
  "id": 1,
  "company_name": "Acme Inc",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2024-07-06T12:00:00Z"
}
```

### GET /api/v1/tenant/{id}
**Headers:**  
`Authorization: Bearer <access_token>`
**Output:**
```json
{
  "id": 1,
  "company_name": "Acme Inc",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2024-07-06T12:00:00Z"
}
```

### PATCH /api/v1/tenant/{id}
**Headers:**  
`Authorization: Bearer <access_token>`
**Input:**
```json
{
  "company_name": "Acme Corp",
  "logo_url": "https://example.com/newlogo.png"
}
```
**Output:**
```json
{
  "id": 1,
  "company_name": "Acme Corp",
  "logo_url": "https://example.com/newlogo.png",
  "created_at": "2024-07-06T12:00:00Z"
}
```

### GET /api/v1/tenant/{id}/users
**Headers:**  
`Authorization: Bearer <access_token>`
**Output:**
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "role": "admin"
  },
  {
    "id": 2,
    "email": "editor@example.com",
    "role": "editor"
  }
]
```

### GET /api/v1/users
**Headers:**  
`Authorization: Bearer <access_token>`
**Output:**
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "tenant_id": 1,
    "role": "admin"
  },
  {
    "id": 2,
    "email": "editor@example.com",
    "tenant_id": 1,
    "role": "editor"
  }
]
```

### GET /api/v1/users/{id}
**Headers:**  
`Authorization: Bearer <access_token>`
**Output:**
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

### PATCH /api/v1/users/{id}/role
**Headers:**  
`Authorization: Bearer <access_token>`
**Input:**
```json
{
  "role": "editor"
}
```
**Output:**
```json
{
  "id": 2,
  "email": "editor@example.com",
  "tenant_id": 1,
  "role": "editor"
}
```

---

## Progress Tracking

### GET /api/v1/progress/overview
**Headers:**  
`Authorization: Bearer <access_token>`
**Output:**
```json
{
  "overall_progress": 16.7,
  "required_progress": 33.3,
  "total_steps": 6,
  "completed_steps": 1,
  "required_steps": 3,
  "completed_required_steps": 1,
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
      "completed_at": "2024-07-06T12:00:00Z",
      "data": {
        "logo_url": "https://example.com/logo.png"
      }
    }
  ]
}
```

### GET /api/v1/progress/steps
**Headers:**  
`Authorization: Bearer <access_token>`
**Output:**
```json
{
  "overview": {
    "overall_progress": 16.7,
    "required_progress": 33.3,
    "total_steps": 6,
    "completed_steps": 1,
    "required_steps": 3,
    "completed_required_steps": 1
  },
  "categories": {
    "setup": [
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
        "completed_at": "2024-07-06T12:00:00Z",
        "data": {
          "logo_url": "https://example.com/logo.png"
        }
      }
    ],
    "configuration": [
      {
        "step_key": "category_setup",
        "title": "Product Categories",
        "description": "Set up your product categories and schemas",
        "order": 3,
        "is_required": true,
        "category": "configuration",
        "icon": "📂",
        "estimated_time": 10,
        "is_completed": false,
        "completed_at": null,
        "data": null
      }
    ],
    "data": [
      {
        "step_key": "product_import",
        "title": "Import Products",
        "description": "Import your product catalog",
        "order": 4,
        "is_required": true,
        "category": "data",
        "icon": "📦",
        "estimated_time": 15,
        "is_completed": false,
        "completed_at": null,
        "data": null
      }
    ]
  }
}
```

### GET /api/v1/progress/next-steps
**Headers:**  
`Authorization: Bearer <access_token>`
**Output:**
```json
{
  "pending_steps": [
    {
      "step_key": "user_invitation",
      "title": "Invite Team Members",
      "description": "Add team members to your organization",
      "order": 2,
      "is_required": false,
      "category": "setup",
      "icon": "👥",
      "estimated_time": 3,
      "is_completed": false,
      "completed_at": null,
      "data": null
    }
  ],
  "next_step": {
    "step_key": "user_invitation",
    "title": "Invite Team Members",
    "description": "Add team members to your organization",
    "order": 2,
    "is_required": false,
    "category": "setup",
    "icon": "👥",
    "estimated_time": 3,
    "is_completed": false,
    "completed_at": null,
    "data": null
  },
  "total_pending": 5
}
```

### POST /api/v1/progress/steps/{step_key}/complete
**Headers:**  
`Authorization: Bearer <access_token>`
**Input:**
```json
{
  "logo_url": "https://example.com/logo.png",
  "additional_data": "any additional data"
}
```
**Output:**
```json
{
  "step_key": "company_setup",
  "is_completed": true,
  "completed_at": "2024-07-06T12:00:00Z",
  "data": {
    "logo_url": "https://example.com/logo.png",
    "additional_data": "any additional data"
  }
}
```

### POST /api/v1/progress/steps/{step_key}/reset
**Headers:**  
`Authorization: Bearer <access_token>`
**Output:**
```json
{
  "step_key": "company_setup",
  "is_completed": false,
  "completed_at": null
}
```

---

## Categories

### POST /api/v1/categories/upload
**Input:**  
Multipart/form-data with a CSV file.
**Output:**
```json
{
  "msg": "Categories uploaded successfully",
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "schema_json": { "fields": [ ... ] }
    }
  ]
}
```

### GET /api/v1/categories
**Output:**
```json
[
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic items",
    "schema_json": { "fields": [ ... ] }
  }
]
```

### GET /api/v1/categories/{id}/schema
**Output:**
```json
{
  "id": 1,
  "name": "Electronics",
  "schema_json": {
    "fields": [
      { "name": "brand", "type": "string", "required": true },
      { "name": "warranty", "type": "string", "required": false }
    ]
  }
}
```

### PUT /api/v1/categories/{id}/schema
**Input:**
```json
{
  "schema_json": {
    "fields": [
      { "name": "brand", "type": "string", "required": true },
      { "name": "warranty", "type": "string", "required": false }
    ]
  }
}
```
**Output:**  
Same as above.

---

## Products

### POST /api/v1/products/upload
**Input:**  
Multipart/form-data with a CSV file.
**Output:**
```json
{
  "msg": "Products uploaded successfully",
  "products": [
    {
      "id": 1,
      "sku_id": "SKU123",
      "category_id": 1,
      "dynamic_fields": { "brand": "Sony", "warranty": "2 years" }
    }
  ]
}
```

### GET /api/v1/products
**Query params:**  
`?category_id=1&search=sony`
**Output:**
```json
[
  {
    "id": 1,
    "sku_id": "SKU123",
    "category_id": 1,
    "price": 199.99,
    "manufacturer": "Sony",
    "supplier": "SupplierX",
    "image_url": "https://example.com/image.jpg",
    "dynamic_fields": { "brand": "Sony", "warranty": "2 years" }
  }
]
```

### GET /api/v1/products/{id}
**Output:**
```json
{
  "id": 1,
  "sku_id": "SKU123",
  "category_id": 1,
  "price": 199.99,
  "manufacturer": "Sony",
  "supplier": "SupplierX",
  "image_url": "https://example.com/image.jpg",
  "dynamic_fields": { "brand": "Sony", "warranty": "2 years" }
}
```

### PUT /api/v1/products/{id}
**Input:**
```json
{
  "price": 189.99,
  "dynamic_fields": { "warranty": "3 years" }
}
```
**Output:**  
Same as above, with updated fields.

### POST /api/v1/products/{id}/favorite
**Output:**
```json
{
  "msg": "Product marked as favorite"
}
```

### POST /api/v1/products/{id}/compare
**Output:**
```json
{
  "msg": "Product added to comparison list"
}
```

### POST /api/v1/products/{id}/report
**Input:**
```json
{
  "reason": "Incorrect price"
}
```
**Output:**
```json
{
  "msg": "Product reported"
}
```

---

## Search

### POST /api/v1/search/index/init
**Output:**
```json
{
  "msg": "Init search index"
}
```

### POST /api/v1/search/reindex
**Output:**
```json
{
  "msg": "Reindex"
}
```

### GET /api/v1/search
**Query params:**  
`?q=sony&category_id=1`
**Output:**
```json
[
  {
    "id": 1,
    "sku_id": "SKU123",
    "category_id": 1,
    "price": 199.99,
    "manufacturer": "Sony",
    "dynamic_fields": { "brand": "Sony" }
  }
]
```

---

## Chatbot

### POST /api/v1/chat/ask
**Input:**
```json
{
  "query": "Show me all Sony products under $200"
}
```
**Output:**
```json
{
  "response": "Here are all Sony products under $200...",
  "products": [
    { "id": 1, "sku_id": "SKU123", "price": 199.99 }
  ]
}
```

### POST /api/v1/chat/session
**Output:**
```json
{
  "id": 1,
  "created_at": "2024-07-06T12:00:00Z"
}
```

### GET /api/v1/chat/session/{id}
**Output:**
```json
{
  "id": 1,
  "context_json": { "last_query": "Show me all Sony products under $200" },
  "created_at": "2024-07-06T12:00:00Z"
}
```

### GET /api/v1/chat/favorites
**Output:**
```json
[
  { "id": 1, "sku_id": "SKU123", "price": 199.99 }
]
```

### GET /api/v1/chat/comparisons
**Output:**
```json
[
  { "id": 1, "sku_id": "SKU123", "price": 199.99 },
  { "id": 2, "sku_id": "SKU456", "price": 299.99 }
]
``` 