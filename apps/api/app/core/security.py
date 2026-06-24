import firebase_admin
from firebase_admin import auth
from app.core.config import settings
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import json
import base64

logger = logging.getLogger(__name__)



from app.core.firebase import init_firebase
init_firebase()

security = HTTPBearer()


def _decode_jwt_payload_unverified(token: str) -> dict:
    """Decode a JWT payload WITHOUT signature verification.
    Only safe for local development where we trust the token issuer (Firebase client SDK).
    """
    try:
        # JWT format: header.payload.signature
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Token is not a valid JWT")
        
        # Decode the payload (second part), adding padding if needed
        payload_b64 = parts[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes)
        return payload
    except Exception as e:
        raise ValueError(f"Failed to decode JWT: {e}")


async def verify_firebase_token(cred: HTTPAuthorizationCredentials) -> dict:
    """Verifies a Firebase JWT and returns the decoded token payload."""
    
    token = cred.credentials
    if token.startswith("Bearer "):
        token = token[7:]
        
    if getattr(settings, "ENVIRONMENT", "production") == "local" and "mock-" in token:
        email = token.replace("mock-", "")
        logger.info(f"Using mock token bypass for email: {email}")
        return {"email": email, "name": "Mock User"}

    # In local development, decode the JWT without verification
    # (no service account key or ADC needed)
    if getattr(settings, "ENVIRONMENT", "production") == "local":
        try:
            decoded_token = _decode_jwt_payload_unverified(token)
            logger.info(f"[LOCAL DEV] Decoded token without verification for: {decoded_token.get('email', 'unknown')}")
            return decoded_token
        except ValueError as e:
            logger.error(f"[LOCAL DEV] Failed to decode token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    try:
        # Production: Use Firebase Admin SDK for full token verification
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.error(f"Firebase token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
