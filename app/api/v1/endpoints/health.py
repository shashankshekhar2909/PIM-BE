from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, engine
from app.core.config import settings
import time
import os
import sqlite3
from datetime import datetime, timezone
import logging

router = APIRouter()

def check_database_health(db: Session) -> dict:
    """Check database connectivity and health"""
    try:
        start_time = time.time()
        
        # Test basic connectivity
        result = db.execute("SELECT 1")
        result.fetchone()
        
        # Test database file existence and permissions
        db_path = None
        if "sqlite" in str(engine.url):
            db_path = str(engine.url).replace("sqlite:///", "").replace("sqlite://", "")
            if db_path.startswith("./"):
                db_path = db_path[2:]
            elif db_path.startswith("/app/"):
                db_path = db_path[5:]
        
        db_status = "healthy"
        db_details = {
            "type": "SQLite",
            "connection": "connected",
            "file_exists": False,
            "file_size": None,
            "file_permissions": None,
            "response_time": None
        }
        
        if db_path and os.path.exists(db_path):
            db_details["file_exists"] = True
            db_details["file_size"] = f"{os.path.getsize(db_path) / 1024:.2f} KB"
            db_details["file_permissions"] = oct(os.stat(db_path).st_mode)[-3:]
        
        # Test a simple query
        result = db.execute("SELECT COUNT(*) FROM users")
        user_count = result.fetchone()[0]
        db_details["user_count"] = user_count
        
        response_time = (time.time() - start_time) * 1000
        db_details["response_time"] = f"{response_time:.2f}ms"
        
        return {
            "status": db_status,
            "details": db_details
        }
        
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "details": {
                "error": str(e),
                "type": "SQLite",
                "connection": "disconnected"
            }
        }

def check_storage_health() -> dict:
    """Check storage (data directory) health"""
    try:
        start_time = time.time()
        
        data_dir = "data"
        storage_status = "healthy"
        storage_details = {
            "data_directory": data_dir,
            "exists": False,
            "writable": False,
            "size": None,
            "permissions": None,
            "response_time": None
        }
        
        if os.path.exists(data_dir):
            storage_details["exists"] = True
            
            # Check if directory is writable
            if os.access(data_dir, os.W_OK):
                storage_details["writable"] = True
            
            # Get directory permissions
            storage_details["permissions"] = oct(os.stat(data_dir).st_mode)[-3:]
            
            # Calculate directory size
            total_size = 0
            file_count = 0
            for dirpath, dirnames, filenames in os.walk(data_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
                        file_count += 1
            
            storage_details["size"] = f"{total_size / 1024:.2f} KB"
            storage_details["file_count"] = file_count
        
        response_time = (time.time() - start_time) * 1000
        storage_details["response_time"] = f"{response_time:.2f}ms"
        
        if not storage_details["exists"]:
            storage_status = "unhealthy"
        elif not storage_details["writable"]:
            storage_status = "warning"
        
        return {
            "status": storage_status,
            "details": storage_details
        }
        
    except Exception as e:
        logging.error(f"Storage health check failed: {e}")
        return {
            "status": "unhealthy",
            "details": {
                "error": str(e),
                "data_directory": "data"
            }
        }

def check_cache_health() -> dict:
    """Check cache health (currently no cache implementation)"""
    return {
        "status": "unknown",
        "details": {
            "type": "No cache configured",
            "message": "Cache system not implemented yet"
        }
    }

def check_external_apis_health() -> dict:
    """Check external APIs health"""
    try:
        start_time = time.time()
        
        external_status = "healthy"
        external_details = {
            "apis": [],
            "response_time": None
        }
        
        # Check if any external APIs are configured
        if settings.SUPABASE_URL:
            external_details["apis"].append({
                "name": "Supabase",
                "url": settings.SUPABASE_URL,
                "status": "configured"
            })
        else:
            external_details["apis"].append({
                "name": "Supabase",
                "status": "not configured"
            })
        
        # Add more external API checks here as needed
        
        response_time = (time.time() - start_time) * 1000
        external_details["response_time"] = f"{response_time:.2f}ms"
        
        return {
            "status": external_status,
            "details": external_details
        }
        
    except Exception as e:
        logging.error(f"External APIs health check failed: {e}")
        return {
            "status": "unhealthy",
            "details": {
                "error": str(e),
                "apis": []
            }
        }

@router.get("")
def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check endpoint"""
    start_time = time.time()
    
    # Run all health checks
    db_health = check_database_health(db)
    storage_health = check_storage_health()
    cache_health = check_cache_health()
    external_apis_health = check_external_apis_health()
    
    # Determine overall status
    overall_status = "healthy"
    if any(check["status"] == "unhealthy" for check in [db_health, storage_health, cache_health, external_apis_health]):
        overall_status = "unhealthy"
    elif any(check["status"] == "warning" for check in [db_health, storage_health, cache_health, external_apis_health]):
        overall_status = "warning"
    
    # Calculate total response time
    total_response_time = (time.time() - start_time) * 1000
    
    # Get current timestamp
    current_time = datetime.now(timezone.utc).isoformat()
    
    return {
        "Overall Status": overall_status,
        "Database": db_health["status"],
        "Cache": cache_health["status"],
        "Storage": storage_health["status"],
        "External APIs": external_apis_health["status"],
        "Response Time": f"{total_response_time:.2f}ms",
        "Last Check": current_time,
        "details": {
            "database": db_health["details"],
            "storage": storage_health["details"],
            "cache": cache_health["details"],
            "external_apis": external_apis_health["details"]
        }
    }

@router.get("/simple")
def simple_health_check():
    """Simple health check for load balancers"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
