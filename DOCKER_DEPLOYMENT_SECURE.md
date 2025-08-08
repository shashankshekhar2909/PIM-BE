# 🔐 Secure PIM System Docker Deployment

## 🎯 **Overview**

This guide provides **secure, Docker-based deployment** for the PIM system with **interactive admin credential setup**.

## 🚀 **Quick Start**

### **1. Deploy with Secure Credentials**
```bash
# Deploy with interactive admin setup (RECOMMENDED)
./deploy_docker.sh

# Or use the existing redeploy script
./redeploy.sh
```

### **2. Stop the System**
```bash
docker compose down
```

## 🔐 **Secure Admin Setup**

### **Interactive Credential Prompting**
Both deployment scripts now **securely prompt** for admin credentials during deployment:

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

## 🎨 **Deployment Scripts**

### **deploy_docker.sh** (NEW)
**Standalone Docker deployment script** that:
- ✅ Checks Docker prerequisites
- ✅ **Prompts for admin credentials securely**
- ✅ Sets up environment and database
- ✅ Builds and starts containers
- ✅ Waits for service readiness
- ✅ Creates admin user
- ✅ Displays deployment summary

### **redeploy.sh** (UPDATED)
**Comprehensive redeployment script** that:
- ✅ Handles multi-service Docker environment
- ✅ **Prompts for admin credentials securely**
- ✅ Updates docker-compose.yml
- ✅ Manages database permissions
- ✅ Builds and starts containers
- ✅ Creates admin user
- ✅ Displays deployment summary

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

- **Database**: `./db/pim.db` - SQLite database
- **Logs**: `docker compose logs pim -f` - Application logs
- **Compose**: `docker-compose.yml` - Docker Compose configuration
- **Environment**: `.env` - Environment variables

## 🚀 **Usage Examples**

### **Basic Docker Deployment (Interactive)**
```bash
$ ./deploy_docker.sh

================================
  PIM SYSTEM DOCKER DEPLOYMENT
================================
[INFO] Checking prerequisites...
[SUCCESS] Docker is running
[SUCCESS] Docker Compose is available

================================
  ADMIN USER SETUP
================================
Please provide admin user credentials:

Admin email (default: admin@pim.com): admin@mycompany.com
Admin password: [hidden input]
Confirm password: [hidden input]

[SUCCESS] Admin credentials set:
Email: admin@mycompany.com
Password: ********

[INFO] Setting up environment...
[SUCCESS] .env file exists
[INFO] Building and starting containers...
[SUCCESS] Containers built and started
[INFO] Waiting for service to be ready...
[SUCCESS] PIM service is ready!
[INFO] Creating admin user...
[SUCCESS] Admin user created successfully!

================================
  DEPLOYMENT SUMMARY
================================
🎯 Project: PIM System
🌐 URL: http://localhost:8004
📊 Health Check: http://localhost:8004/health
📚 API Docs: http://localhost:8004/docs

🔑 ADMIN CREDENTIALS
Email: admin@mycompany.com
Password: MySecurePassword123
Role: superadmin

📁 IMPORTANT FILES
Database: ./db/pim.db
Logs: docker compose logs pim -f
Compose: docker-compose.yml

🚀 USEFUL COMMANDS
Stop application: docker compose down
View logs: docker compose logs pim -f
Restart: ./deploy_docker.sh

================================
✅ PIM System deployed successfully!
================================
```

### **Multi-Service Deployment**
```bash
$ ./redeploy.sh

================================
  PIM SYSTEM DEPLOYMENT
================================
[INFO] Checking prerequisites...
[SUCCESS] Docker is running
[SUCCESS] Docker Compose is available

================================
  ADMIN USER SETUP
================================
Please provide admin user credentials:

Admin email (default: admin@pim.com): admin@mycompany.com
Admin password: [hidden input]
Confirm password: [hidden input]

[SUCCESS] Admin credentials set:
Email: admin@mycompany.com
Password: ********

[INFO] Setting up environment variables...
[SUCCESS] .env file exists
[INFO] Setting up database directory...
[SUCCESS] Database directory created
[INFO] Updating docker-compose.yml...
[SUCCESS] Updated docker-compose.yml with db mount
[INFO] Building and starting containers...
[SUCCESS] Containers built and started
[INFO] Waiting for service to be ready...
[SUCCESS] PIM service is ready!
[INFO] Creating admin user...
[SUCCESS] Admin user created successfully!

================================
  DEPLOYMENT SUMMARY
================================
🎯 Project: PIM System
🌐 URL: http://localhost:8004
📊 Health Check: http://localhost:8004/health
📚 API Docs: http://localhost:8004/docs

🔑 ADMIN CREDENTIALS
Email: admin@mycompany.com
Password: MySecurePassword123
Role: superadmin

📁 IMPORTANT FILES
Database: ./fastAPI/PIM-BE/db/pim.db
Logs: docker compose logs pim -f
Compose: ../../docker-compose.yml

🚀 USEFUL COMMANDS
Stop application: docker compose down
View logs: docker compose logs pim -f
Restart: ./redeploy.sh

================================
✅ PIM System deployed successfully!
================================
```

