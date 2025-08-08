# 🔐 Superadmin Credentials & Setup

## 🎯 **Authentication Strategy**

### **Hybrid Authentication System**
- **Superadmin**: Local authentication (bcrypt)
- **Regular Users**: Supabase authentication
- **Single Login API**: Works for both types of users

## 🔑 **Default Superadmin Credentials**

### **Login Details**
- **Email**: `admin@pim.com`
- **Password**: `admin123`
- **Role**: `superadmin`
- **Authentication**: Local (bcrypt)
- **Status**: Active, Not Blocked

### **Login API**
```bash
curl -X POST "http://localhost:8004/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@pim.com",
    "password": "admin123"
  }'
```

### **Response**
```json
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

## 🚀 **Superadmin Features**

### **Dashboard**
```bash
curl -X GET "http://localhost:8004/api/v1/superadmin/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **User Management**
```bash
# List all users
curl -X GET "http://localhost:8004/api/v1/superadmin/users" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create user
curl -X POST "http://localhost:8004/api/v1/superadmin/users" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "tenant_user",
    "tenant_id": 1
  }'

# Block user
curl -X POST "http://localhost:8004/api/v1/superadmin/users/11/block" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Violation of terms"}'

# Unblock user
curl -X POST "http://localhost:8004/api/v1/superadmin/users/11/unblock" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Issue resolved"}'
```

### **Tenant Management**
```bash
# List all tenants
curl -X GET "http://localhost:8004/api/v1/superadmin/tenants" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update tenant
curl -X PUT "http://localhost:8004/api/v1/superadmin/tenants/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Updated Company Name",
    "logo_url": "https://example.com/logo.png"
  }'
```

### **Product Management**
```bash
# List all products across tenants
curl -X GET "http://localhost:8004/api/v1/superadmin/products" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Audit Logs**
```bash
# Get audit logs
curl -X GET "http://localhost:8004/api/v1/superadmin/audit-logs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎨 **Key Benefits**

### **Security**
- ✅ Local authentication for superadmin (no external dependencies)
- ✅ Supabase authentication for regular users
- ✅ Role-based access control
- ✅ Audit logging for all actions

### **Flexibility**
- ✅ Single login API works for both authentication types
- ✅ Superadmin can manage all users and tenants
- ✅ Full system control and monitoring

### **Management**
- ✅ User blocking/unblocking
- ✅ Password reset functionality
- ✅ Tenant management
- ✅ Product oversight across all tenants

## ⚠️ **Important Notes**

1. **Change Default Password**: Immediately change the default password after first login
2. **Backup Credentials**: Keep superadmin credentials secure
3. **Audit Trail**: All superadmin actions are logged
4. **Regular Users**: Will use Supabase authentication (requires Supabase setup)

## 🔄 **Next Steps**

1. **Change Password**: Update superadmin password after first login
2. **Create Regular Users**: Use superadmin to create tenant users
3. **Set Up Tenants**: Create and configure tenant organizations
4. **Monitor Activity**: Check audit logs regularly

## 📞 **Support**

For issues or questions:
1. Check authentication logs
2. Verify database connectivity
3. Test password verification
4. Review Supabase configuration (for regular users)

---

**🎉 Superadmin system is fully operational with hybrid authentication!** 