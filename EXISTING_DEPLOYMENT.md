# Existing Multi-Service Deployment Guide

This guide covers how to deploy the PIM system in your existing multi-service Docker Compose environment.

## 🏗️ Current Structure

Your existing `docker-compose.yml` structure:
```yaml
version: '3.8'

services:
  app1:
    build: ./fastAPI/app1
    container_name: app1
    volumes:
      - ./fastAPI/app1:/app
    working_dir: /app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8001:8000"

  app2:
    build: ./fastAPI/app2
    container_name: app2
    volumes:
      - ./fastAPI/app2:/app
    working_dir: /app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8002:8000"

  giftg:
    build: ./fastAPI/giftg-BE
    container_name: giftg
    volumes:
      - ./fastAPI/giftg-BE:/app
    working_dir: /app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8003:8000"
    restart: unless-stopped

  pim:
    build: ./fastAPI/PIM-BE
    container_name: pim
    volumes:
      - ./fastAPI/PIM-BE:/app
    working_dir: /app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8004:8000"
    restart: unless-stopped
    environment:
      - PYTHONPATH=/app
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-here}
      - DATABASE_URL=${DATABASE_URL:-sqlite:///./pim.db}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## 🚀 Quick Deployment

### 1. Directory Structure
Ensure your directory structure looks like this:
```
your-project/
├── docker-compose.yml
├── .env
├── deploy.sh
└── fastAPI/
    ├── app1/
    ├── app2/
    ├── giftg-BE/
    └── PIM-BE/          # Your PIM system code
        ├── Dockerfile
        ├── requirements.txt
        ├── app/
        ├── pim.db
        └── ...
```

### 2. Environment Setup
Create or update your `.env` file in the root directory:
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Application Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./pim.db
```

### 3. Deploy All Services
```bash
# Option 1: Use the deployment script
./deploy.sh

# Option 2: Manual deployment
docker-compose build
docker-compose up -d
```

## 🔧 Service Management

### Start Services
```bash
# Start all services
docker-compose up -d

# Start only PIM service
docker-compose up -d pim

# Start with logs
docker-compose up pim
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop only PIM service
docker-compose stop pim
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart only PIM service
docker-compose restart pim
```

### View Logs
```bash
# View all logs
docker-compose logs

# View PIM service logs
docker-compose logs pim

# Follow PIM service logs
docker-compose logs -f pim
```

## 🌐 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| App1 | http://localhost:8001 | First application |
| App2 | http://localhost:8002 | Second application |
| GiftG | http://localhost:8003 | GiftG backend |
| PIM | http://localhost:8004 | PIM system |
| PIM Docs | http://localhost:8004/docs | API documentation |
| PIM Health | http://localhost:8004/health | Health check |

## 🔍 Health Checks

### Check PIM Service Health
```bash
# Using curl
curl http://localhost:8004/health

# Expected response
{
  "status": "healthy",
  "service": "Multi-Tenant PIM System",
  "version": "1.0.0"
}
```

### Check All Services
```bash
# View service status
docker-compose ps

# Check service health
docker-compose exec pim curl -f http://localhost:8000/health
```

## 🐛 Troubleshooting

### Common Issues

1. **PIM service not starting**
   ```bash
   # Check logs
   docker-compose logs pim
   
   # Check if directory exists
   ls -la fastAPI/PIM-BE/
   ```

2. **Environment variables not loaded**
   ```bash
   # Check environment variables
   docker-compose exec pim env | grep SUPABASE
   
   # Verify .env file
   cat .env
   ```

3. **Port conflicts**
   ```bash
   # Check if port 8004 is in use
   lsof -i :8004
   
   # Change port in docker-compose.yml if needed
   ```

4. **Database issues**
   ```bash
   # Check if database file exists
   ls -la fastAPI/PIM-BE/pim.db
   
   # Check database permissions
   docker-compose exec pim ls -la pim.db
   ```

### Debug Commands

```bash
# Enter PIM container
docker-compose exec pim bash

# Check Python environment
docker-compose exec pim python -c "import sys; print(sys.path)"

# Check installed packages
docker-compose exec pim pip list

# Check application files
docker-compose exec pim ls -la /app
```

## 📊 Monitoring

### Service Status
```bash
# View all services
docker-compose ps

# View resource usage
docker stats
```

### Logs
```bash
# View recent logs
docker-compose logs --tail=50

# Follow logs in real-time
docker-compose logs -f
```

## 🔄 Updates

### Update PIM Service
```bash
# Pull latest changes
cd fastAPI/PIM-BE
git pull

# Rebuild and restart
docker-compose build pim
docker-compose up -d pim
```

### Update All Services
```bash
# Stop all services
docker-compose down

# Rebuild all services
docker-compose build

# Start all services
docker-compose up -d
```

## 📝 Notes

- **Volume Mounting**: Code is mounted as volumes for development
- **Hot Reload**: Services use `--reload` flag for development
- **Port Mapping**: Each service runs on a different port
- **Health Checks**: PIM service includes health check endpoint
- **Environment Variables**: Loaded from root `.env` file
- **Database**: SQLite database file is persisted in the mounted volume

## 🎯 Quick Commands

```bash
# Deploy everything
./deploy.sh

# Check status
docker-compose ps

# View logs
docker-compose logs -f pim

# Restart PIM
docker-compose restart pim

# Stop everything
docker-compose down
``` 