"""Main entry point for the FastAPI application."""

from request_system.infrastructure.database.sqlite import SQLiteDatabase
from request_system.infrastructure.database.sqlite.unit_of_work import SQLiteUnitOfWork
from request_system.presentation.api import create_app

# Initialize database
db = SQLiteDatabase("requests.db")
db.init_schema()

# Create FastAPI app
app = create_app(lambda: SQLiteUnitOfWork(db.connection))
