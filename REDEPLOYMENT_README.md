# 🚀 PIM Application Redeployment

This directory contains a single comprehensive redeployment script that handles the complete deployment of the PIM application.

## 📁 Files

- **`redeploy.sh`** - Comprehensive redeployment script (the only script you need!)

## 🎯 Quick Start

### Prerequisites

1. **Docker** - Must be running
2. **Docker Compose** - Must be installed
3. **Parent directory** - Must contain `docker-compose.yml`

### Deploy the Application

```bash
# From PIM-BE directory
./redeploy.sh
```

## 🔧 What the Script Does

The `redeploy.sh` script performs the following steps automatically:

### ✅ Step 1: Prerequisites Check
- Verifies Docker is running
- Checks Docker Compose is available
- Confirms docker-compose.yml exists

### ✅ Step 2: Environment Setup
- Creates/updates `.env` file with Supabase configuration
- Sets up database URL and secret key

### ✅ Step 3: Database Setup
- Creates `db/` directory with proper permissions (777)
- Moves existing database to `db/pim.db`
- Sets correct permissions for database file

### ✅ Step 4: Docker Configuration
- Updates `docker-compose.yml` with db mount
- Creates backup of original docker-compose.yml
- Configures PIM service with proper volumes

### ✅ Step 5: Container Management
- Stops and removes existing containers
- Builds new containers with latest code
- Starts all services

### ✅ Step 6: Health Check
- Waits for service to be ready (up to 3.5 minutes)
- Verifies health endpoint is responding
- Tests authentication functionality

### ✅ Step 7: Final Status
- Displays service URLs
- Shows database location
- Provides deployment summary

## 🌐 Service URLs

After successful deployment:

- **PIM API**: http://localhost:8004
- **API Documentation**: http://localhost:8004/docs
- **Health Check**: http://localhost:8004/health

## 📁 Database Location

- **Database file**: `./fastAPI/PIM-BE/db/pim.db`
- **Permissions**: 777 (readable/writable by all)
- **Persistence**: Survives container restarts

## 🔐 Environment Variables

The script creates/updates these environment variables:

```bash
# Supabase Configuration
SUPABASE_URL=https://hhxuxthwvpeplhtprnhf.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Application Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./db/pim.db
```

## 🎯 Expected Results

After running `./redeploy.sh`:

- ✅ **Environment variables**: Configured
- ✅ **Database directory**: Created (db/)
- ✅ **Database permissions**: Fixed (777)
- ✅ **Docker-compose.yml**: Updated with db mount
- ✅ **Containers**: Built and started
- ✅ **Service**: Running and healthy
- ✅ **Health endpoint**: Working
- ✅ **Authentication**: Working (may need email confirmation)

## 🔍 Troubleshooting

### Service Not Starting
```bash
# Check logs
docker compose logs pim -f

# Check if containers are running
docker compose ps
```

### Database Issues
```bash
# Check database permissions
ls -la db/pim.db

# Check if db directory exists
ls -la db/
```

### Authentication Issues
```bash
# Test health endpoint
curl http://localhost:8004/health

# Test signup
curl -X POST http://localhost:8004/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","company_name":"Test Company"}'
```

## 🎉 Success!

Once you see:
- ✅ PIM service status: "Up"
- ✅ Health check: `{"status": "healthy"}`
- ✅ API docs: http://localhost:8004/docs loads

**Your PIM application is successfully deployed and ready to use!** 🚀 