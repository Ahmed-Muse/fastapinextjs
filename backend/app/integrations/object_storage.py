"""
Object Storage Client - Azure Blob Storage

Uses Azure Blob Storage for lab reports, proposals, and file uploads.
Configure AZURE_STORAGE_CONNECTION_STRING in .env.
"""
import logging
from typing import Optional, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

_storage_client: Optional[Any] = None


def get_storage_client():
    """
    Get the Azure Blob Storage client.
    Requires AZURE_STORAGE_CONNECTION_STRING in .env.
    """
    global _storage_client
    if _storage_client is None:
        conn_str = getattr(settings, "AZURE_STORAGE_CONNECTION_STRING", None)
        if conn_str and str(conn_str).strip():
            from app.integrations.azure_blob_client import AzureBlobClient
            _storage_client = AzureBlobClient()
            logger.info("Azure Blob Storage (container: %s)", settings.AZURE_BLOB_CONTAINER)
        else:
            logger.warning(
                "AZURE_STORAGE_CONNECTION_STRING not configured - object storage unavailable"
            )
            _storage_client = None
    return _storage_client


def get_minio_client():
    """Backward-compatible alias for get_storage_client."""
    return get_storage_client()
