# 🗄️ Database Setup & Deployment Guide

## Overview

This project now uses **SQLite** for both development and production, making it easy to deploy and maintain. The database includes a default admin user and is committed to git for production deployment.

## 🚀 Quick Start

### Development Setup
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Setup development database
./setup_dev_db.sh

# 3. Run the application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
```bash
# Full deployment (recommended for first time)
./full-deploy.sh

# Quick deployment (for updates)
./quick-deploy.sh
```

## 📁 Database Files

- **`data/pim.db`** - Main SQLite database (committed to git)
- **`backups/`** - Database backups created during deployment
- **`create_production_db.py`** - Script to create fresh production database

## 👤 Default Admin User

- **Email**: `admin@pim.com`
- **Password**: `admin123`
- **Role**: `superadmin`
- **⚠️ IMPORTANT**: Change this password after first login!

## 🔧 Database Management

### Create Fresh Database
```bash
python3 create_production_db.py
```

### Backup Database
```bash
cp data/pim.db backups/pim.db.backup.$(date +%Y%m%d_%H%M%S)
```

### Restore Database
```bash
cp backups/pim.db.backup.YYYYMMDD_HHMMSS data/pim.db
```

## 🚀 Deployment Scripts

### `full-deploy.sh`
- **Purpose**: Complete deployment with fresh database
- **Use when**: First installation, major updates, troubleshooting
- **What it does**:
  - Stops existing containers
  - Creates fresh production database
  - Builds and starts Docker containers
  - Tests all endpoints
  - Verifies admin user access

### `quick-deploy.sh`
- **Purpose**: Fast deployment for existing setups
- **Use when**: Code updates, configuration changes
- **What it does**:
  - Restarts existing containers
  - Quick health check
  - No database recreation

### `setup_dev_db.sh`
- **Purpose**: Development database setup
- **Use when**: Local development, testing
- **What it does**:
  - Creates fresh development database
  - Sets up admin user
  - Ready for local development

## 🐳 Docker Deployment

The database is automatically handled during Docker deployment:

1. **Database Creation**: Fresh database created with admin user
2. **Permissions**: Proper file permissions set
3. **Backups**: Existing database backed up before recreation
4. **Verification**: Admin user access tested after deployment

## 📊 Database Schema

The database includes all necessary tables:
- Users (with admin user)
- Tenants
- Categories
- Products
- Audit logs
- Field mappings
- And more...

## 🔒 Security Features

- **Password Hashing**: Bcrypt password hashing
- **Admin User**: Pre-configured superadmin account
- **Audit Logging**: User actions tracked
- **Role-based Access**: Different user roles supported

## 🚨 Important Notes

### For Production
1. **Change Default Password**: Always change `admin123` after first login
2. **Database Backup**: Regular backups recommended
3. **File Permissions**: Database file has 644 permissions
4. **Git Committed**: Database is committed to git for deployment

### For Development
1. **Local Database**: Each developer gets their own database
2. **Admin Access**: Same admin credentials for all environments
3. **Easy Reset**: Use `setup_dev_db.sh` to reset database

## 🔍 Troubleshooting

### Database Connection Issues
```bash
# Check if database exists
ls -la data/pim.db

# Recreate database
python3 create_production_db.py

# Check permissions
ls -la data/
```

### Admin User Issues
```bash
# Test admin login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@pim.com","password":"admin123"}'
```

### Deployment Issues
```bash
# Check logs
docker compose logs pim

# Restart service
docker compose restart pim

# Full redeploy
./full-deploy.sh
```

## 📚 API Endpoints

After setup, test these endpoints:

- **Health Check**: `GET /health`
- **Admin Login**: `POST /api/v1/auth/login`
- **API Docs**: `GET /docs`

## 🎯 Next Steps

1. **Deploy**: Use `./full-deploy.sh` for production
2. **Test**: Verify admin user access
3. **Secure**: Change default admin password
4. **Monitor**: Check application logs and health

## 📞 Support

If you encounter issues:
1. Check the logs: `docker compose logs pim`
2. Verify database: `ls -la data/pim.db`
3. Test endpoints: `curl http://localhost:8000/health`
4. Recreate database: `python3 create_production_db.py`

---

**🎉 Your PIM system is now ready for production deployment with a production-ready SQLite database!**
