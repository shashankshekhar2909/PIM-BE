# 🚀 Server Deployment Guide for PIM System

This guide provides step-by-step instructions for deploying the PIM system on a server using Docker.

## 📋 Prerequisites

Before deploying, ensure your server has:

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **curl** (for health checks)
- **Git** (for code deployment)

### Install Docker (Ubuntu/Debian)
```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Add user to docker group
sudo usermod -aG docker $USER

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Log out and back in for group changes to take effect
```

### Install Docker Compose
```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

## 🎯 Quick Deployment

### Option 1: Standard Deployment (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd pim-be

# Make the script executable (if not already)
chmod +x deploy-server.sh

# Run the deployment script
./deploy-server.sh
```

### Option 2: Root Deployment (For Server Environments)
If you need to run as root on your server:

```bash
# Clone the repository
git clone <your-repo-url>
cd pim-be

# Make the root script executable
chmod +x deploy-server-root.sh

# Run the root deployment script
sudo ./deploy-server-root.sh
```

**Note**: The root deployment script will automatically install Docker and Docker Compose if they're not present.

### Option 3: Force Root with Standard Script
```bash
# Use the --force-root flag with the standard script
./deploy-server.sh --force-root
```

The script will automatically:
- ✅ Check prerequisites
- ✅ Set up directories
- ✅ Migrate existing database
- ✅ Clean up Docker resources
- ✅ Build and deploy the service
- ✅ Verify health status
- ✅ Show final status

## 🔧 Manual Deployment Steps

If you prefer to deploy manually or need to troubleshoot:

### 1. Set Up Directories
```bash
# Create necessary directories
mkdir -p data backups

# Set permissions
chmod 755 data backups
```

### 2. Database Setup
```bash
# If you have an existing database
if [ -f "pim.db" ]; then
    # Create backup
    cp pim.db "backups/pim.db.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Copy to data directory
    cp pim.db data/pim.db
    
    # Set permissions
    chmod 644 data/pim.db
fi
```

### 3. Deploy with Docker Compose
```bash
# Navigate to parent directory (if using multi-service setup)
cd ../..

# Stop existing services
docker compose down

# Build and start the service
docker compose up --build -d pim

# Check status
docker compose ps pim
```

### 4. Verify Deployment
```bash
# Check health endpoint
curl http://localhost:8004/health

# Check logs
docker compose logs pim -f
```

## 🌐 Configuration

### Environment Variables
Create a `.env` file in the parent directory:

```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Security
SECRET_KEY=your_secret_key_here

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./data/pim.db
```

### Port Configuration
The service runs on port 8004 by default. To change this:

1. Update `docker-compose.yml`:
```yaml
ports:
  - "YOUR_PORT:8000"  # Change YOUR_PORT to desired port
```

2. Update `deploy-server.sh`:
```bash
PORT="YOUR_PORT"  # Change to desired port
```

## 📊 Monitoring and Maintenance

### View Logs
```bash
# Follow logs in real-time
docker compose logs pim -f

# View last 100 lines
docker compose logs pim --tail=100

# View logs for specific time period
docker compose logs pim --since="2024-01-01T00:00:00"
```

### Service Management
```bash
# Check service status
docker compose ps

# Restart service
docker compose restart pim

# Stop service
docker compose stop pim

# Start service
docker compose start pim

# Stop all services
docker compose down
```

### Database Management
```bash
# Create backup
cp data/pim.db "backups/pim.db.backup.$(date +%Y%m%d_%H%M%S)"

# Restore from backup
cp "backups/pim.db.backup.YYYYMMDD_HHMMSS" data/pim.db

# Check database size
du -h data/pim.db

# Check database permissions
ls -la data/pim.db
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8004

# Kill the process
sudo kill -9 <PID>
```

#### 2. Database Permission Issues
```bash
# Fix database permissions
sudo chown $USER:$USER data/pim.db
chmod 644 data/pim.db

# Fix directory permissions
sudo chown $USER:$USER data/
chmod 755 data/
```

#### 3. Docker Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker
```

#### 4. Service Won't Start
```bash
# Check logs for errors
docker compose logs pim

# Check container status
docker compose ps

# Restart the service
docker compose restart pim
```

#### 5. Health Check Fails
```bash
# Check if service is running
docker compose ps pim

# Check container logs
docker compose logs pim --tail=50

# Check network connectivity
docker exec pim curl -f http://localhost:8000/health
```

### Debug Mode
```bash
# Run service in foreground to see logs
docker compose up pim

# Or run with debug logging
docker compose up pim --build --force-recreate
```

## 🔄 Updates and Redeployment

### Code Updates
```bash
# Pull latest code
git pull origin main

# Redeploy
./deploy-server.sh
```

### Configuration Updates
```bash
# Update environment variables
nano .env

# Restart service
docker compose restart pim
```

### Full Redeployment
```bash
# Stop and remove everything
docker compose down --volumes --remove-orphans

# Clean up images
docker image prune -f

# Redeploy
./deploy-server.sh
```

## 📈 Performance Optimization

### Resource Limits
Add resource limits to `docker-compose.yml`:

```yaml
services:
  pim:
    # ... existing configuration ...
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

### Database Optimization
For production use, consider:
- Using PostgreSQL instead of SQLite
- Implementing connection pooling
- Adding database indexes
- Setting up read replicas

## 🔒 Security Considerations

### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 8004/tcp
sudo ufw enable
```

### SSL/TLS Setup
For production, set up a reverse proxy (nginx) with SSL:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8004;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Security
- Use strong, unique SECRET_KEY
- Store sensitive data in environment variables
- Never commit `.env` files to version control
- Use Docker secrets for sensitive data in production

## 📞 Support

If you encounter issues:

1. Check the logs: `docker compose logs pim`
2. Verify configuration files
3. Check system resources
4. Review this troubleshooting guide
5. Check GitHub issues for known problems

## 🎉 Success!

Once deployed successfully, you should see:

```
🎉 SERVER DEPLOYMENT COMPLETED SUCCESSFULLY!

🌐 Access URLs:
  Application: http://localhost:8004
  Health Check: http://localhost:8004/health
  API Docs: http://localhost:8004/docs
```

Your PIM system is now running and accessible at `http://localhost:8004`!
