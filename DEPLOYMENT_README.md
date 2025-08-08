# 🚀 PIM System Deployment Guide

## 📋 **Overview**

This guide provides simple deployment scripts for the PIM (Product Information Management) system with **secure, interactive admin user creation**.

## 🎯 **Quick Start**

### **1. Deploy the System**
```bash
# Deploy with interactive admin setup (RECOMMENDED)
./deploy_pim.sh

# Deploy on custom port
./deploy_pim.sh -p 8080
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
- ✅ **Prompts for admin credentials securely**
- ✅ Starts the application
- ✅ Tests the deployment
- ✅ Displays credentials

### **stop_pim.sh**
Stop script that:
- ✅ Stops the application
- ✅ Cleans up processes
- ✅ Removes PID files

## 🔐 **Secure Admin Setup**

### **Interactive Credential Prompting**
The deployment script now **securely prompts** for admin credentials during deployment:

1. **Email Prompt**: 
   - Default: `admin@pim.com`
   - Can be customized during deployment
   - Validates email format

2. **Password Prompt**:
   - **Hidden input** (password not displayed)
   - **Confirmation required** (type twice)
   - **Minimum 6 characters**
   - **Secure validation**

### **Security Features**
- ✅ **No hardcoded passwords** in scripts or documentation
- ✅ **Hidden password input** during prompting
- ✅ **Password confirmation** to prevent typos
- ✅ **Email validation** for proper format
- ✅ **Minimum password length** enforcement
- ✅ **Credentials only displayed once** at the end

## 🎨 **Features**

### **Automatic Setup**
- **Virtual Environment**: Creates and activates Python virtual environment
- **Dependencies**: Installs all required Python packages
- **Database**: Runs migrations and sets up database schema
- **Admin User**: **Securely creates admin user with custom credentials**

### **Smart Deployment**
- **Port Management**: Checks and frees up ports if needed
- **Process Management**: Handles existing processes gracefully
- **Error Handling**: Comprehensive error checking and reporting
- **Testing**: Automatically tests the deployment

### **User-Friendly**
- **Colored Output**: Easy-to-read colored console output
- **Progress Tracking**: Shows progress for each step
- **Secure Credential Input**: Hidden password prompting
- **Help System**: Built-in help and usage information

## 🔑 **Admin Credentials**

After deployment, you'll see your custom credentials:

```
🔑 ADMIN CREDENTIALS
Email: [your-custom-email]
Password: [your-custom-password]
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

### **Basic Deployment (Interactive)**
```bash
./deploy_pim.sh
```
*This will prompt for admin email and password during deployment*

### **Custom Port**
```bash
./deploy_pim.sh -p 8080
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
2. **Admin Credentials**: **Securely prompts for admin email and password**
3. **Port Check**: Ensures port is available
4. **Virtual Environment**: Creates Python virtual environment
5. **Dependencies**: Installs required packages
6. **Database Setup**: Runs migrations and creates tables
7. **Admin User**: Creates admin user with custom credentials
8. **Application Start**: Starts the FastAPI application
9. **Testing**: Tests health check and admin login
10. **Summary**: Displays all important information

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
Email: [your-custom-email]
Password: [your-custom-password]
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

## 🔐 **Security Notes**

- **No hardcoded credentials**: All credentials are prompted during deployment
- **Secure input**: Passwords are hidden during input
- **Validation**: Email format and password strength are validated
- **Confirmation**: Password must be entered twice to confirm
- **Temporary display**: Credentials are only shown once at the end

## 🆘 **Support**

If you encounter issues:

1. **Check logs**: `tail -f pim.log`
2. **Verify prerequisites**: Ensure Python 3.8+ is installed
3. **Check ports**: Ensure port 8004 is available
4. **Restart**: Run `./stop_pim.sh && ./deploy_pim.sh`

---

**🎯 Your PIM system is now ready for production use with secure credential management!** 