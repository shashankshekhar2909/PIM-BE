from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api_router import api_router
from app.core.init_db import init_db
from app.core.config import settings

print(f"[DEBUG] JWT SECRET_KEY: {settings.SECRET_KEY}")

app = FastAPI(title="Multi-Tenant PIM System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    init_db() 