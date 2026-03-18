"""
Azure Blob Storage Client for Object Storage Integration

Handles PDF storage and retrieval from Azure Blob Storage.
Used when AZURE_STORAGE_CONNECTION_STRING is configured (replaces MinIO).
Container: ai-sizing (configurable via AZURE_BLOB_CONTAINER)
"""
import logging
from typing import Optional, BinaryIO
from io import BytesIO
from datetime import timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy import to avoid hard dependency when using MinIO
_blob_service_client = None


def _get_blob_service_client():
    """Lazy-initialize BlobServiceClient."""
    global _blob_service_client
    if _blob_service_client is None and settings.AZURE_STORAGE_CONNECTION_STRING:
        try:
            from azure.storage.blob import BlobServiceClient
            _blob_service_client = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
            logger.info(
                "✅ Azure Blob Storage client initialized: container=%s",
                settings.AZURE_BLOB_CONTAINER,
            )
        except ImportError:
            logger.error("azure-storage-blob not installed. Run: pip install azure-storage-blob")
        except Exception as e:
            logger.error("Failed to initialize Azure Blob client: %s", e, exc_info=True)
    return _blob_service_client


class AzureBlobClient:
    """
    Client for Azure Blob Storage operations.
    Implements the same interface as MinIOClient for drop-in replacement.
    """

    def __init__(self):
        self.client = _get_blob_service_client()
        self.container_name = settings.AZURE_BLOB_CONTAINER or "ai-sizing"
        self.bucket_name = self.container_name  # Alias for MinIO compatibility

    def _blob_path(self, bucket_name: str, object_name: str):
        """
        Return (container, blob_path). For Azure we use one container (ai-sizing)
        and logical buckets as path prefixes: proposals/file.pdf, lab-reports/uuid.pdf.
        """
        if bucket_name == self.container_name or not bucket_name:
            return (self.container_name, object_name)
        return (self.container_name, f"{bucket_name}/{object_name}")

    def ensure_bucket_exists(self, bucket_name: Optional[str] = None) -> bool:
        """
        Ensure the container exists, creating it if necessary.
        For Azure, 'bucket' is a path prefix; we ensure the main container exists.
        """
        if not self.client:
            logger.error("Azure Blob client not initialized")
            return False
        try:
            container_client = self.client.get_container_client(self.container_name)
            if not container_client.exists():
                self.client.create_container(self.container_name)
                logger.info("Created Azure container: %s", self.container_name)
            return True
        except Exception as e:
            logger.error("Error ensuring container exists: %s", e)
            return False

    def upload_pdf(self, file_content: bytes, object_name: str) -> Optional[str]:
        """
        Upload a PDF/file to Azure Blob Storage.
        Returns a SAS URL for access (24h expiry), or base URL if SAS generation fails.
        """
        if not self.client:
            logger.error("Azure Blob client not initialized")
            return None
        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(object_name)
            # Upload without content_settings to avoid SDK dict/cache_control issues.
            # Default content_type (octet-stream) works for PDF storage/retrieval.
            blob_client.upload_blob(file_content, overwrite=True)
            sas_url = self.generate_sas_url(object_name, expiry_hours=24)
            url = sas_url if sas_url else blob_client.url
            logger.info("Uploaded to Azure Blob: %s", object_name)
            return url
        except ImportError as e:
            logger.error("azure-storage-blob not installed: %s", e)
            raise Exception("azure-storage-blob package not installed. Run: pip install azure-storage-blob")
        except Exception as e:
            logger.error("Failed to upload to Azure Blob: %s", e, exc_info=True)
            raise

    def download_pdf(self, object_name: str) -> Optional[bytes]:
        """Download a blob from Azure Storage."""
        if not self.client:
            return None
        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(object_name)
            data = blob_client.download_blob().readall()
            logger.info("Downloaded from Azure Blob: %s", object_name)
            return data
        except Exception as e:
            logger.error("Failed to download from Azure Blob: %s", e)
            return None

    def get_pdf_url(self, object_name: str, expiry_hours: int = 24) -> Optional[str]:
        """Generate a SAS URL for read access."""
        return self.generate_sas_url(object_name, expiry_hours)

    def generate_sas_url(
        self,
        object_name: str,
        expiry_hours: int = 24,
        container_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a SAS URL for a blob with read permissions.
        """
        if not self.client:
            return None
        try:
            from azure.storage.blob import BlobSasPermissions, generate_blob_sas
            from datetime import datetime, timezone

            container = container_name or self.container_name
            account_name = settings.AZURE_STORAGE_ACCOUNT_NAME or "dsstvmsharedservprod01"
            account_key = settings.AZURE_STORAGE_ACCOUNT_KEY
            if not account_key:
                logger.error("AZURE_STORAGE_ACCOUNT_KEY required for SAS URL generation")
                return None

            sas_token = generate_blob_sas(
                account_name=account_name,
                container_name=container,
                blob_name=object_name,
                account_key=account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.now(timezone.utc) + timedelta(hours=expiry_hours),
            )

            base_url = f"https://{account_name}.blob.core.windows.net"
            return f"{base_url}/{container}/{object_name}?{sas_token}"
        except Exception as e:
            logger.error("Failed to generate SAS URL: %s", e)
            return None

    def put_object(
        self,
        bucket_name: str,
        object_name: str,
        data: BinaryIO,
        length: int,
        content_type: str = "application/pdf",
    ) -> bool:
        """
        Upload bytes to a blob (for compatibility with proposal_generation).
        Maps bucket to path prefix: container=ai-sizing, blob=bucket_name/object_name.
        """
        if not self.client:
            return False
        try:
            container, blob_path = self._blob_path(bucket_name, object_name)
            container_client = self.client.get_container_client(container)
            blob_client = container_client.get_blob_client(blob_path)
            content = data.read(length) if hasattr(data, "read") else data
            if isinstance(content, (bytes, bytearray)):
                pass
            else:
                content = content.read() if hasattr(content, "read") else bytes(content)
            # Upload without content_settings to avoid SDK dict/cache_control issues.
            blob_client.upload_blob(content, overwrite=True)
            return True
        except ImportError as e:
            logger.error("azure-storage-blob not installed: %s", e)
            return False
        except Exception as e:
            logger.error("put_object failed: %s", e)
            return False

    def get_object(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        """Download blob content (for proposal download)."""
        if not self.client:
            return None
        try:
            container, blob_path = self._blob_path(bucket_name, object_name)
            container_client = self.client.get_container_client(container)
            blob_client = container_client.get_blob_client(blob_path)
            return blob_client.download_blob().readall()
        except Exception as e:
            logger.error("get_object failed: %s", e)
            return None

    def presigned_get_object(
        self,
        bucket_name: str,
        object_name: str,
        expires: Optional[timedelta] = None,
    ) -> Optional[str]:
        """Generate presigned/SAS URL for download (MinIO API compatibility)."""
        hours = int(expires.total_seconds() / 3600) if expires else 24
        container, blob_path = self._blob_path(bucket_name, object_name)
        return self.generate_sas_url(blob_path, expiry_hours=hours, container_name=container)

    def delete_pdf(self, object_name: str) -> bool:
        """Delete a blob."""
        if not self.client:
            return False
        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(object_name)
            blob_client.delete_blob()
            return True
        except Exception as e:
            logger.error("delete_pdf failed: %s", e)
            return False