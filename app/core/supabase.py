from supabase import create_client, Client
from app.core.config import settings
import logging

# Initialize Supabase client
supabase: Client = None

def get_supabase_client() -> Client:
    """Get or create Supabase client instance."""
    global supabase
    if supabase is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            logging.warning("Supabase URL and ANON_KEY not set. Supabase features will be disabled.")
            return None
        
        try:
            supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
            logging.info("Supabase client initialized")
        except Exception as e:
            logging.error(f"Failed to initialize Supabase client: {str(e)}")
            return None
    
    return supabase

def get_supabase_admin_client() -> Client:
    """Get Supabase admin client with service role key."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        logging.warning("Supabase URL and SERVICE_ROLE_KEY not set. Admin features will be disabled.")
        return None
    
    try:
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    except Exception as e:
        logging.error(f"Failed to initialize Supabase admin client: {str(e)}")
        return None 