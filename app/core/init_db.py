from app.core.dependencies import engine
from app.models import *
from app.models.base import Base
from app.core.migrations import run_migrations

def init_db():
    Base.metadata.create_all(bind=engine)
    # Run migrations for Supabase integration
    run_migrations() 