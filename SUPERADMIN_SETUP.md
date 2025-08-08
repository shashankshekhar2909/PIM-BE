# 👑 Superadmin Setup & Management Guide

## Overview

This guide explains how to set up and manage superadmin users in the PIM system.

## 🚀 Quick Setup

### Option 1: Automatic Setup (Recommended)

The system automatically creates a default superadmin during database migrations:

```bash
# Run migrations (creates default superadmin automatically)
python -m app.core.migrations
```

**Default Credentials:**
- **Email**: `admin@pim.com`
- **Password**: `admin123`

### Option 2: Manual Setup

Use the provided script to create a superadmin:

```bash
# Make script executable (if not already)
chmod +x add_superadmin.sh

# Run the script
./add_superadmin.sh
```

### Option 3: Custom Superadmin

Create a custom superadmin with your own credentials:

```bash
# Create custom superadmin
python3 create_default_superadmin.py --action create-custom \
  --email "your-email@example.com" \
  --password "your-secure-password" \
  --first-name "Your" \
  --last-name "Name"
```

## 🔧 Management Commands

### List All Superadmins

```bash
python3 create_default_superadmin.py --action list
```

### Create Additional Superadmin

```bash
python3 create_default_superadmin.py --action create-custom \
  --email "new-admin@example.com" \
  --password "secure-password123" \
  --first-name "New" \
  --last-name "Admin"
```

## 🎯 Superadmin Features

### Dashboard Access
- **URL**: `/superadmin/dashboard`
- **Features**: System overview, user management, tenant management

### User Management
- **List Users**: `/api/v1/superadmin/users`
- **Create User**: `POST /api/v1/superadmin/users`
- **Update User**: `PUT /api/v1/superadmin/users/{id}`
- **Block User**: `POST /api/v1/superadmin/users/{id}/block`
- **Unblock User**: `POST /api/v1/superadmin/users/{id}/unblock`
- **Reset Password**: `POST /api/v1/superadmin/users/{id}/reset-password`

### Tenant Management
- **List Tenants**: `/api/v1/superadmin/tenants`
- **View Tenant**: `/api/v1/superadmin/tenants/{id}`
- **Update Tenant**: `PUT /api/v1/superadmin/tenants/{id}`

### Product Management
- **List All Products**: `/api/v1/superadmin/products`

### Audit Logs
- **View Logs**: `/api/v1/superadmin/audit-logs`

## 🔐 Security Best Practices

### 1. Change Default Password

**IMPORTANT**: Always change the default password after first login!

```bash
# Login with default credentials
curl -X POST "http://localhost:8004/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@pim.com",
    "password": "admin123"
  }'
```

### 2. Create Additional Superadmins

Don't rely on a single superadmin account:

```bash
# Create backup superadmin
python3 create_default_superadmin.py --action create-custom \
  --email "backup-admin@example.com" \
  --password "secure-backup-password123" \
  --first-name "Backup" \
  --last-name "Admin"
```

### 3. Regular Password Updates

- Change passwords every 90 days
- Use strong passwords (12+ characters, mixed case, numbers, symbols)
- Never share superadmin credentials

### 4. Monitor Audit Logs

Regularly check audit logs for suspicious activity:

```bash
# Get recent audit logs
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8004/api/v1/superadmin/audit-logs?limit=50"
```

## 🎨 UI Access

### Superadmin Dashboard

Once logged in as superadmin, you'll have access to:

1. **System Overview**
   - Total users, tenants, products
   - System statistics
   - Recent activity

2. **User Management**
   - List all users across tenants
   - Create, edit, block/unblock users
   - Reset passwords
   - Assign roles

3. **Tenant Management**
   - View all tenants
   - Manage tenant information
   - Monitor tenant activity

4. **Product Management**
   - View all products across tenants
   - Product analytics
   - Data insights

5. **Audit Logs**
   - Complete system audit trail
   - User action tracking
   - Security monitoring

## 🚨 Troubleshooting

### Superadmin Not Created

If the default superadmin wasn't created during migrations:

```bash
# Check if superadmin exists
python3 create_default_superadmin.py --action list

# If none exists, create one
./add_superadmin.sh
```

### Can't Login

1. **Check if user exists**:
   ```bash
   python3 create_default_superadmin.py --action list
   ```

2. **Verify password**:
   ```bash
   # Try with default password
   curl -X POST "http://localhost:8004/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@pim.com", "password": "admin123"}'
   ```

3. **Reset password if needed**:
   ```bash
   # Use the API to reset password
   curl -X POST "http://localhost:8004/api/v1/superadmin/users/{id}/reset-password" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"new_password": "new-secure-password123"}'
   ```

### Database Issues

If you encounter database issues:

```bash
# Check database connection
python3 -c "
from app.core.config import settings
from sqlalchemy import create_engine
engine = create_engine(settings.DATABASE_URL, connect_args={'check_same_thread': False})
try:
    with engine.connect() as conn:
        result = conn.execute('SELECT COUNT(*) FROM users WHERE role = \"superadmin\"')
        count = result.fetchone()[0]
        print(f'Found {count} superadmin users')
except Exception as e:
    print(f'Database error: {e}')
"
```

## 📊 Monitoring

### Health Checks

Regularly monitor the system:

```bash
# Check system health
curl "http://localhost:8004/health"

# Check superadmin dashboard
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8004/api/v1/superadmin/dashboard"
```

### Log Monitoring

Monitor application logs for issues:

```bash
# View application logs
docker-compose logs -f pim

# Check for errors
docker-compose logs pim | grep -i error
```

## 🔄 Maintenance

### Regular Tasks

1. **Weekly**:
   - Review audit logs
   - Check system health
   - Monitor user activity

2. **Monthly**:
   - Update superadmin passwords
   - Review user permissions
   - Backup system data

3. **Quarterly**:
   - Security audit
   - Performance review
   - System updates

### Backup Strategy

```bash
# Backup database
cp db/pim.db db/pim.db.backup.$(date +%Y%m%d_%H%M%S)

# Backup configuration
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
```

## 🎯 Next Steps

After setting up your superadmin:

1. **Change default password** immediately
2. **Create additional superadmins** for redundancy
3. **Set up monitoring** and alerting
4. **Configure audit logging** preferences
5. **Review security settings**
6. **Train team members** on superadmin features

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review application logs
3. Verify database connectivity
4. Ensure all dependencies are installed
5. Check system requirements

For additional help, refer to the main documentation or contact your system administrator. 