"""
Database Migration Utilities

Handles running Alembic migrations on application startup.
"""
import logging
import subprocess
import sys
from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.core.config import settings
from app.db import sync_engine

logger = logging.getLogger(__name__)


def get_alembic_config() -> Config:
    """Get Alembic configuration."""
    alembic_ini_path = Path(__file__).parent.parent.parent / "alembic.ini"
    
    if not alembic_ini_path.exists():
        raise FileNotFoundError(
            f"Alembic configuration not found at {alembic_ini_path}. "
            "Run 'alembic init alembic' to initialize."
        )
    
    alembic_cfg = Config(str(alembic_ini_path))
    
    # Set database URL from settings
    database_url = settings.DATABASE_URL or ""
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    elif not database_url or not database_url.startswith("postgresql://"):
        # Construct from components (fallback)
        database_url = (
            f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )
    
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    return alembic_cfg


def check_database_connection() -> bool:
    """Check if database connection is available."""
    try:
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def run_migrations() -> bool:
    """
    Run Alembic migrations to upgrade database to latest version.
    
    Returns:
        True if migrations succeeded, False otherwise
    """
    try:
        if not check_database_connection():
            logger.error("Cannot run migrations: database connection failed")
            return False
        
        logger.info("🔄 Running database migrations...")
        
        alembic_cfg = get_alembic_config()
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        
        logger.info("✅ Database migrations completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def create_initial_migration() -> bool:
    """
    Create initial migration from models (if no migrations exist).
    
    This should be run manually, not on startup.
    """
    try:
        alembic_cfg = get_alembic_config()
        
        # Check if versions directory exists and has migrations
        versions_dir = Path(__file__).parent.parent.parent / "alembic" / "versions"
        if versions_dir.exists() and list(versions_dir.glob("*.py")):
            logger.info("Migrations already exist. Use 'alembic revision --autogenerate' to create new ones.")
            return False
        
        logger.info("📝 Creating initial migration...")
        command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
        
        logger.info("✅ Initial migration created")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to create initial migration: {e}")
        return False


def get_current_revision() -> str:
    """Get current database revision."""
    try:
        alembic_cfg = get_alembic_config()
        with sync_engine.connect() as conn:
            context = command.current(alembic_cfg)
            return context or "unknown"
    except Exception:
        return "unknown"


def get_head_revision() -> str:
    """Get head (latest) revision."""
    try:
        alembic_cfg = get_alembic_config()
        script = alembic_cfg.get_main_option("script_location")
        versions_dir = Path(script) / "versions"
        if versions_dir.exists():
            # Get latest migration file
            migrations = sorted(versions_dir.glob("*.py"))
            if migrations:
                # Extract revision from file
                with open(migrations[-1], 'r') as f:
                    content = f.read()
                    if 'revision = ' in content:
                        return content.split('revision = ')[1].split('\n')[0].strip('"\'')
        return "unknown"
    except Exception:
        return "unknown"
