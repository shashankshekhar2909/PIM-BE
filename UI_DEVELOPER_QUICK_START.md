# 🚀 UI Developer Quick Start Guide

## 📋 **Overview**

This guide helps UI developers quickly integrate with the PIM System API. The system uses JWT-based authentication and provides a clean REST API for all operations.

---

## 🔐 **Authentication Flow**

### **1. User Registration**
```typescript
// Register a new user
const signup = async (email: string, password: string, companyName: string) => {
  const response = await fetch('/api/v1/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, company_name: companyName })
  });
  
  const data = await response.json();
  if (response.ok) {
    // Store token
    localStorage.setItem('access_token', data.access_token);
    return data.user;
  } else {
    throw new Error(data.detail);
  }
};
```

### **2. User Login**
```typescript
// Login existing user
const login = async (email: string, password: string) => {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  if (response.ok) {
    // Store token
    localStorage.setItem('access_token', data.access_token);
    return data.user;
  } else {
    throw new Error(data.detail);
  }
};
```

### **3. Token Management**
```typescript
// Get stored token
const getToken = () => localStorage.getItem('access_token');

// Check if user is authenticated
const isAuthenticated = () => !!getToken();

// Logout user
const logout = () => {
  localStorage.removeItem('access_token');
  // Redirect to login page
};

// Refresh token before expiration
const refreshToken = async () => {
  const token = getToken();
  if (!token) return null;
  
  const response = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return data.access_token;
  } else {
    // Token expired, redirect to login
    logout();
    return null;
  }
};
```

---

## 🌐 **API Client Setup**

### **Base API Client**
```typescript
class APIClient {
  private baseURL: string;
  
  constructor(baseURL: string = '/api/v1') {
    this.baseURL = baseURL;
  }
  
  private async request(endpoint: string, options: RequestInit = {}) {
    const token = getToken();
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
    };
    
    const response = await fetch(url, config);
    
    if (response.status === 401) {
      // Token expired, try to refresh
      const newToken = await refreshToken();
      if (newToken) {
        // Retry request with new token
        config.headers = {
          ...config.headers,
          'Authorization': `Bearer ${newToken}`,
        };
        return fetch(url, config);
      } else {
        logout();
        throw new Error('Authentication required');
      }
    }
    
    return response;
  }
  
  // Auth methods
  async signup(email: string, password: string, companyName: string) {
    const response = await this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, company_name: companyName })
    });
    return response.json();
  }
  
  async login(email: string, password: string) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    return response.json();
  }
  
  async getCurrentUser() {
    const response = await this.request('/auth/me');
    return response.json();
  }
  
  // Product methods
  async getProducts(params: { skip?: number; limit?: number; category_id?: number } = {}) {
    const queryString = new URLSearchParams(params as any).toString();
    const response = await this.request(`/product?${queryString}`);
    return response.json();
  }
  
  async createProduct(product: { name: string; description?: string; price: number; category_id: number }) {
    const response = await this.request('/product', {
      method: 'POST',
      body: JSON.stringify(product)
    });
    return response.json();
  }
  
  // Category methods
  async getCategories() {
    const response = await this.request('/category');
    return response.json();
  }
  
  async createCategory(category: { name: string; description?: string }) {
    const response = await this.request('/category', {
      method: 'POST',
      body: JSON.stringify(category)
    });
    return response.json();
  }
  
  // Search methods
  async search(query: string, type: 'products' | 'categories' | 'users' | 'all' = 'all', limit: number = 20) {
    const params = new URLSearchParams({ q: query, type, limit: limit.toString() });
    const response = await this.request(`/search?${params}`);
    return response.json();
  }
}

// Create global API client instance
export const apiClient = new APIClient();
```

---

## 🎯 **Common UI Patterns**

### **Protected Route Component**
```typescript
import React from 'react';
import { Navigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole 
}) => {
  const token = getToken();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    if (token) {
      apiClient.getCurrentUser()
        .then(userData => {
          setUser(userData);
          setLoading(false);
        })
        .catch(() => {
          logout();
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [token]);
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }
  
  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }
  
  return <>{children}</>;
};
```

