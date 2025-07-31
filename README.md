# Multi-Tenant Product Information Management (PIM) System Backend

This is a FastAPI backend for a scalable, multi-tenant Product Information Management (PIM) system, using SQLite for development. It supports modular, extensible APIs for user, tenant, category, product, and search management.

## Features
- Multi-tenant onboarding & isolation
- Category & schema management
- Dynamic attribute configuration
- Product CRUD operations
- CSV/XLSX bulk upload and edit
- Typesense-powered search (stub)
- LLM-powered product assistant (stub)
- Asset/media management (stub)
- Role-based access control
- Audit trail and versioning (stub)

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. The API will be available at `http://localhost:8000`.

## Project Structure
- `app/` - Main application code
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation 