from fastapi import APIRouter
from app.api.v1.endpoints import auth, tenant, user, category, product, search, chat, progress, superadmin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tenant.router, prefix="/tenant", tags=["tenant"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(category.router, prefix="/categories", tags=["categories"])
api_router.include_router(product.router, prefix="/products", tags=["products"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(superadmin.router, prefix="/superadmin", tags=["superadmin"]) 