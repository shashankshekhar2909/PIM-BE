# 🎨 UI Integration Guide - Complete PIM System

## 📋 **Table of Contents**
1. [Authentication & Authorization](#authentication--authorization)
2. [User Management](#user-management)
3. [Tenant Management](#tenant-management)
4. [Product Management](#product-management)
5. [Category Management](#category-management)
6. [Search & Filtering](#search--filtering)
7. [File Upload & AI Processing](#file-upload--ai-processing)
8. [Superadmin System](#superadmin-system)
9. [Error Handling](#error-handling)
10. [WebSocket & Real-time](#websocket--real-time)

---

## 🔐 **Authentication & Authorization**

### **Login (Works for Both Superadmin and Regular Users)**

```javascript
// Login API
const login = async (email, password) => {
  try {
    const response = await fetch('http://localhost:8004/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // Store token and user info
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      return data;
    } else {
      throw new Error(data.detail || 'Login failed');
    }
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

// Usage
const handleLogin = async () => {
  try {
    const result = await login('admin@pim.com', 'admin123');
    console.log('Login successful:', result.user);
    
    // Redirect based on role
    if (result.user.role === 'superadmin') {
      window.location.href = '/superadmin/dashboard';
    } else {
      window.location.href = '/dashboard';
    }
  } catch (error) {
    console.error('Login failed:', error.message);
  }
};
```

### **Token Management**

```javascript
// Get stored token
const getToken = () => {
  return localStorage.getItem('access_token');
};

// Check if user is authenticated
const isAuthenticated = () => {
  return !!getToken();
};

// Logout
const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};

// API request helper with authentication
const apiRequest = async (url, options = {}) => {
  const token = getToken();
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };
  
  const response = await fetch(url, config);
  
  if (response.status === 401) {
    // Token expired or invalid
    logout();
    throw new Error('Authentication required');
  }
  
  return response;
};
```

### **User Profile**

```javascript
// Get current user profile
const getCurrentUser = async () => {
  try {
    const response = await apiRequest('http://localhost:8004/api/v1/auth/me');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to get user profile:', error);
    throw error;
  }
};
```

---

## 👥 **User Management**

### **List Users (Superadmin Only)**

```javascript
// List all users
const listUsers = async (filters = {}) => {
  try {
    const params = new URLSearchParams(filters);
    const response = await apiRequest(`http://localhost:8004/api/v1/superadmin/users?${params}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to list users:', error);
    throw error;
  }
};

// Usage
const loadUsers = async () => {
  try {
    const users = await listUsers({
      role: 'tenant_user',
      is_active: true,
      limit: 50
    });
    
    // Render users table
    renderUsersTable(users.users);
  } catch (error) {
    showError('Failed to load users');
  }
};
```

### **Create User**

```javascript
// Create new user
const createUser = async (userData) => {
  try {
    const response = await apiRequest('http://localhost:8004/api/v1/superadmin/users', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to create user:', error);
    throw error;
  }
};

// Usage
const handleCreateUser = async (formData) => {
  try {
    const newUser = await createUser({
      email: formData.email,
      password: formData.password,
      first_name: formData.firstName,
      last_name: formData.lastName,
      role: formData.role,
      tenant_id: formData.tenantId
    });
    
    showSuccess('User created successfully');
    loadUsers(); // Refresh user list
  } catch (error) {
    showError('Failed to create user');
  }
};
```

### **Block/Unblock User**

```javascript
// Block user
const blockUser = async (userId, reason) => {
  try {
    const response = await apiRequest(`http://localhost:8004/api/v1/superadmin/users/${userId}/block`, {
      method: 'POST',
      body: JSON.stringify({ reason })
    });
    
    return await response.json();
  } catch (error) {
    console.error('Failed to block user:', error);
    throw error;
  }
};

// Unblock user
const unblockUser = async (userId, reason) => {
  try {
    const response = await apiRequest(`http://localhost:8004/api/v1/superadmin/users/${userId}/unblock`, {
      method: 'POST',
      body: JSON.stringify({ reason })
    });
    
    return await response.json();
  } catch (error) {
    console.error('Failed to unblock user:', error);
    throw error;
  }
};
```

---

## 🏢 **Tenant Management**

### **List Tenants**

```javascript
// List all tenants
const listTenants = async (filters = {}) => {
  try {
    const params = new URLSearchParams(filters);
    const response = await apiRequest(`http://localhost:8004/api/v1/superadmin/tenants?${params}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to list tenants:', error);
    throw error;
  }
};
```

### **Create Tenant**

```javascript
// Create new tenant
const createTenant = async (tenantData) => {
  try {
    const response = await apiRequest('http://localhost:8004/api/v1/tenant', {
      method: 'POST',
      body: JSON.stringify(tenantData)
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to create tenant:', error);
    throw error;
  }
};

// Usage
const handleCreateTenant = async (formData) => {
  try {
    const newTenant = await createTenant({
      company_name: formData.companyName,
      logo_url: formData.logoUrl || null
    });
    
    showSuccess('Tenant created successfully');
    loadTenants(); // Refresh tenant list
  } catch (error) {
    showError('Failed to create tenant');
  }
};
```

### **Update Tenant**

```javascript
// Update tenant
const updateTenant = async (tenantId, tenantData) => {
  try {
    const response = await apiRequest(`http://localhost:8004/api/v1/tenant/${tenantId}`, {
      method: 'PATCH',
      body: JSON.stringify(tenantData)
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to update tenant:', error);
    throw error;
  }
};
```

---

## 📦 **Product Management**

### **List Products**

```javascript
// List products with filters
const listProducts = async (filters = {}) => {
  try {
    const params = new URLSearchParams(filters);
    const response = await apiRequest(`http://localhost:8004/api/v1/products?${params}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to list products:', error);
    throw error;
  }
};

// Usage with field configuration
const loadProducts = async (viewType = 'all') => {
  try {
    const products = await listProducts({
      view_type: viewType, // 'primary', 'secondary', 'all'
      limit: 50
    });
    
    renderProductsGrid(products.products);
  } catch (error) {
    showError('Failed to load products');
  }
};
```

### **Get Product Details**

```javascript
// Get single product
const getProduct = async (productId) => {
  try {
    const response = await apiRequest(`http://localhost:8004/api/v1/products/${productId}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to get product:', error);
    throw error;
  }
};
```

### **Update Product**

```javascript
// Update product
const updateProduct = async (productId, productData) => {
  try {
    const response = await apiRequest(`http://localhost:8004/api/v1/products/${productId}`, {
      method: 'PUT',
      body: JSON.stringify(productData)
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to update product:', error);
    throw error;
  }
};
```

### **Delete Product**

```javascript
// Delete product
const deleteProduct = async (productId) => {
  try {
    const response = await apiRequest(`http://localhost:8004/api/v1/products/${productId}`, {
      method: 'DELETE'
    });
    
    return response.ok;
  } catch (error) {
    console.error('Failed to delete product:', error);
    throw error;
  }
};
```

---

## 🏷️ **Category Management**

### **List Categories**

```javascript
// List categories
const listCategories = async (filters = {}) => {
  try {
    const params = new URLSearchParams(filters);
    const response = await apiRequest(`http://localhost:8004/api/v1/categories?${params}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to list categories:', error);
    throw error;
  }
};
```

### **Create Category**

```javascript
// Create category
const createCategory = async (categoryData) => {
  try {
    const response = await apiRequest('http://localhost:8004/api/v1/categories', {
      method: 'POST',
      body: JSON.stringify(categoryData)
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to create category:', error);
    throw error;
  }
};
```

---

## 🔍 **Search & Filtering**

### **Search Products**

```javascript
// Search products
const searchProducts = async (query, filters = {}) => {
  try {
    const params = new URLSearchParams({
      q: query,
      ...filters
    });
    
    const response = await apiRequest(`http://localhost:8004/api/v1/search?${params}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Search failed:', error);
    throw error;
  }
};

// Usage with field-specific search
const handleSearch = async (searchTerm, fieldFilters = {}) => {
  try {
    const results = await searchProducts(searchTerm, fieldFilters);
    
    // Example: Search by brand and manufacturer
    // const results = await searchProducts('laptop', { brand: 'Dell,HP', manufacturer: 'Intel' });
    
    renderSearchResults(results.products);
  } catch (error) {
    showError('Search failed');
  }
};
```

### **Get Filter Options**

```javascript
// Get unique filter values
const getFilterOptions = async (field) => {
  try {
    const response = await apiRequest(`http://localhost:8004/api/v1/products/filters/${field}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to get filter options:', error);
    throw error;
  }
};

// Usage
const loadFilterOptions = async () => {
  try {
    const brands = await getFilterOptions('brand');
    const manufacturers = await getFilterOptions('manufacturer');
    const categories = await getFilterOptions('category');
    
    populateFilterDropdowns({ brands, manufacturers, categories });
  } catch (error) {
    showError('Failed to load filter options');
  }
};
```

---

## 📁 **File Upload & AI Processing**

### **Analyze File (Step 1)**

```javascript
// Analyze CSV/Excel file
const analyzeFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiRequest('http://localhost:8004/api/v1/products/upload/analyze', {
      method: 'POST',
      headers: {
        // Remove Content-Type to let browser set it with boundary
      },
      body: formData
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('File analysis failed:', error);
    throw error;
  }
};

// Usage
const handleFileUpload = async (file) => {
  try {
    showLoading('Analyzing file...');
    
    const analysis = await analyzeFile(file);
    
    // Show analysis results
    showAnalysisResults(analysis);
    
    // Store analysis data for next step
    sessionStorage.setItem('fileAnalysis', JSON.stringify(analysis));
    
  } catch (error) {
    showError('File analysis failed');
  } finally {
    hideLoading();
  }
};
```

### **Save Products (Step 2)**

```javascript
// Save analyzed products
const saveProducts = async (analysisData) => {
  try {
    const response = await apiRequest('http://localhost:8004/api/v1/products/upload', {
      method: 'POST',
      body: JSON.stringify(analysisData)
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to save products:', error);
    throw error;
  }
};

// Usage
const handleSaveProducts = async () => {
  try {
    const analysisData = JSON.parse(sessionStorage.getItem('fileAnalysis'));
    
    if (!analysisData) {
      throw new Error('No analysis data found');
    }
    
    showLoading('Saving products...');
    
    const result = await saveProducts(analysisData);
    
    showSuccess(`Successfully saved ${result.saved_count} products`);
    
    // Clear analysis data
    sessionStorage.removeItem('fileAnalysis');
    
    // Redirect to products list
    window.location.href = '/products';
    
  } catch (error) {
    showError('Failed to save products');
  } finally {
    hideLoading();
  }
};
```

---

## 👑 **Superadmin System**

### **Dashboard**

```javascript
// Get superadmin dashboard
const getSuperadminDashboard = async () => {
  try {
    const response = await apiRequest('http://localhost:8004/api/v1/superadmin/dashboard');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to get dashboard:', error);
    throw error;
  }
};

// Usage
const loadDashboard = async () => {
  try {
    const dashboard = await getSuperadminDashboard();
    
    // Update statistics
    updateStatistics(dashboard.statistics);
    
    // Update user role chart
    updateUserRoleChart(dashboard.users_by_role);
    
    // Update recent activity
    updateRecentActivity(dashboard.recent_activity);
    
  } catch (error) {
    showError('Failed to load dashboard');
  }
};
```

### **Audit Logs**

```javascript
// Get audit logs
const getAuditLogs = async (filters = {}) => {
  try {
    const params = new URLSearchParams(filters);
    const response = await apiRequest(`http://localhost:8004/api/v1/superadmin/audit-logs?${params}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to get audit logs:', error);
    throw error;
  }
};
```

---

## 🎯 **Field Configuration**

### **Get Field Configuration**

```javascript
// Get field configuration
const getFieldConfiguration = async () => {
  try {
    const response = await apiRequest('http://localhost:8004/api/v1/products/fields/configuration');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to get field configuration:', error);
    throw error;
  }
};

// Usage
const loadFieldConfiguration = async () => {
  try {
    const config = await getFieldConfiguration();
    
    // Render field configuration UI
    renderFieldConfiguration(config.fields);
    
    // Update search fields
    updateSearchFields(config.fields.filter(f => f.is_searchable));
    
    // Update editable fields
    updateEditableFields(config.fields.filter(f => f.is_editable));
    
  } catch (error) {
    showError('Failed to load field configuration');
  }
};
```

### **Update Field Configuration**

```javascript
// Update field configuration
const updateFieldConfiguration = async (fieldId, config) => {
  try {
    const response = await apiRequest(`http://localhost:8004/api/v1/products/fields/configuration/${fieldId}`, {
      method: 'PUT',
      body: JSON.stringify(config)
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to update field configuration:', error);
    throw error;
  }
};
```

---

## ⚠️ **Error Handling**

### **Global Error Handler**

```javascript
// Global error handler
const handleApiError = (error, context = '') => {
  console.error(`API Error in ${context}:`, error);
  
  let message = 'An unexpected error occurred';
  
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;
    
    switch (status) {
      case 400:
        message = data.detail || 'Invalid request';
        break;
      case 401:
        message = 'Authentication required';
        logout();
        break;
      case 403:
        message = 'Access denied';
        break;
      case 404:
        message = 'Resource not found';
        break;
      case 500:
        message = 'Server error';
        break;
      default:
        message = data.detail || `Error ${status}`;
    }
  } else if (error.message) {
    message = error.message;
  }
  
  showError(message);
};

// Usage in components
const safeApiCall = async (apiFunction, ...args) => {
  try {
    return await apiFunction(...args);
  } catch (error) {
    handleApiError(error, apiFunction.name);
    throw error;
  }
};
```

### **Loading States**

```javascript
// Loading state management
let loadingCount = 0;

const showLoading = (message = 'Loading...') => {
  loadingCount++;
  // Show loading spinner
  document.getElementById('loading-spinner').style.display = 'block';
  document.getElementById('loading-message').textContent = message;
};

const hideLoading = () => {
  loadingCount--;
  if (loadingCount <= 0) {
    loadingCount = 0;
    // Hide loading spinner
    document.getElementById('loading-spinner').style.display = 'none';
  }
};
```

---

## 🔄 **WebSocket & Real-time**

### **Real-time Updates**

```javascript
// WebSocket connection for real-time updates
class RealTimeManager {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }
  
  connect() {
    try {
      const token = getToken();
      this.ws = new WebSocket(`ws://localhost:8004/ws?token=${token}`);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };
      
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.reconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  }
  
  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
        this.connect();
      }, 1000 * this.reconnectAttempts);
    }
  }
  
  handleMessage(data) {
    switch (data.type) {
      case 'product_updated':
        this.handleProductUpdate(data.product);
        break;
      case 'user_blocked':
        this.handleUserBlocked(data.user);
        break;
      case 'audit_log':
        this.handleAuditLog(data.log);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  }
  
  handleProductUpdate(product) {
    // Update product in UI
    updateProductInList(product);
    showNotification(`Product "${product.name}" was updated`);
  }
  
  handleUserBlocked(user) {
    // Handle user blocked event
    if (user.id === getCurrentUser().id) {
      logout();
      showError('Your account has been blocked');
    }
  }
  
  handleAuditLog(log) {
    // Update audit log in UI
    addAuditLogToList(log);
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Usage
const realTimeManager = new RealTimeManager();

// Connect on app start
if (isAuthenticated()) {
  realTimeManager.connect();
}

// Disconnect on logout
const logout = () => {
  realTimeManager.disconnect();
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};
```

---

## 🎨 **UI Components Examples**

### **Product Card Component**

```javascript
// Product card component
const createProductCard = (product) => {
  return `
    <div class="product-card" data-product-id="${product.id}">
      <div class="product-image">
        <img src="${product.image_url || '/placeholder.png'}" alt="${product.name}">
      </div>
      <div class="product-info">
        <h3 class="product-name">${product.name}</h3>
        <p class="product-brand">${product.brand || 'N/A'}</p>
        <p class="product-price">$${product.price || '0.00'}</p>
        <div class="product-actions">
          <button onclick="viewProduct(${product.id})" class="btn btn-primary">View</button>
          <button onclick="editProduct(${product.id})" class="btn btn-secondary">Edit</button>
          <button onclick="addToFavorites(${product.id})" class="btn btn-outline">
            <i class="fas fa-heart"></i>
          </button>
        </div>
      </div>
    </div>
  `;
};
```

### **Search Component**

```javascript
// Search component
const createSearchComponent = () => {
  return `
    <div class="search-container">
      <div class="search-input">
        <input type="text" id="search-input" placeholder="Search products...">
        <button onclick="performSearch()" class="btn btn-primary">
          <i class="fas fa-search"></i>
        </button>
      </div>
      <div class="search-filters">
        <select id="brand-filter">
          <option value="">All Brands</option>
        </select>
        <select id="category-filter">
          <option value="">All Categories</option>
        </select>
        <select id="price-range">
          <option value="">All Prices</option>
          <option value="0-50">$0 - $50</option>
          <option value="50-100">$50 - $100</option>
          <option value="100+">$100+</option>
        </select>
      </div>
    </div>
  `;
};
```

### **File Upload Component**

```javascript
// File upload component
const createFileUploadComponent = () => {
  return `
    <div class="file-upload-container">
      <div class="upload-area" id="upload-area">
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Drag and drop your CSV/Excel file here</p>
        <p>or</p>
        <input type="file" id="file-input" accept=".csv,.xlsx,.xls" style="display: none;">
        <button onclick="document.getElementById('file-input').click()" class="btn btn-primary">
          Choose File
        </button>
      </div>
      <div class="upload-progress" id="upload-progress" style="display: none;">
        <div class="progress-bar">
          <div class="progress-fill" id="progress-fill"></div>
        </div>
        <p id="progress-text">Analyzing file...</p>
      </div>
    </div>
  `;
};
```

---

## 📱 **Mobile Responsiveness**

### **Responsive Design Guidelines**

```css
/* Mobile-first responsive design */
.product-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  padding: 1rem;
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

@media (min-width: 1440px) {
  .product-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Mobile navigation */
.mobile-nav {
  display: none;
}

@media (max-width: 768px) {
  .desktop-nav {
    display: none;
  }
  
  .mobile-nav {
    display: block;
  }
}
```

---

## 🚀 **Performance Optimization**

### **Lazy Loading**

```javascript
// Lazy load images
const lazyLoadImages = () => {
  const images = document.querySelectorAll('img[data-src]');
  
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
        observer.unobserve(img);
      }
    });
  });
  
  images.forEach(img => imageObserver.observe(img));
};

// Lazy load components
const lazyLoadComponent = async (componentName) => {
  try {
    const module = await import(`./components/${componentName}.js`);
    return module.default;
  } catch (error) {
    console.error(`Failed to load component ${componentName}:`, error);
    return null;
  }
};
```

### **Caching**

```javascript
// Simple caching mechanism
const cache = new Map();

const cachedApiCall = async (key, apiFunction, ttl = 5 * 60 * 1000) => {
  const cached = cache.get(key);
  
  if (cached && Date.now() - cached.timestamp < ttl) {
    return cached.data;
  }
  
  const data = await apiFunction();
  cache.set(key, {
    data,
    timestamp: Date.now()
  });
  
  return data;
};

// Usage
const getCachedProducts = () => {
  return cachedApiCall('products', () => listProducts());
};
```

---

## 🔧 **Development Tools**

### **Debug Mode**

```javascript
// Debug mode for development
const DEBUG = process.env.NODE_ENV === 'development';

const debugLog = (...args) => {
  if (DEBUG) {
    console.log('[DEBUG]', ...args);
  }
};

const debugApiCall = async (url, options) => {
  if (DEBUG) {
    console.log('[API]', url, options);
  }
  
  const start = Date.now();
  const response = await apiRequest(url, options);
  const duration = Date.now() - start;
  
  if (DEBUG) {
    console.log('[API]', `Response in ${duration}ms:`, response);
  }
  
  return response;
};
```

### **Error Tracking**

```javascript
// Error tracking
const trackError = (error, context = '') => {
  const errorData = {
    message: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    url: window.location.href
  };
  
  // Send to error tracking service
  if (DEBUG) {
    console.error('[ERROR]', errorData);
  } else {
    // Send to production error tracking
    fetch('/api/errors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(errorData)
    }).catch(console.error);
  }
};
```

---

## 📊 **Analytics & Monitoring**

### **User Analytics**

```javascript
// Track user actions
const trackEvent = (eventName, properties = {}) => {
  const eventData = {
    event: eventName,
    properties,
    timestamp: new Date().toISOString(),
    userId: getCurrentUser()?.id,
    sessionId: sessionStorage.getItem('sessionId')
  };
  
  // Send to analytics service
  if (window.gtag) {
    window.gtag('event', eventName, properties);
  }
  
  // Send to our analytics endpoint
  fetch('/api/analytics/events', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(eventData)
  }).catch(console.error);
};

// Usage
const trackProductView = (productId, productName) => {
  trackEvent('product_view', {
    product_id: productId,
    product_name: productName
  });
};

const trackSearch = (query, resultsCount) => {
  trackEvent('search', {
    query,
    results_count: resultsCount
  });
};
```

---

## 🎯 **Complete Integration Example**

```javascript
// Complete integration example
class PIMIntegration {
  constructor() {
    this.baseUrl = 'http://localhost:8004';
    this.token = null;
    this.user = null;
    this.realTimeManager = null;
  }
  
  async init() {
    // Check authentication
    this.token = localStorage.getItem('access_token');
    this.user = JSON.parse(localStorage.getItem('user') || 'null');
    
    if (this.token && this.user) {
      // Initialize real-time connection
      this.realTimeManager = new RealTimeManager();
      this.realTimeManager.connect();
      
      // Load initial data
      await this.loadInitialData();
    } else {
      // Redirect to login
      window.location.href = '/login';
    }
  }
  
  async loadInitialData() {
    try {
      // Load field configuration
      const fieldConfig = await this.getFieldConfiguration();
      this.renderFieldConfiguration(fieldConfig);
      
      // Load products
      const products = await this.listProducts();
      this.renderProducts(products);
      
      // Load categories
      const categories = await this.listCategories();
      this.renderCategories(categories);
      
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  }
  
  // ... implement all the methods above
}

// Initialize the integration
const pim = new PIMIntegration();
pim.init();
```

---

## 📚 **Additional Resources**

- [API Documentation](./API_INTEGRATION.md)
- [Superadmin Guide](./SUPERADMIN_CREDENTIALS.md)
- [Deployment Guide](./EXISTING_DEPLOYMENT.md)
- [Error Handling](./ERROR_HANDLING.md)

---

**🎉 This comprehensive integration guide covers all aspects of the PIM system for UI development!** 