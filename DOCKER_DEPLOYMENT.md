# Docker Deployment Guide

This guide covers how to deploy the PIM system using Docker.

## 🐳 Quick Start

### Prerequisites
- Docker installed
- Docker Compose installed
- Environment variables configured

### 1. Environment Setup

Create a `.env` file in the root directory:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Application Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./pim.db

# Optional: PostgreSQL (if using external database)
# DATABASE_URL=postgresql://pim_user:pim_password@postgres:5432/pim
```

### 2. Build and Run with Docker Compose

```bash
# Build and start the application
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f pim-api

# Stop the application
docker-compose down
```

### 3. Build and Run with Docker

```bash
# Build the image
docker build -t pim-system .

# Run the container
docker run -d \
  --name pim-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/pim.db:/app/pim.db \
  pim-system

# View logs
docker logs -f pim-api

# Stop the container
docker stop pim-api
docker rm pim-api
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SUPABASE_URL` | Supabase project URL | - | Yes |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | - | Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | - | Yes |
| `SECRET_KEY` | JWT secret key | `your-secret-key-here` | No |
| `DATABASE_URL` | Database connection string | `sqlite:///./pim.db` | No |

### Port Configuration

The application runs on port `8000` by default. You can change this by:

1. **Docker Compose**: Modify the `ports` section in `docker-compose.yml`
2. **Docker**: Use the `-p` flag to map a different port

```bash
# Example: Run on port 8080
docker run -p 8080:8000 pim-system
```

## 🏥 Health Checks

The application includes a health check endpoint:

```bash
# Check health
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "service": "Multi-Tenant PIM System",
  "version": "1.0.0"
}
```

## 📊 Monitoring

### Logs
```bash
# View application logs
docker-compose logs -f pim-api

# View specific service logs
docker logs -f pim-api
```

### Metrics
- Health check endpoint: `GET /health`
- API documentation: `GET /docs`
- Root endpoint: `GET /`

## 🔒 Security

### Non-Root User
The application runs as a non-root user (`appuser`) for security.

### Environment Variables
- Sensitive data should be stored in environment variables
- Never commit `.env` files to version control
- Use Docker secrets for production deployments

### Network Security
- The application only exposes port 8000
- Use reverse proxy (nginx) for production
- Configure SSL/TLS for HTTPS

## 🚀 Production Deployment

### 1. Production Dockerfile

For production, consider using a multi-stage build:

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Production Docker Compose

```yaml
version: '3.8'

services:
  pim-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./pim.db:/app/pim.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - pim-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - pim-api
    networks:
      - pim-network

networks:
  pim-network:
    driver: bridge
```

### 3. Reverse Proxy (Nginx)

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream pim_api {
        server pim-api:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://pim_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'supabase'**
   - Ensure requirements.txt is copied and installed
   - Check if the build completed successfully

2. **Permission denied**
   - The application runs as non-root user
   - Ensure proper file permissions

3. **Database connection issues**
   - Check DATABASE_URL environment variable
   - Ensure database file is accessible

4. **Health check failures**
   - Check if the application is running
   - Verify the health endpoint is accessible

### Debug Commands

```bash
# Check container status
docker ps

# Check container logs
docker logs pim-api

# Enter container for debugging
docker exec -it pim-api bash

# Check environment variables
docker exec pim-api env

# Test health endpoint
curl http://localhost:8000/health
```

## 📝 Notes

- The application uses SQLite by default for simplicity
- For production, consider using PostgreSQL or MySQL
- The database file is mounted as a volume for persistence
- Health checks are configured for monitoring
- The application runs on port 8000 by default

## 🔄 Updates

To update the application:

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up --build -d
``` 