## 🔄 **Management Commands**

### **Start Application**
```bash
# Standalone deployment
./deploy_docker.sh

# Multi-service deployment
./redeploy.sh
```

### **Stop Application**
```bash
# Stop all services
docker compose down

# Stop only PIM service
docker compose stop pim
```

### **View Logs**
```bash
# View PIM logs
docker compose logs pim -f

# View all service logs
docker compose logs -f
```

### **Restart Application**
```bash
# Restart with secure credentials
./deploy_docker.sh

# Restart multi-service
./redeploy.sh
```

## ⚠️ **Prerequisites**

- **Docker**: Running Docker daemon
- **Docker Compose**: Docker Compose v2+
- **curl**: For health checks (usually pre-installed)

## 🎯 **Deployment Steps**

### **deploy_docker.sh**
1. **Prerequisites Check**: Verifies Docker and Docker Compose
2. **Admin Credentials**: **Securely prompts for admin email and password**
3. **Environment Setup**: Creates db directory and .env file
4. **Container Build**: Builds and starts containers
5. **Service Wait**: Waits for service to be ready
6. **Admin User**: Creates admin user with custom credentials
7. **Summary**: Displays all important information

### **redeploy.sh**
1. **Prerequisites Check**: Verifies Docker and Docker Compose
2. **Admin Credentials**: **Securely prompts for admin email and password**
3. **Environment Setup**: Creates .env file and db directory
4. **Compose Update**: Updates docker-compose.yml with db mount
5. **Container Build**: Builds and starts containers
6. **Service Wait**: Waits for service to be ready
7. **Admin User**: Creates admin user with custom credentials
8. **Summary**: Displays all important information

## 🔍 **Troubleshooting**

### **Docker Issues**
```bash
# Check Docker status
docker info

# Check Docker Compose
docker compose version

# Check running containers
docker compose ps
```

### **Service Issues**
```bash
# Check service logs
docker compose logs pim -f

# Check service health
curl http://localhost:8004/health

# Restart service
docker compose restart pim
```

### **Database Issues**
```bash
# Check database permissions
ls -la db/

# Fix database permissions
chmod 777 db/
chmod 777 db/pim.db

# Recreate database
rm -f db/pim.db
./deploy_docker.sh
```

## 📊 **Security Comparison**

| Feature | Before | After |
|---------|--------|-------|
| **Credentials** | Hardcoded in scripts | Prompted during deployment |
| **Password Input** | Visible during typing | Hidden input |
| **Validation** | No validation | Email format + password strength |
| **Confirmation** | Single entry | Double confirmation |
| **Documentation** | Credentials in docs | No credentials in docs |
| **Security** | Low | High |

## 🎉 **Key Benefits**

- **🔐 Secure**: No hardcoded credentials anywhere
- **🛡️ Protected**: Hidden password input during typing
- **✅ Validated**: Email format and password strength validation
- **🔄 Confirmed**: Password confirmation to prevent typos
- **📝 Clean**: No credentials in documentation
- **🚀 User-friendly**: Interactive and easy to use
- **🎯 Production-ready**: Secure for production deployments
- **🐳 Docker-native**: Full Docker integration

## 🚀 **Ready for Production**

Your PIM system now has:
1. ✅ **Secure credential management**
2. ✅ **Interactive admin setup**
3. ✅ **No hardcoded passwords**
4. ✅ **Production-ready security**
5. ✅ **User-friendly deployment**
6. ✅ **Docker-native architecture**

**🎯 To deploy securely:**
1. Run `./deploy_docker.sh` or `./redeploy.sh`
2. Enter your custom admin credentials when prompted
3. Note the credentials displayed at the end
4. Access the system at http://localhost:8004

---

**🔐 Your PIM system now has enterprise-grade security for credential management with Docker!** 