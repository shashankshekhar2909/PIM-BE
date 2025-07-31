from app.core.dependencies import engine
from app.models import *
from app.models.base import Base

def init_db():
    Base.metadata.create_all(bind=engine) 