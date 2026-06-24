import firebase_admin
import os
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class _EmulatorCredential(firebase_admin.credentials.Base):
    """A no-op credential for use with Firebase emulators."""

    def get_credential(self):
        from google.auth.credentials import AnonymousCredentials
        return AnonymousCredentials()


def init_firebase():
    try:
        if not firebase_admin._apps:
            project_id = getattr(settings, "FIREBASE_PROJECT_ID", os.environ.get("FIREBASE_PROJECT_ID", "omnimind-499716"))
            emulator_host = os.environ.get("FIRESTORE_EMULATOR_HOST")

            if emulator_host:
                # When using the Firestore emulator, use a no-op credential
                # so the SDK doesn't attempt real ADC/service-account lookup.
                firebase_admin.initialize_app(
                    credential=_EmulatorCredential(),
                    options={"projectId": project_id} if project_id else {}
                )
                logger.info(f"Firebase initialized with emulator at {emulator_host}")
            elif project_id:
                firebase_admin.initialize_app(options={"projectId": project_id})
            else:
                firebase_admin.initialize_app()
    except ValueError:
        pass
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
