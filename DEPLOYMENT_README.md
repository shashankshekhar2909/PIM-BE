# 🚀 PIM System Deployment

## 📁 **Two Simple Deployment Options**

### 1. **Quick Deploy** - `./quick-deploy.sh`
- **Use for**: Quick updates, fixes, restarts
- **What it does**: Stops and starts the service
- **Preserves**: All data, users, configuration
- **Time**: ~30 seconds
- **Command**: `./quick-deploy.sh`

### 2. **Full Deploy** - `./full-deploy.sh`
- **Use for**: Fresh installation, major issues, complete reset
- **What it does**: Rebuilds everything from scratch
- **Preserves**: Database data (with backup)
- **Time**: ~2-3 minutes
- **Command**: `./full-deploy.sh`

## 🎯 **Quick Start**

### **For Existing Setup (Recommended)**
```bash
./quick-deploy.sh
```

### **For Fresh Start or Major Issues**
```bash
./full-deploy.sh
```

## 🔧 **What Each Script Does**

| Feature | Quick Deploy | Full Deploy |
|---------|--------------|--------------|
| Stop Service | ✅ | ✅ |
| Start Service | ✅ | ✅ |
| Database Backup | ❌ | ✅ |
| Database Migration | ❌ | ✅ |
| Fresh Build | ❌ | ✅ |
| Cleanup | ❌ | ✅ |
| Health Test | ✅ | ✅ |
| Database Test | ❌ | ✅ |

## 🚨 **Important Notes**

- **Quick Deploy** preserves all your data and users
- **Full Deploy** creates backups before making changes
- Both scripts work for both standalone and multi-service environments
- Both scripts handle root and non-root users automatically
- **Default admin user** (admin@pim.com / admin123) is automatically created if none exists
- **Always change the default password** after first login!

## 📋 **After Deployment**

Your PIM system will be available at:
- **Application**: http://localhost:8004
- **Health Check**: http://localhost:8004/health
- **API Docs**: http://localhost:8004/docs

## 🔍 **Troubleshooting**

### **If Quick Deploy Fails**
```bash
# Try Full Deploy instead
./full-deploy.sh
```

### **Check Service Status**
```bash
docker compose ps pim
```

### **View Logs**
```bash
docker compose logs pim -f
```

### **Restart Service**
```bash
docker compose restart pim
```

## 🎉 **That's It!**

Just two scripts for all your deployment needs:
- **`./quick-deploy.sh`** - Fast and safe
- **`./full-deploy.sh`** - Complete and thorough

Choose the one that fits your situation!
