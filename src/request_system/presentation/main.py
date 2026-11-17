"""Main entry point for the FastAPI application."""

from pathlib import Path
from urllib.parse import urlparse

from request_system.config import settings
from request_system.infrastructure.database.sqlite import SQLiteDatabase
from request_system.presentation.api import create_app

# Parse database URL
db_url = settings.database_url
if db_url.startswith("sqlite://"):
    # Handle sqlite://path and sqlite:///path formats
    db_path = db_url.replace("sqlite:///", "").replace("sqlite://", "")
else:
    db_path = db_url

# Schema path
schema_path = Path("/app/docs/sql/schema.sql")
if not schema_path.exists():
    schema_path = Path(__file__).parent.parent.parent / "docs" / "sql" / "schema.sql"

# Initialize database lazily
_db = None

def get_db():
    global _db
    if _db is None:
        _db = SQLiteDatabase(db_path, schema_path)
        _db.initialize()
    return _db

def uow_factory():
    return get_db().unit_of_work()

# Create FastAPI app
app = create_app(uow_factory)

# Initialize DB on startup
@app.on_event("startup")
async def startup():
    try:
        get_db()
        print("[INFO] Database initialized successfully")
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()