### **Login Form Component**
```typescript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const result = await apiClient.login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      
      <div>
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      
      <div>
        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};
```

### **Product List Component**
```typescript
import React, { useState, useEffect } from 'react';

interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  category_id: number;
}

export const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  useEffect(() => {
    loadProducts();
  }, []);
  
  const loadProducts = async () => {
    try {
      const data = await apiClient.getProducts();
      setProducts(data);
    } catch (err) {
      setError('Failed to load products');
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Loading products...</div>;
  if (error) return <div className="error">{error}</div>;
  
  return (
    <div className="product-list">
      <h2>Products ({products.length})</h2>
      {products.map(product => (
        <div key={product.id} className="product-item">
          <h3>{product.name}</h3>
          <p>{product.description}</p>
          <p className="price">${product.price}</p>
        </div>
      ))}
    </div>
  );
};
```

---

## 🔧 **Environment Configuration**

### **Development Environment**
```typescript
// config/development.ts
export const config = {
  apiBaseURL: 'http://localhost:8000/api/v1',
  environment: 'development',
  debug: true
};
```

### **Production Environment**
```typescript
// config/production.ts
export const config = {
  apiBaseURL: 'https://your-domain.com:8004/api/v1',
  environment: 'production',
  debug: false
};
```

### **Environment Detection**
```typescript
// config/index.ts
const isDevelopment = process.env.NODE_ENV === 'development';

export const config = isDevelopment 
  ? require('./development').config
  : require('./production').config;
```

---

## 🚨 **Error Handling**

### **Global Error Handler**
```typescript
// utils/errorHandler.ts
export const handleAPIError = (error: any) => {
  if (error.status === 401) {
    // Unauthorized - redirect to login
    logout();
    return 'Please log in to continue';
  }
  
  if (error.status === 403) {
    // Forbidden - insufficient permissions
    return 'You do not have permission to perform this action';
  }
  
  if (error.status === 404) {
    // Not found
    return 'The requested resource was not found';
  }
  
  if (error.status >= 500) {
    // Server error
    return 'A server error occurred. Please try again later.';
  }
  
  // Default error message
  return error.message || 'An unexpected error occurred';
};
```

### **Toast Notifications**
```typescript
// components/Toast.tsx
import React from 'react';

interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ message, type, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);
  
  return (
    <div className={`toast toast-${type}`}>
      <span>{message}</span>
      <button onClick={onClose}>&times;</button>
    </div>
  );
};
```

---

## 📱 **Responsive Design Considerations**

### **Mobile-First Approach**
```css
/* Base styles for mobile */
.product-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  padding: 1rem;
}

/* Tablet and up */
@media (min-width: 768px) {
  .product-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    padding: 1.5rem;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .product-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
    padding: 2rem;
  }
}
```

---

## 🧪 **Testing**

### **API Mocking for Tests**
```typescript
// tests/mocks/apiMock.ts
export const mockAPI = {
  auth: {
    login: jest.fn().mockResolvedValue({
      access_token: 'mock-token',
      user: { id: 1, email: 'test@example.com', role: 'tenant_admin' }
    }),
    getCurrentUser: jest.fn().mockResolvedValue({
      id: 1, email: 'test@example.com', role: 'tenant_admin'
    })
  },
  products: {
    getProducts: jest.fn().mockResolvedValue([
      { id: 1, name: 'Test Product', price: 99.99 }
    ])
  }
};

// Mock fetch globally
global.fetch = jest.fn();
```

---

## 📚 **Additional Resources**

- **Full API Documentation**: `API_ENDPOINTS_DOCUMENTATION.md`
- **Database Setup**: `DATABASE_README.md`
- **Deployment Guide**: `DEPLOYMENT_README.md`

---

## 🆘 **Getting Help**

If you encounter issues:

1. **Check the API documentation** for endpoint details
2. **Verify authentication** - ensure tokens are valid
3. **Check network requests** in browser dev tools
4. **Review server logs** for backend errors
5. **Test with cURL** to isolate frontend vs backend issues

---

**Happy Coding! 🎉**

This guide should get you started with integrating your UI with the PIM System API. The system is designed to be simple and RESTful, making it easy to build modern web applications.
