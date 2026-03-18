"""
Configuration Management for AILIFF AI Engine
"""
from pydantic_settings import BaseSettings
from pydantic import Field, model_validator
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Davis & Shirtliff AI Product Sizing Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., description="OpenAI API Key")
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Database Configuration
    # Option 1: Full DATABASE_URL (takes precedence if provided)
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="PostgreSQL Database URL (supports both sync and async: postgresql:// or postgresql+asyncpg://)"
    )
    # Option 2: Individual components (used if DATABASE_URL not provided)
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=5432, description="Database port")
    DB_USER: str = Field(default="postgres", description="Database user")
    DB_PASSWORD: str = Field(default="postgres", description="Database password")
    DB_NAME: str = Field(default="Product_Sizing_System", description="Database name")
    
    @model_validator(mode='after')
    def construct_database_url(self):
        """Construct DATABASE_URL from components if not provided."""
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return self
    
    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://:DAVIS194500@redis-master:6379",
        description="Redis URL for caching"
    )
    
    # Microsoft Business Central ERP Configuration
    BC_BASE_URL: str = Field(
        default="https://api.businesscentral.dynamics.com/v2.0",
        description="Business Central API Base URL"
    )
    BC_URL: Optional[str] = Field(default=None, description="Business Central API URL (alternative)")
    BC_USERNAME: Optional[str] = Field(default=None, description="Business Central Username")
    BC_PASSWORD: Optional[str] = Field(default=None, description="Business Central Password")
    BC_TENANT_ID: str = Field(default="", description="Azure AD Tenant ID")
    BC_CLIENT_ID: str = Field(default="", description="Azure AD Client ID")
    BC_CLIENT_SECRET: str = Field(default="", description="Azure AD Client Secret")
    BC_ENVIRONMENT: str = Field(default="Production", description="BC Environment")
    BC_COMPANY_ID: str = Field(default="", description="BC Company ID")
    
    # PVGIS API for Solar Data
    PVGIS_API_URL: str = "https://re.jrc.ec.europa.eu/api/v5_2"
    
    # Pump Database
    PUMP_CATALOG_SIZE: int = 2500
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: list = ["pdf", "png", "jpg", "jpeg"]

    # Document context ingestion
    DOCUMENT_CONTEXT_BASE_DIR: str = Field(
        default="Product_Manual_Data",
        description="Base directory for product manuals and reference PDFs"
    )
    
    # Document Parsing (LlamaParse)
    LLAMA_PARSE_API_KEY: Optional[str] = Field(
        default=None,
        description="LlamaParse API key for high-accuracy document parsing"
    )
    
    # MinIO Configuration
    MINIO_ENDPOINT: str = Field(
        default="localhost:9000",
        description="MinIO server endpoint (internal, for Docker use 'minio:9000')"
    )
    MINIO_PUBLIC_ENDPOINT: str = Field(
        default="localhost:9000",
        description="MinIO public endpoint (for external access, use 'localhost:9000' or your domain)"
    )
    MINIO_ACCESS_KEY: str = Field(
        default="minioadmin",
        description="MinIO access key"
    )
    MINIO_SECRET_KEY: str = Field(
        default="minioadmin123",
        description="MinIO secret key"
    )
    MINIO_BUCKET: str = Field(
        default="ailiff",
        description="MinIO bucket name for lab reports and documents"
    )
    MINIO_SECURE: bool = Field(
        default=False,
        description="Use HTTPS for MinIO"
    )

    # Azure Blob Storage (replaces MinIO when configured)
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = Field(
        default=None,
        description="Azure Storage connection string. When set, Azure Blob is used instead of MinIO."
    )
    AZURE_STORAGE_ACCOUNT_NAME: Optional[str] = Field(
        default=None,
        description="Azure Storage account name (for SAS URL generation)"
    )
    AZURE_STORAGE_ACCOUNT_KEY: Optional[str] = Field(
        default=None,
        description="Azure Storage account key (for SAS URL generation)"
    )
    AZURE_BLOB_CONTAINER: str = Field(
        default="ai-sizing",
        description="Azure Blob container name for lab reports, proposals, etc."
    )
    AZURE_BLOB_PREFIX: str = Field(
        default="ai-sizing/",
        description="Blob path prefix within the container (e.g., ai-sizing/)"
    )

    # Azure AD (for other integrations, e.g. auth)
    AZURE_CLIENT_ID: Optional[str] = Field(default=None, description="Azure AD Application (client) ID")
    AZURE_TENANT_ID: Optional[str] = Field(default=None, description="Azure AD Tenant ID")
    AZURE_CLIENT_SECRET: Optional[str] = Field(default=None, description="Azure AD Client secret")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Export settings instance
settings = get_settings()
