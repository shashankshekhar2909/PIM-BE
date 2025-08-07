from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api_router import api_router
from app.core.init_db import init_db
from app.core.config import settings

print(f"[DEBUG] JWT SECRET_KEY: {settings.SECRET_KEY}")

app = FastAPI(title="Multi-Tenant PIM System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:4200","https://pim-v1.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    """
    Health check endpoint for Docker and monitoring.
    """
    return {
        "status": "healthy",
        "service": "Multi-Tenant PIM System",
        "version": "1.0.0"
    }

@app.get("/")
def root():
    """
    Root endpoint with basic information.
    """
    return {
        "message": "Multi-Tenant PIM System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.on_event("startup")
def on_startup():
    init_db() 