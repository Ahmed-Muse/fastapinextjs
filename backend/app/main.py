"""
AILIFF AI Engine - FastAPI Application

Davis & Shirtliff's AI-powered quotation platform
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
import asyncio
from .integrations.business_central import get_bc_client
import logging
import logging.config
from .integrations.object_storage import get_storage_client
from app.core.config import settings
from .routers import (pump_sizing,water_treatment,solar,quotations,health,customers,inquiries,equipment,idayliff,lab_reports,proposals_router,
    documents_router, unified_parser, solarized_treatment, proposal_generation,agentic_workflows, workflow_traces, document_context
)
from app.api.api import api_router


#from .integrations.business_central import get_bc_client
#from .integrations.object_storage import get_storage_client

# ----------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------
# Uvicorn can override/disable existing loggers when started via CLI.
# Force a predictable configuration so module loggers (e.g. minio_client) show up
# in `docker compose logs api`.
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "INFO",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"handlers": ["console"], "level": "INFO"},
    }
)
logger = logging.getLogger(__name__)


tags_metadata = [
    # ========== CORE WORKFLOW (Primary endpoints for the proposal flow) ==========
    {"name": "1. Health", "description": "System health checks"},
    {"name": "2. Customers", "description": "ERP customer search (by name, phone, customer number)"},
    {"name": "3. Lab Reports", "description": "Lab report upload, parsing, and parameter extraction"},
    {"name": "4. Treatment Recommendations", "description": "AI-powered water treatment recommendations (3 options)"},
    {"name": "5. Proposal Generation", "description": "Generate treatment proposals with pricing"},
    
    # ========== SUPPORTING ENDPOINTS ==========
    {"name": "Quotations", "description": "BOQ generation and pricing"},
    {"name": "Equipment", "description": "Product catalog search"},
    
    # ========== ADVANCED (Hidden from main view) ==========
    {"name": "Water Treatment Analysis", "description": "Low-level water quality analysis"},
    {"name": "Document Parsing", "description": "Document parsing utilities"},
    {"name": "Pump Sizing", "description": "Hydraulic calculations"},
    {"name": "Solar Pumping", "description": "Solar system design"},
    {"name": "iDayliff IoT", "description": "Pump telemetry"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    logger.info("🚀 Starting AIDASH AI Engine...")
    logger.info(f"📊 Environment: {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"🤖 OpenAI Model: {settings.OPENAI_MODEL}")
  
    # Azure Blob Storage connectivity check
    try:
        logger.info("🪣 Object storage: Azure Blob (container: %s)", getattr(settings, "AZURE_BLOB_CONTAINER", "ai-sizing"))
        storage = get_storage_client()
        if not storage:
            logger.error("❌ Object storage client failed to initialize")
        else:
            bucket = getattr(storage, "bucket_name", None) or getattr(storage, "container_name", "ai-sizing")
            try:
                if storage.ensure_bucket_exists():
                    logger.info("✅ Object storage connectivity OK (bucket/container: %s)", bucket)
                else:
                    logger.warning("⚠️ Could not ensure bucket/container exists; will retry on first upload")
            except Exception as e:
                logger.error("❌ Object storage check failed: %s", e, exc_info=True)
    except Exception as e:
        logger.error("❌ Object storage startup check crashed: %s", e, exc_info=True)
    
    # Run database migrations on startup
    try:
        from app.db.migrations import run_migrations, get_current_revision, get_head_revision
        
        current_rev = get_current_revision()
        head_rev = get_head_revision()
        logger.info(f"📦 Database: Current revision: {current_rev}, Head: {head_rev}")
        
        if run_migrations():
            logger.info("✅ Database schema up to date")
        else:
            logger.warning("⚠️ Database migrations may have failed. Check logs.")
    except Exception as e:
        logger.error(f"❌ Failed to run database migrations: {e}")
        # Don't fail startup, but log the error
        import traceback
        logger.error(traceback.format_exc())
    
    # Test BC connection (optional, don't fail if not configured)
    # Use timeout so unreachable BC does not block API startup
    try:
        bc_client = get_bc_client()
        if settings.BC_TENANT_ID:
            loop = asyncio.get_running_loop()
            bc_status = await asyncio.wait_for(
                loop.run_in_executor(None, bc_client.test_connection_sync),
                timeout=8.0,
            )
            logger.info("📦 Business Central: %s", bc_status.get("status"))
        else:
            logger.info("📦 Business Central: not configured (BC_TENANT_ID unset)")
    except asyncio.TimeoutError:
        logger.warning("⚠️ Business Central connection check timed out (startup continues)")
    except Exception as e:
        logger.warning("⚠️ Business Central not configured: %s", e)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AIDASH AI Engine...")
    try:
        bc_client = get_bc_client()
        await bc_client.close()
    except Exception:
        pass
    

# Custom favicon for Swagger UI
custom_favicon_url = "https://res.cloudinary.com/ddk7rghqd/image/upload/v1747315349/Logo_phomyv.png"


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered quotation and sizing platform for water and energy solutions",
    version=settings.APP_VERSION,
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_favicon_url=custom_favicon_url,
    redoc_favicon_url=custom_favicon_url,
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    #allow_origins=["*"],  # Configure appropriately for production
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


# ============================================================================
# INCLUDE ROUTERS WITH PROPER TAGS
# Organized by the main workflow: Customer -> Lab Report -> Recommendations -> Proposal
# ============================================================================

# ============================================================================
# ROOT & UTILITY ENDPOINTS
# ============================================================================

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Davis & Shirtliff AI-powered quotation platform",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/health",
        "api_prefix": "/api/v1",
        "endpoints": {
            "customers": "/api/v1/customers",
            "inquiries": "/api/v1/inquiries",
            "pump_sizing": "/api/v1/pump-sizing",
            "water_treatment": "/api/v1/water-treatment",
            "solar": "/api/v1/solar",
            "equipment": "/api/v1/equipment",
            "quotations": "/api/v1/quotations",
            "idayliff": "/api/v1/idayliff"
        }
    }


@app.get("/api/v1", include_in_schema=False)
async def api_info():
    """API version information."""
    return {
        "api_version": "v1",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "documentation": "/docs"
    }


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
