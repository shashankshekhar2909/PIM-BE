# 🚀 PIM System - Product Information Management

A **secure, multi-tenant Product Information Management (PIM) system** built with FastAPI, Docker, and AI-powered features.

## 🎯 **Quick Start**

### **Deploy the System**
```bash
# This is the ONLY command you need to run
./deploy.sh
```

The script will:
- ✅ **Securely prompt** for admin credentials
- ✅ **Auto-detect** your environment (standalone or multi-service)
- ✅ **Setup** database and environment
- ✅ **Build and start** containers
- ✅ **Create** admin user
- ✅ **Display** all important information

### **Stop the System**
```bash
docker compose down
```

## 🔐 **Authentication & User Management**

### **Hybrid Authentication System**
- **Local Authentication**: Superadmin users with local password hashing
- **Supabase Authentication**: Regular users with Supabase integration
- **Automatic User Sync**: Users from Supabase are automatically created in local database

### **User Types**
1. **Superadmin**: Full system access, local authentication
2. **Analyst**: View-only access to all data
3. **Tenant Admin**: Manage tenant-specific users and data
4. **Tenant User**: Standard user with tenant-scoped access

### **Supabase Integration**
- ✅ **Automatic User Creation**: Users existing in Supabase are automatically created in local database
- ✅ **Seamless Login**: No manual intervention required for Supabase users
- ✅ **Default Tenant**: New users get assigned to "Default Company" tenant
- ✅ **Backward Compatibility**: Existing local users continue to work

### **Login Flow**
1. **Check Local Database**: First checks if user exists locally
2. **Supabase Authentication**: If not found locally, tries Supabase authentication
3. **Auto-Create User**: If Supabase authentication succeeds, creates user locally
4. **Return Token**: Provides access token for API access

### **Testing Supabase Login**
```bash
# Test script for Supabase users
python3 test_supabase_fix.py
```

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

## 🎨 **Key Features**

### **Core PIM Features**
- **Product Management**: CRUD operations for products
- **Category Management**: Hierarchical category structure
- **Tenant Isolation**: Multi-tenant data separation
- **Field Configuration**: Configurable searchable/editable fields
- **AI-Powered Upload**: Intelligent CSV/Excel processing
- **Search & Filter**: Advanced search with field-specific queries

### **User Management**
- **Superadmin**: Full system access and user management
- **Analyst**: View-only access to all data
- **Tenant Admin**: Manage tenant-specific users and data
- **Tenant User**: Standard user with tenant-scoped access

### **Security Features**
- **Hybrid Authentication**: Local (superadmin) + Supabase (users)
- **Role-Based Access Control**: Granular permissions
- **Audit Logging**: Complete action tracking
- **Secure Credentials**: Interactive setup with validation

### **Technical Features**
- **Docker Support**: Full containerization
- **Multi-Service**: Integrates with existing Docker environments
- **Database**: SQLite with automatic migrations
- **API**: RESTful FastAPI with automatic documentation
- **Health Checks**: Built-in monitoring endpoints

## 🐛 **Recent Fixes**

### **AI Analysis Error** ✅ **FIXED**
- **Problem**: AI service was failing to parse JSON responses and showing warnings
- **Solution**: Improved error handling and robust fallback analysis
- **Result**: Graceful fallback when AI is unavailable, cleaner logs

### **Supabase Login Issue** ✅ **FIXED**
- **Problem**: Users existing in Supabase but not in local database couldn't login
- **Solution**: Automatic user creation from Supabase during login
- **Result**: Seamless login experience for all Supabase users

### **Pydantic Warnings** ✅ **FIXED**
- **Problem**: Field name conflicts with Pydantic BaseModel
- **Solution**: Renamed conflicting fields and used aliases
- **Result**: Clean application logs with no warnings

## 📁 **Project Structure**

```
pim-be/
├── deploy.sh                 # 🎯 MAIN DEPLOYMENT SCRIPT
├── cleanup.sh               # 🧹 Cleanup script (optional)
├── README.md                # 📚 This documentation
├── docker-compose.yml       # 🐳 Docker Compose configuration
├── Dockerfile              # 🐳 Docker image definition
├── requirements.txt        # 📦 Python dependencies
├── .env                    # 🔧 Environment variables
├── db/                     # 💾 Database directory
│   └── pim.db             # SQLite database
├── app/                    # 🏗️ Application code
│   ├── api/               # 🌐 API endpoints
│   ├── core/              # 🔧 Core functionality
│   ├── models/            # 🗄️ Database models
│   ├── schemas/           # 📋 Pydantic schemas
│   └── utils/             # 🛠️ Utility functions
└── sample_data/           # 📊 Sample data files
```

## 🚀 **Deployment Options**

### **After Code Updates - How to Deploy**

#### **Option 1: Full Redeploy (Recommended for Major Changes)**
```bash
# This is the complete deployment script - use for major changes
./deploy.sh
```
**When to use:**
- ✅ New features added
- ✅ Database schema changes
- ✅ New dependencies added
- ✅ Major code refactoring
- ✅ First-time deployment

#### **Option 2: Quick Redeploy (For Minor Changes)**
```bash
# Stop containers
docker compose down

# Rebuild and start (faster than full deploy)
docker compose up --build -d

# Check status
docker compose ps
```
**When to use:**
- ✅ Bug fixes
- ✅ Minor code changes
- ✅ Configuration updates
- ✅ When you want to skip admin setup

