# 🚀 PIM System Deployment Guide

## 📋 **Overview**

This guide provides simple deployment scripts for the PIM (Product Information Management) system with automatic admin user creation.

## 🎯 **Quick Start**

### **1. Deploy the System**
```bash
# Deploy with default settings
./deploy_pim.sh

# Deploy on custom port
./deploy_pim.sh -p 8080

# Deploy with custom admin credentials
./deploy_pim.sh -e admin@mycompany.com -w mypassword
```

### **2. Stop the System**
```bash
./stop_pim.sh
```

## 🔧 **Scripts**

### **deploy_pim.sh**
Main deployment script that:
- ✅ Creates virtual environment
- ✅ Installs dependencies
- ✅ Sets up database
- ✅ Creates default admin user
- ✅ Starts the application
- ✅ Tests the deployment
- ✅ Displays credentials

### **stop_pim.sh**
Stop script that:
- ✅ Stops the application
- ✅ Cleans up processes
- ✅ Removes PID files

## 🎨 **Features**

### **Automatic Setup**
- **Virtual Environment**: Creates and activates Python virtual environment
- **Dependencies**: Installs all required Python packages
- **Database**: Runs migrations and sets up database schema
- **Admin User**: Creates default superadmin user automatically

### **Smart Deployment**
- **Port Management**: Checks and frees up ports if needed
- **Process Management**: Handles existing processes gracefully
- **Error Handling**: Comprehensive error checking and reporting
- **Testing**: Automatically tests the deployment

### **User-Friendly**
- **Colored Output**: Easy-to-read colored console output
- **Progress Tracking**: Shows progress for each step
- **Credential Display**: Prints admin credentials clearly
- **Help System**: Built-in help and usage information

## 🔑 **Default Credentials**

After deployment, you'll see:

```
🔑 ADMIN CREDENTIALS
Email: admin@pim.com
Password: admin123
Role: superadmin
```

## 🌐 **Access URLs**

- **Application**: http://localhost:8004
- **Health Check**: http://localhost:8004/health
- **API Documentation**: http://localhost:8004/docs
- **Interactive API**: http://localhost:8004/redoc

## 📁 **Important Files**

- **Logs**: `pim.log` - Application logs
- **PID**: `pim.pid` - Process ID file
- **Database**: `pim.db` - SQLite database
- **Virtual Environment**: `venv/` - Python virtual environment

## 🚀 **Usage Examples**

### **Basic Deployment**
```bash
./deploy_pim.sh
```

### **Custom Port**
```bash
./deploy_pim.sh -p 8080
```

### **Custom Admin Credentials**
```bash
./deploy_pim.sh -e admin@mycompany.com -w mypassword
```

### **Help**
```bash
./deploy_pim.sh -h
```

## 🔄 **Management Commands**

### **Start Application**
```bash
./deploy_pim.sh
```

### **Stop Application**
```bash
./stop_pim.sh
```

### **View Logs**
```bash
tail -f pim.log
```

### **Restart Application**
```bash
./stop_pim.sh && ./deploy_pim.sh
```

## ⚠️ **Prerequisites**

- **Python 3.8+**: Required for the application
- **pip**: Python package manager
- **curl**: For testing endpoints
- **lsof**: For port management (usually pre-installed)

## 🎯 **Deployment Steps**

1. **Prerequisites Check**: Verifies Python, pip, and curl
2. **Port Check**: Ensures port is available
3. **Virtual Environment**: Creates Python virtual environment
4. **Dependencies**: Installs required packages
5. **Database Setup**: Runs migrations and creates tables
6. **Admin User**: Creates default superadmin user
7. **Application Start**: Starts the FastAPI application
8. **Testing**: Tests health check and admin login
9. **Summary**: Displays all important information

## 🔍 **Troubleshooting**

### **Port Already in Use**
```bash
# The script will automatically handle this, but you can manually:
sudo lsof -ti:8004 | xargs kill -9
```

### **Permission Issues**
```bash
# Make scripts executable
chmod +x deploy_pim.sh stop_pim.sh
```

### **Python Issues**
```bash
# Ensure Python 3 is installed
python3 --version

# Install pip if needed
sudo apt-get install python3-pip  # Ubuntu/Debian
brew install python3              # macOS
```

### **Database Issues**
```bash
# Remove existing database (if corrupted)
rm -f pim.db

# Re-run deployment
./deploy_pim.sh
```

## 📊 **Monitoring**

### **Check Application Status**
```bash
# Check if application is running
curl http://localhost:8004/health

# Check process
ps aux | grep uvicorn
```

### **View Logs**
```bash
# Real-time logs
tail -f pim.log

# Last 100 lines
tail -n 100 pim.log
```

## 🎉 **Success Indicators**

When deployment is successful, you'll see:

```
================================
  DEPLOYMENT SUMMARY
================================
🎯 Project: PIM System
🌐 URL: http://localhost:8004
📊 Health Check: http://localhost:8004/health
📚 API Docs: http://localhost:8004/docs

🔑 ADMIN CREDENTIALS
Email: admin@pim.com
Password: admin123
Role: superadmin

📁 IMPORTANT FILES
Logs: pim.log
PID: pim.pid
Database: pim.db

🚀 USEFUL COMMANDS
Stop application: ./stop_pim.sh
View logs: tail -f pim.log
Restart: ./deploy_pim.sh

================================
✅ PIM System deployed successfully!
================================
```

## 🆘 **Support**

If you encounter issues:

1. **Check logs**: `tail -f pim.log`
2. **Verify prerequisites**: Ensure Python 3.8+ is installed
3. **Check ports**: Ensure port 8004 is available
4. **Restart**: Run `./stop_pim.sh && ./deploy_pim.sh`

---

**🎯 Your PIM system is now ready for production use!** 