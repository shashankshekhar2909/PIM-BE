# 🎯 Superadmin System

## Overview

The PIM system now includes a comprehensive **superadmin structure** with role-based access control, user management, audit logging, and cross-tenant data access.

## 🏗️ Architecture

### User Roles

1. **superadmin** - Full access to all data and functionality
2. **analyst** - View-only access to all data (no editing)
3. **tenant_admin** - Admin access to their own tenant
4. **tenant_user** - Standard user access to their own tenant

### Key Features

- ✅ **User Management**: CRUD operations, block/unblock, reset passwords
- ✅ **Tenant Management**: View all tenants, update tenant information
- ✅ **Product Management**: View all products across tenants
- ✅ **Audit Logging**: Track all user actions with detailed metadata
- ✅ **Dashboard**: Statistics and recent activity overview
- ✅ **Role-Based Access Control**: Granular permissions per role

## 🚀 Quick Start

### 1. Create Superadmin User

```bash
# Create the first superadmin user
curl -X POST "http://localhost:8004/api/v1/superadmin/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "role": "superadmin",
    "first_name": "Super",
    "last_name": "Admin"
  }'
```

### 2. Access Dashboard

```bash
# Get dashboard statistics
curl -X GET "http://localhost:8004/api/v1/superadmin/dashboard"
```

### 3. Manage Users

```bash
# List all users
curl -X GET "http://localhost:8004/api/v1/superadmin/users"

# Create new user
curl -X POST "http://localhost:8004/api/v1/superadmin/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "role": "tenant_user",
    "first_name": "John",
    "last_name": "Doe",
    "tenant_id": 1
  }'

# Block user
curl -X POST "http://localhost:8004/api/v1/superadmin/users/1/block" \
  -H "Content-Type: application/json" \
  -d '"User violated terms of service"'
```

## 📊 API Endpoints

### Dashboard
- `GET /api/v1/superadmin/dashboard` - Get statistics and recent activity

### User Management
- `GET /api/v1/superadmin/users` - List all users
- `GET /api/v1/superadmin/users/{id}` - Get user details
- `POST /api/v1/superadmin/users` - Create new user
- `PUT /api/v1/superadmin/users/{id}` - Update user
- `POST /api/v1/superadmin/users/{id}/block` - Block user
- `POST /api/v1/superadmin/users/{id}/unblock` - Unblock user
- `POST /api/v1/superadmin/users/{id}/reset-password` - Reset password

### Tenant Management
- `GET /api/v1/superadmin/tenants` - List all tenants
- `GET /api/v1/superadmin/tenants/{id}` - Get tenant details
- `PUT /api/v1/superadmin/tenants/{id}` - Update tenant

### Product Management
- `GET /api/v1/superadmin/products` - List all products

### Audit Logs
- `GET /api/v1/superadmin/audit-logs` - Get audit logs

## 🔐 Security Features

### Role-Based Access Control

#### Superadmin Permissions
- ✅ Full access to all data and functionality
- ✅ User management (CRUD, block/unblock, reset passwords)
- ✅ Tenant management (view and update all tenants)
- ✅ Product management (view and manage all products)
- ✅ Audit logs (full access)
- ✅ System administration (dashboard, statistics)

#### Analyst Permissions
- ✅ Read-only access to all data
- ✅ User viewing (no editing)
- ✅ Tenant viewing (no editing)
- ✅ Product viewing (no editing)
- ✅ Audit logs (view only)
- ✅ Dashboard access
- ❌ No editing capabilities

#### Tenant Admin Permissions
- ✅ Full access to their own tenant
- ✅ User management within their tenant
- ✅ Product management within their tenant
- ✅ Category management within their tenant
- ❌ No cross-tenant access

#### Tenant User Permissions
- ✅ Product access within their tenant
- ✅ Category access within their tenant
- ✅ Search within their tenant's data
- ❌ No user management
- ❌ No tenant management

