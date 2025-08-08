# 🚀 UI Quick Reference - PIM System

## 🔑 **Authentication**

### **Login**
```javascript
// Superadmin or Regular User
POST /api/v1/auth/login
{
  "email": "admin@pim.com",
  "password": "admin123"
}

// Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 11,
    "email": "admin@pim.com",
    "role": "superadmin",
    "first_name": "System",
    "last_name": "Administrator",
    "is_active": true,
    "is_blocked": false,
    "tenant_id": null
  }
}
```

### **Token Usage**
```javascript
// Add to all API requests
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

---

## 📦 **Product Management**

### **List Products**
```javascript
GET /api/v1/products?view_type=all&limit=50&skip=0
```

### **Get Product**
```javascript
GET /api/v1/products/{id}
```

### **Update Product**
```javascript
PUT /api/v1/products/{id}
{
  "name": "Updated Product",
  "price": 99.99,
  "brand": "Brand Name"
}
```

### **Delete Product**
```javascript
DELETE /api/v1/products/{id}
```

---

## 🔍 **Search & Filtering**

### **Search Products**
```javascript
GET /api/v1/search?q=laptop&brand=Dell,HP&manufacturer=Intel
```

### **Get Filter Options**
```javascript
GET /api/v1/products/filters/brand
GET /api/v1/products/filters/manufacturer
GET /api/v1/products/filters/category
```

---

## 📁 **File Upload**

### **Step 1: Analyze File**
```javascript
POST /api/v1/products/upload/analyze
Content-Type: multipart/form-data
file: [CSV/Excel file]
```

### **Step 2: Save Products**
```javascript
POST /api/v1/products/upload
{
  "analysis_id": "uuid",
  "field_mappings": {...},
  "products": [...]
}
```

---

## 👑 **Superadmin System**

### **Dashboard**
```javascript
GET /api/v1/superadmin/dashboard
```

### **List Users**
```javascript
GET /api/v1/superadmin/users?role=tenant_user&is_active=true
```

### **Create User**
```javascript
POST /api/v1/superadmin/users
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "tenant_user",
  "tenant_id": 1
}
```

### **Block/Unblock User**
```javascript
POST /api/v1/superadmin/users/{id}/block
POST /api/v1/superadmin/users/{id}/unblock
{
  "reason": "Violation of terms"
}
```

### **List Tenants**
```javascript
GET /api/v1/superadmin/tenants
```

### **Audit Logs**
```javascript
GET /api/v1/superadmin/audit-logs?limit=50
```

---

## 🎯 **Field Configuration**

### **Get Configuration**
```javascript
GET /api/v1/products/fields/configuration
```

### **Update Configuration**
```javascript
PUT /api/v1/products/fields/configuration/{field_id}
{
  "is_searchable": true,
  "is_editable": true,
  "is_primary": true,
  "display_order": 1
}
```

---

## 🏷️ **Categories**

### **List Categories**
```javascript
GET /api/v1/categories
```

### **Create Category**
```javascript
POST /api/v1/categories
{
  "name": "Electronics",
  "description": "Electronic products"
}
```

---

## 🏢 **Tenants**

### **Create Tenant**
```javascript
POST /api/v1/tenant
{
  "company_name": "My Company",
  "logo_url": "https://example.com/logo.png"
}
```

### **Update Tenant**
```javascript
PATCH /api/v1/tenant/{id}
{
  "company_name": "Updated Company",
  "logo_url": "https://example.com/new-logo.png"
}
```

---

## ⚠️ **Error Handling**

### **Common Error Codes**
- `400` - Bad Request (Invalid data)
- `401` - Unauthorized (Invalid/missing token)
- `403` - Forbidden (Insufficient permissions)
- `404` - Not Found (Resource doesn't exist)
- `500` - Internal Server Error

### **Error Response Format**
```javascript
{
  "detail": "Error message",
  "status_code": 400
}
```

---

## 🔄 **Real-time Updates**

### **WebSocket Connection**
```javascript
const ws = new WebSocket(`ws://localhost:8004/ws?token=${token}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle real-time updates
};
```

---

## 📊 **Response Formats**

### **Paginated Response**
```javascript
{
  "items": [...],
  "total_count": 100,
  "skip": 0,
  "limit": 50
}
```

### **Success Response**
```javascript
{
  "message": "Operation successful",
  "data": {...}
}
```

---

## 🎨 **UI Components**

### **Product Card**
```javascript
const productCard = `
  <div class="product-card">
    <img src="${product.image_url}" alt="${product.name}">
    <h3>${product.name}</h3>
    <p>${product.brand}</p>
    <p>$${product.price}</p>
    <button onclick="editProduct(${product.id})">Edit</button>
  </div>
`;
```

### **Search Component**
```javascript
const searchComponent = `
  <div class="search">
    <input type="text" placeholder="Search products...">
    <select id="brand-filter">
      <option value="">All Brands</option>
    </select>
    <button onclick="search()">Search</button>
  </div>
`;
```

---

## 🚀 **Quick Start**

### **1. Login**
```javascript
const login = async (email, password) => {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
};
```

### **2. Load Products**
```javascript
const loadProducts = async () => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('/api/v1/products', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  return data.products;
};
```

### **3. Search Products**
```javascript
const searchProducts = async (query) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`/api/v1/search?q=${query}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  return data.products;
};
```

---

## 📱 **Mobile Considerations**

### **Responsive Design**
```css
/* Mobile-first approach */
.product-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .product-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .product-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### **Touch-friendly Buttons**
```css
.btn {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 16px;
}
```

---

## 🔧 **Development Tips**

### **Debug Mode**
```javascript
const DEBUG = process.env.NODE_ENV === 'development';

const apiRequest = async (url, options) => {
  if (DEBUG) console.log('[API]', url, options);
  // ... rest of the code
};
```

### **Error Tracking**
```javascript
const handleError = (error, context) => {
  console.error(`Error in ${context}:`, error);
  // Send to error tracking service
};
```

---

## 📚 **Resources**

- [Full Integration Guide](./UI_INTEGRATION_GUIDE.md)
- [API Documentation](./API_INTEGRATION.md)
- [Superadmin Guide](./SUPERADMIN_CREDENTIALS.md)
- [Deployment Guide](./EXISTING_DEPLOYMENT.md)

---

**🎯 This quick reference covers the most commonly used endpoints and features for UI development!** 