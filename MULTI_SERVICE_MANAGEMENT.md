# Multi-Service Docker Management Guide

This guide covers how to manage the PIM system when `docker-compose.yml` is located in a parent directory (multi-service setup).

## 🏗️ Directory Structure

```
your-project/
├── docker-compose.yml          # Main compose file (parent directory)
├── .env                        # Environment variables (parent directory)
├── fastAPI/
│   ├── app1/
│   ├── app2/
│   ├── giftg-BE/
│   └── PIM-BE/                 # Your current directory
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── app/
│       ├── pim.db
│       ├── manage-docker.sh    # Management script
│       └── ...
```

## 🚀 Quick Start

### 1. From PIM-BE Directory

```bash
# Make sure you're in the PIM-BE directory
cd fastAPI/PIM-BE

# Check if you're in the right place
ls -la
# Should show: Dockerfile, app/, requirements.txt, etc.

# Use the management script
./manage-docker.sh help
```

### 2. Environment Setup

The script will automatically create a `.env` template in the parent directory if it doesn't exist:

```bash
# The script will create this automatically
./manage-docker.sh up-pim
```

## 🔧 Management Commands

### Service Management

```bash
# Start only PIM service
./manage-docker.sh up-pim

# Start all services
./manage-docker.sh up

# Stop all services
./manage-docker.sh down

# Restart only PIM service
./manage-docker.sh restart-pim

# Restart all services
./manage-docker.sh restart
```

### Building Services

```bash
# Build only PIM service
./manage-docker.sh build-pim

# Build all services
./manage-docker.sh build
```

### Monitoring and Debugging

```bash
# Check PIM service health
./manage-docker.sh health

# View PIM service logs
./manage-docker.sh logs-pim

# View all service logs
./manage-docker.sh logs

# Show service status
./manage-docker.sh status

# Enter PIM container shell
./manage-docker.sh shell
```

### Cleanup

```bash
# Remove orphan containers (fixes the orphan container warning)
./manage-docker.sh clean
```

## 🌐 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| App1 | http://localhost:8001 | First application |
| App2 | http://localhost:8002 | Second application |
| GiftG | http://localhost:8003 | GiftG backend |
| **PIM** | **http://localhost:8004** | **PIM system** |
| **PIM Docs** | **http://localhost:8004/docs** | **API documentation** |
| **PIM Health** | **http://localhost:8004/health** | **Health check** |

## 🔍 Health Checks

### Check PIM Service Health
```bash
# Using the management script
./manage-docker.sh health

# Expected response
{
  "status": "healthy",
  "service": "Multi-Tenant PIM System",
  "version": "1.0.0"
}
```

### Manual Health Check
```bash
# Using curl
curl http://localhost:8004/health
```

## 🐛 Troubleshooting

### Common Issues

1. **Script not found**
   ```bash
   # Make sure you're in the PIM-BE directory
   pwd
   # Should show: .../fastAPI/PIM-BE
   
   # Make script executable
   chmod +x manage-docker.sh
   ```

2. **docker-compose.yml not found**
   ```bash
   # Check if docker-compose.yml exists in parent directories
   ls -la ../docker-compose.yml
   ls -la ../../docker-compose.yml
   ```

3. **Environment variables not set**
   ```bash
   # The script will create .env template automatically
   ./manage-docker.sh up-pim
   
   # Then edit the .env file in the parent directory
   nano ../.env  # or ../../.env
   ```

4. **Orphan containers warning**
   ```bash
   # Clean up orphan containers
   ./manage-docker.sh clean
   ```

5. **Port conflicts**
   ```bash
   # Check if port 8004 is in use
   lsof -i :8004
   
   # Stop all services and restart
   ./manage-docker.sh down
   ./manage-docker.sh up-pim
   ```

### Debug Commands

```bash
# Check current directory
pwd

# List files in current directory
ls -la

# Check if docker-compose.yml exists in parent
find .. -name "docker-compose.yml" -type f

# Check environment variables
./manage-docker.sh shell
env | grep SUPABASE
exit
```

## 📊 Monitoring

### Service Status
```bash
# View all services
./manage-docker.sh status

# Check specific service
docker ps | grep pim
```

### Logs
```bash
# View PIM logs
./manage-docker.sh logs-pim

# Follow logs in real-time
./manage-docker.sh logs-pim | tail -f
```

## 🔄 Updates

### Update PIM Service
```bash
# Pull latest changes
git pull

# Rebuild and restart PIM service
./manage-docker.sh build-pim
./manage-docker.sh restart-pim
```

### Update All Services
```bash
# Stop all services
./manage-docker.sh down

# Rebuild all services
./manage-docker.sh build

# Start all services
./manage-docker.sh up
```

## 🎯 Quick Reference

### Essential Commands
```bash
# Start PIM service
./manage-docker.sh up-pim

# Check health
./manage-docker.sh health

# View logs
./manage-docker.sh logs-pim

# Restart PIM
./manage-docker.sh restart-pim

# Stop everything
./manage-docker.sh down
```

### Development Workflow
```bash
# 1. Start PIM service
./manage-docker.sh up-pim

# 2. Check health
./manage-docker.sh health

# 3. View logs (if needed)
./manage-docker.sh logs-pim

# 4. Make code changes (hot reload enabled)

# 5. Restart if needed
./manage-docker.sh restart-pim
```

## 📝 Notes

- **Hot Reload**: Services use `--reload` flag for development
- **Volume Mounting**: Code is mounted as volumes for instant updates
- **Environment Variables**: Loaded from parent directory `.env` file
- **Health Checks**: Built-in monitoring for PIM service
- **Orphan Containers**: Use `./manage-docker.sh clean` to remove them
- **Port Mapping**: Each service runs on a different port
- **Service Isolation**: Each service is independent

## 🆘 Getting Help

```bash
# Show all available commands
./manage-docker.sh help

# Check script version and location
./manage-docker.sh help | head -5
```

## 🎉 Success Indicators

✅ **PIM service is running**: `./manage-docker.sh status` shows "Up" for pim service
✅ **Health check passes**: `./manage-docker.sh health` returns healthy status
✅ **API accessible**: http://localhost:8004/docs loads successfully
✅ **No warnings**: No orphan container or environment variable warnings 