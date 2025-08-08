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

## 🔐 **Secure Admin Setup**

The deployment script **securely prompts** for admin credentials:

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

## 🌐 **Access URLs**

- **Application**: http://localhost:8004
- **Health Check**: http://localhost:8004/health
- **API Documentation**: http://localhost:8004/docs
- **Interactive API**: http://localhost:8004/redoc

## 🔑 **Admin Credentials**

After deployment, you'll see your custom credentials:

```
🔑 ADMIN CREDENTIALS
Email: [your-custom-email]
Password: [your-custom-password]
Role: superadmin
```

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

### **Option 1: Standalone Deployment**
```bash
# In the pim-be directory
./deploy.sh
```

### **Option 2: Multi-Service Deployment**
```bash
# In a multi-service environment
# The script automatically detects and configures
./deploy.sh
```

## 🔄 **Management Commands**

### **Start Application**
```bash
./deploy.sh
```

### **Stop Application**
```bash
docker compose down
```

### **View Logs**
```bash
docker compose logs pim -f
```

### **Restart Application**
```bash
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