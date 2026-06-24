import asyncio
import os
from google.cloud import storage
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# GCS project ID — used to construct the client without requiring ADC project detection
_GCS_PROJECT = os.environ.get(
    "GOOGLE_CLOUD_PROJECT",
    os.environ.get("FIREBASE_PROJECT_ID", getattr(settings, "FIREBASE_PROJECT_ID", None))
)


class StorageService:
    def __init__(self):
        self.bucket_name = settings.GCS_BUCKET_NAME
        self._client = None  # Lazy — created on first use

    def _get_client(self) -> storage.Client:
        """Return the GCS client, creating it on first use (lazy init)."""
        if self._client is not None:
            return self._client

        try:
            self._client = storage.Client(project=_GCS_PROJECT)
            logger.info("[StorageService] Connected using Google Cloud Credentials")
        except Exception as e:
            raise RuntimeError(
                "GCS credentials not found. Run:\n"
                "  gcloud auth application-default login\n"
                "Or set GOOGLE_APPLICATION_CREDENTIALS=<path-to-service-account.json> in .env"
            ) from e

        return self._client

    async def upload_document(self, project_id: str, document_id: str, filename: str, file_obj) -> str:
        gcs_path = f"projects/{project_id}/documents/{document_id}/{filename}"

        loop = asyncio.get_running_loop()
        def _upload():
            client = self._get_client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(gcs_path)
            blob.upload_from_file(file_obj)

        await loop.run_in_executor(None, _upload)
        logger.info(f"[StorageService] Uploaded | bucket={self.bucket_name} | path={gcs_path}")
        return gcs_path

    async def delete_document(self, gcs_path: str) -> None:
        loop = asyncio.get_running_loop()
        def _delete():
            client = self._get_client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(gcs_path)
            blob.delete()

        await loop.run_in_executor(None, _delete)
        logger.info(f"[StorageService] Deleted blob | path={gcs_path}")

storage_service = StorageService()
logger.info(f"[StorageService] Ready — bucket={settings.GCS_BUCKET_NAME} | project={_GCS_PROJECT} (client connects on first use)")