### Audit Logging

All user actions are automatically logged with:
- **User ID**: Who performed the action
- **Action**: What action was performed
- **Resource Type**: What type of resource was affected
- **Resource ID**: Which specific resource was affected
- **Details**: Additional context about the action
- **IP Address**: User's IP address
- **User Agent**: Browser/client information
- **Timestamp**: When the action occurred

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR UNIQUE NOT NULL,
    supabase_user_id VARCHAR,
    password_hash VARCHAR,
    tenant_id INTEGER,
    role VARCHAR NOT NULL DEFAULT 'tenant_user',
    first_name VARCHAR,
    last_name VARCHAR,
    is_active BOOLEAN DEFAULT 1,
    is_blocked BOOLEAN DEFAULT 0,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    notes TEXT,
    FOREIGN KEY (tenant_id) REFERENCES tenants (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);
```

### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action VARCHAR NOT NULL,
    resource_type VARCHAR NOT NULL,
    resource_id INTEGER,
    resource_name VARCHAR,
    details TEXT,
    ip_address VARCHAR,
    user_agent VARCHAR,
    metadata TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## 🧪 Testing

Run the superadmin test script:

```bash
# Test all superadmin functionality
./test-superadmin.sh
```

This will test:
- ✅ Service connectivity
- ✅ Dashboard access
- ✅ User management
- ✅ Tenant management
- ✅ Product management
- ✅ Audit logs
- ✅ User creation (if superadmin)
- ✅ User blocking/unblocking (if superadmin)

## 🔧 Configuration

### Environment Variables

No additional environment variables are required. The superadmin system uses the existing authentication and database configuration.

### Database Migration

The system automatically runs migrations to:
- Add new user fields (first_name, last_name, is_active, is_blocked, etc.)
- Create audit_logs table
- Add necessary indexes for performance

## 📈 Usage Examples

### 1. Create Analyst User
```bash
curl -X POST "http://localhost:8004/api/v1/superadmin/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@example.com",
    "role": "analyst",
    "first_name": "Data",
    "last_name": "Analyst"
  }'
```

### 2. View Recent Activity
```bash
curl -X GET "http://localhost:8004/api/v1/superadmin/audit-logs?limit=10"
```

### 3. Get User Statistics
```bash
curl -X GET "http://localhost:8004/api/v1/superadmin/dashboard" | jq '.users_by_role'
```

### 4. Block Inactive User
```bash
curl -X POST "http://localhost:8004/api/v1/superadmin/users/123/block" \
  -H "Content-Type: application/json" \
  -d '"User inactive for 30 days"'
```

## 🎯 Benefits

1. **Centralized Management**: Single interface to manage all users and tenants
2. **Audit Trail**: Complete tracking of all user actions
3. **Role-Based Security**: Granular permissions based on user roles
4. **Cross-Tenant Visibility**: Superadmin can view all data across tenants
5. **User Control**: Block/unblock users, reset passwords, manage roles
6. **Analytics**: Dashboard with statistics and recent activity
7. **Compliance**: Audit logs for regulatory compliance

## 🚨 Important Notes

1. **Superadmin Creation**: Only existing superadmins can create new superadmins
2. **Self-Protection**: Superadmins cannot change their own role from superadmin
3. **Audit Logging**: All actions are logged automatically
4. **Blocked Users**: Blocked users cannot access the system
5. **Tenant Isolation**: Regular users can only access their own tenant's data
6. **Analyst Role**: Analysts can view but cannot edit any data

## 🔄 Migration from Existing System

The superadmin system is designed to work with existing data:
- Existing users are automatically assigned the `tenant_user` role
- Existing user data is preserved
- New fields are added with default values
- Audit logging starts immediately after deployment

## 📞 Support

For issues or questions about the superadmin system:
1. Check the audit logs for detailed error information
2. Verify user roles and permissions
3. Test with the provided test script
4. Review the API documentation at `/docs` 