#### **Option 3: Hot Reload (For Development)**
```bash
# If you're in development mode with volume mounts
docker compose restart pim
```
**When to use:**
- ✅ Code changes only (no new dependencies)
- ✅ Development environment
- ✅ When using volume mounts for live code updates

#### **Option 4: Service-Specific Update**
```bash
# Update only the PIM service
docker compose up --build -d pim

# Check logs
docker compose logs pim -f
```
**When to use:**
- ✅ Only PIM service changes
- ✅ Other services are working fine
- ✅ Quick testing of changes

### **Deployment Checklist**

#### **Before Deploying**
1. ✅ **Code committed** to version control
2. ✅ **Tests passed** (if applicable)
3. ✅ **Dependencies updated** (if needed)
4. ✅ **Environment variables** configured
5. ✅ **Database backups** (for production)

#### **After Deploying**
1. ✅ **Health check** - `curl http://localhost:8004/health`
2. ✅ **Service status** - `docker compose ps`
3. ✅ **Logs check** - `docker compose logs pim -f`
4. ✅ **API test** - Test a few endpoints
5. ✅ **User login** - Verify authentication works

### **Troubleshooting Deployment**

#### **Common Issues**
```bash
# If containers won't start
docker compose down -v
docker compose up --build -d

# If database issues
docker compose down
rm -rf db/pim.db  # WARNING: This deletes all data
./deploy.sh

# If port conflicts
docker compose down
# Check what's using port 8004
lsof -i :8004
# Kill conflicting process or change port in docker-compose.yml
```

#### **Logs and Debugging**
```bash
# View real-time logs
docker compose logs pim -f

# View specific service logs
docker compose logs pim --tail=100

# Check container status
docker compose ps

# Enter container for debugging
docker compose exec pim bash
```

### **Production Deployment**

#### **For Production Environment**
```bash
# 1. Backup current deployment
docker compose down
cp -r db db_backup_$(date +%Y%m%d_%H%M%S)

# 2. Pull latest code
git pull origin main

# 3. Full redeploy
./deploy.sh

# 4. Verify deployment
curl http://localhost:8004/health
docker compose ps
```

#### **Rollback Plan**
```bash
# If deployment fails, rollback
docker compose down
git checkout HEAD~1  # Go back one commit
./deploy.sh
```

## ⚠️ **Prerequisites**

- **Docker**: Running Docker daemon
- **Docker Compose**: Docker Compose v2+
- **curl**: For health checks (usually pre-installed)

## 🎯 **Deployment Steps**

1. **Prerequisites Check**: Verifies Docker and Docker Compose
2. **Admin Credentials**: **Securely prompts for admin email and password**
3. **Environment Setup**: Creates db directory and .env file
4. **Environment Detection**: Auto-detects standalone or multi-service
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
./deploy.sh
```

## 📊 **API Endpoints**

### **Authentication**
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/signup` - User registration
- `GET /api/v1/auth/me` - Get current user

### **Products**
- `GET /api/v1/products` - List products
- `POST /api/v1/products` - Create product
- `GET /api/v1/products/{id}` - Get product details
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `POST /api/v1/products/upload/analyze` - Analyze product file
- `POST /api/v1/products/upload` - Upload products

### **Categories**
- `GET /api/v1/categories` - List categories
- `POST /api/v1/categories` - Create category
- `GET /api/v1/categories/{id}` - Get category details
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Delete category

### **Search**
- `GET /api/v1/search` - Search products
- `GET /api/v1/products/fields/configuration` - Get field configuration
- `PUT /api/v1/products/fields/configuration` - Update field configuration

### **Superadmin**
- `GET /api/v1/superadmin/dashboard` - Superadmin dashboard
- `GET /api/v1/superadmin/users` - List all users
- `POST /api/v1/superadmin/users` - Create user
- `PUT /api/v1/superadmin/users/{id}` - Update user
- `POST /api/v1/superadmin/users/{id}/block` - Block user
- `POST /api/v1/superadmin/users/{id}/unblock` - Unblock user

## 🎉 **Key Benefits**

- **🔐 Secure**: No hardcoded credentials anywhere
- **🛡️ Protected**: Hidden password input during typing
- **✅ Validated**: Email format and password strength validation
- **🔄 Confirmed**: Password confirmation to prevent typos
- **📝 Clean**: No credentials in documentation
- **🚀 User-friendly**: Interactive and easy to use
- **🎯 Production-ready**: Secure for production deployments
- **🐳 Docker-native**: Full Docker integration
- **🤖 AI-powered**: Intelligent data processing
- **👥 Multi-tenant**: Complete tenant isolation

## 🚀 **Ready for Production**

Your PIM system now has:
1. ✅ **Secure credential management**
2. ✅ **Interactive admin setup**
3. ✅ **No hardcoded passwords**
4. ✅ **Production-ready security**
5. ✅ **User-friendly deployment**
6. ✅ **Docker-native architecture**
7. ✅ **AI-powered features**
8. ✅ **Multi-tenant support**

**🎯 To deploy securely:**
1. Run `./deploy.sh`
2. Enter your custom admin credentials when prompted
3. Note the credentials displayed at the end
4. Access the system at http://localhost:8004

---

**🔐 Your PIM system now has enterprise-grade security for credential management with Docker!** 