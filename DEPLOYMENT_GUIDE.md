# PIM System Deployment Guide

This guide shows you exactly how to deploy the PIM system in your existing multi-service environment.

## 🚀 Quick Deployment (3 Steps)

### Step 1: Navigate to PIM-BE Directory
```bash
# Go to your PIM-BE directory
cd fastAPI/PIM-BE

# Verify you're in the right place
ls -la
# Should show: Dockerfile, app/, requirements.txt, manage-docker.sh, etc.
```

### Step 2: Start PIM Service
```bash
# Start only the PIM service (recommended for development)
./manage-docker.sh up-pim

# OR start all services (if you want everything running)
./manage-docker.sh up
```

### Step 3: Verify Deployment
```bash
# Check if PIM service is running
./manage-docker.sh health

# Expected response:
# {
#   "status": "healthy",
#   "service": "Multi-Tenant PIM System",
#   "version": "1.0.0"
# }
```

## 🎯 That's It! Your PIM System is Deployed

### ✅ Success Indicators
- **PIM service running**: http://localhost:8004
- **API documentation**: http://localhost:8004/docs
- **Health check**: http://localhost:8004/health

## 🔧 Alternative Deployment Methods

### Method 1: Using the Management Script (Recommended)
```bash
# From PIM-BE directory
./manage-docker.sh up-pim
```

### Method 2: Using Docker Compose Directly
```bash
# From the parent directory (where docker-compose.yml is located)
cd ../..  # or wherever your docker-compose.yml is

# Start only PIM service
docker-compose up -d pim

# OR start all services
docker-compose up -d
```

### Method 3: Manual Docker Commands
```bash
# Build PIM service
docker-compose build pim

# Start PIM service
docker-compose up -d pim
```

## 🌐 Service URLs After Deployment

| Service | URL | Description |
|---------|-----|-------------|
| App1 | http://localhost:8001 | First application |
| App2 | http://localhost:8002 | Second application |
| GiftG | http://localhost:8003 | GiftG backend |
| **PIM** | **http://localhost:8004** | **PIM system** |
| **PIM Docs** | **http://localhost:8004/docs** | **API documentation** |
| **PIM Health** | **http://localhost:8004/health** | **Health check** |

## 🔍 Monitoring Your Deployment

### Check Service Status
```bash
# Using management script
./manage-docker.sh status

# Using docker-compose directly
docker-compose ps
```

### View Logs
```bash
# View PIM service logs
./manage-docker.sh logs-pim

# Follow logs in real-time
./manage-docker.sh logs-pim | tail -f
```

### Health Check
```bash
# Check PIM service health
./manage-docker.sh health

# Manual health check
curl http://localhost:8004/health
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. "Script not found" Error
```bash
# Make sure you're in the PIM-BE directory
pwd
# Should show: .../fastAPI/PIM-BE

# Make script executable
chmod +x manage-docker.sh
```

#### 2. "docker-compose.yml not found" Error
```bash
# Check if docker-compose.yml exists in parent directories
ls -la ../docker-compose.yml
ls -la ../../docker-compose.yml

# If not found, ensure you're in the right directory structure
```

#### 3. Environment Variables Not Set
```bash
# The script will create .env template automatically
./manage-docker.sh up-pim

# Then edit the .env file in the parent directory
nano ../.env  # or ../../.env
```

#### 4. Port 8004 Already in Use
```bash
# Check what's using port 8004
lsof -i :8004

# Stop conflicting service or change port in docker-compose.yml
```

#### 5. Service Won't Start
```bash
# Check logs for errors
./manage-docker.sh logs-pim

# Check if all dependencies are installed
./manage-docker.sh shell
pip list
exit
```

## 🔄 Daily Development Workflow

### Start Development
```bash
# 1. Start PIM service
./manage-docker.sh up-pim

# 2. Check health
./manage-docker.sh health

# 3. Start coding (hot reload enabled)
```

### During Development
```bash
# View logs if needed
./manage-docker.sh logs-pim

# Restart service if needed
./manage-docker.sh restart-pim
```

### Stop Development
```bash
# Stop PIM service only
./manage-docker.sh down

# OR stop all services
docker-compose down  # from parent directory
```

## 📊 Production Deployment

### For Production
```bash
# 1. Update environment variables in .env file
nano ../.env

# 2. Build and start services
./manage-docker.sh build-pim
./manage-docker.sh up-pim

# 3. Verify deployment
./manage-docker.sh health
```

### Environment Variables for Production
```bash
# Edit .env file in parent directory
SUPABASE_URL=https://your-production-project.supabase.co
SUPABASE_ANON_KEY=your-production-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-production-service-role-key
SECRET_KEY=your-secure-secret-key
DATABASE_URL=sqlite:///./pim.db
```

## 🎯 Quick Reference Commands

### Essential Commands
```bash
# Start PIM service
./manage-docker.sh up-pim

# Stop PIM service
./manage-docker.sh down

# Check health
./manage-docker.sh health

# View logs
./manage-docker.sh logs-pim

# Restart PIM service
./manage-docker.sh restart-pim

# Enter container shell
./manage-docker.sh shell
```

### Service Management
```bash
# Build PIM service
./manage-docker.sh build-pim

# Start all services
./manage-docker.sh up

# Stop all services
./manage-docker.sh down

# Show service status
./manage-docker.sh status
```

## 🎉 Success!

Once you see:
- ✅ PIM service status: "Up" 
- ✅ Health check: `{"status": "healthy"}`
- ✅ API docs: http://localhost:8004/docs loads

**Your PIM system is successfully deployed and ready to use!** 🚀 