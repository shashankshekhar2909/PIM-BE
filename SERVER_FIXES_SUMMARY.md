# 🚨 SERVER ISSUES & FIXES SUMMARY

## ❌ **Current Issues on Server**

### 1. **JWT Authentication Failures**
- **Error**: `'Settings' object has no attribute 'ALGORITHM'`
- **Symptom**: Users can't authenticate, getting 401 Unauthorized
- **Root Cause**: Missing JWT algorithm configuration in settings

### 2. **Database Read-Only Errors**
- **Error**: `sqlite3.OperationalError: attempt to write a readonly database`
- **Symptom**: Can't create users, tenants, or write data
- **Root Cause**: Docker container using wrong database path/permissions

### 3. **JWT Token Mismatch**
- **Error**: JWT tokens created but validation fails
- **Symptom**: Users get authenticated but then immediately fail on subsequent requests
- **Root Cause**: User ID type mismatch (string vs integer)

## ✅ **Fixes Applied**

### 1. **JWT Configuration Fixed**
```python
# app/core/config.py - ADDED:
ALGORITHM: str = "HS256"  # JWT algorithm
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # JWT token expiration
```

### 2. **JWT Token Creation Fixed**
```python
# app/core/auth_service.py - FIXED:
# Before: data={"sub": str(user.id)}  # String ID
# After:  data={"sub": user.id}        # Integer ID
```

### 3. **Database Path Configuration**
```yaml
# docker-compose.yml - VERIFIED:
environment:
  - DATABASE_URL=${DATABASE_URL:-sqlite:///./data/pim.db}
volumes:
  - pim_db_data:/app/data
```

## 🚀 **How to Fix on Server**

### **Option 1: Run the Fix Script (RECOMMENDED)**
```bash
# On your server:
cd /root/apps/fastAPI/PIM-BE

# Make script executable
chmod +x fix-server-database.sh

# Run the fix
./fix-server-database.sh
```

### **Option 2: Manual Fix Steps**
```bash
# 1. Stop the service
docker compose stop pim

# 2. Fix database location
mkdir -p data
cp pim.db data/pim.db  # if pim.db exists in root
chmod 644 data/pim.db
chmod 755 data

# 3. Remove old database from root
rm -f pim.db

# 4. Rebuild and restart
docker compose build --no-cache pim
docker compose up -d pim

# 5. Verify
curl http://localhost:8004/health
```

### **Option 3: Full Redeployment**
```bash
# Use the root deployment script
sudo ./deploy-server-root.sh
```

## 🔍 **What the Fix Script Does**

1. **✅ Stops the service** to prevent conflicts
2. **✅ Moves database** to `data/pim.db` with correct permissions
3. **✅ Verifies Docker Compose** configuration
4. **✅ Cleans up Docker** resources
5. **✅ Rebuilds service** with `--no-cache` to pick up changes
6. **✅ Restarts service** with new configuration
7. **✅ Tests database access** to confirm fix
8. **✅ Shows status** and troubleshooting info

## 📊 **Expected Results After Fix**

### **Before Fix:**
```
ERROR:root:Supabase authentication failed: 'Settings' object has no attribute 'ALGORITHM'
ERROR:root:Signup error: (sqlite3.OperationalError) attempt to write a readonly database
INFO: 192.168.0.101:59946 - "POST /api/v1/auth/signup HTTP/1.1" 500 Internal Server Error
```

### **After Fix:**
```
INFO: 192.168.0.101:59946 - "POST /api/v1/auth/signup HTTP/1.1" 200 OK
INFO: 192.168.0.101:59946 - "POST /api/v1/auth/login HTTP/1.1" 200 OK
```

## 🧪 **Testing the Fix**

### **1. Health Check**
```bash
curl http://localhost:8004/health
# Should return: {"status": "healthy"}
```

### **2. User Creation**
```bash
curl -X POST "http://localhost:8004/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","company_name":"Test Company"}'
# Should return: {"access_token": "...", "user": {...}}
```

### **3. User Login**
```bash
curl -X POST "http://localhost:8004/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
# Should return: {"access_token": "...", "user": {...}}
```

### **4. Protected Endpoints**
```bash
# Get the token from login response
TOKEN="your_jwt_token_here"

curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8004/api/v1/auth/me"
# Should return user info instead of 401
```

## 🚨 **If Issues Persist**

### **Check Docker Logs**
```bash
docker compose logs pim -f
```

### **Check Database Permissions**
```bash
ls -la data/pim.db
# Should show: -rw-r--r-- (644 permissions)
```

### **Check Volume Mounts**
```bash
docker compose exec pim ls -la /app/data
# Should show the database file
```

### **Check Configuration**
```bash
docker compose exec pim env | grep DATABASE_URL
# Should show: DATABASE_URL=sqlite:///./data/pim.db
```

## 🎯 **Quick Fix Commands**

### **For Immediate Fix:**
```bash
# Stop service
docker compose stop pim

# Fix database
mkdir -p data
[ -f pim.db ] && cp pim.db data/pim.db && rm pim.db
chmod 644 data/pim.db

# Restart
docker compose up -d pim
```

### **For Complete Fix:**
```bash
./fix-server-database.sh
```

## 📞 **Need Help?**

1. **Run the fix script**: `./fix-server-database.sh`
2. **Check logs**: `docker compose logs pim -f`
3. **Verify database**: `ls -la data/`
4. **Test endpoints**: Use the testing commands above
5. **Full redeploy**: `sudo ./deploy-server-root.sh`

## 🎉 **Success Indicators**

Your fix is successful when you see:
- ✅ Health check returns `{"status": "healthy"}`
- ✅ User signup returns `200 OK` with access token
- ✅ User login returns `200 OK` with access token
- ✅ Protected endpoints return user data instead of `401 Unauthorized`
- ✅ No more "readonly database" errors in logs
- ✅ No more "ALGORITHM" attribute errors in logs
