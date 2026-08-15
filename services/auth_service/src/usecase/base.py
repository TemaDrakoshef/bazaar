import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from src.core.settings import settings


class AuthBaseUsecase:
    @staticmethod
    def hash_password(password: str) -> str:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt(rounds=12)
        )
        return hashed_password.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def hash_token(token: str) -> str:
        """Return a sha256 hex digest of a token (used to track refresh tokens)."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

    @classmethod
    def create_access_token(cls, user_id: uuid.UUID, session_id: uuid.UUID) -> str:
        now = cls._now()
        payload = {
            "iss": settings.JWT_ISSUER,
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "jti": uuid.uuid4().hex,
            "type": "access",
            "user_id": str(user_id),
            "session_id": str(session_id),
        }
        return jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )

    @classmethod
    def create_refresh_token(cls, session_id: uuid.UUID) -> str:
        now = cls._now()
        payload = {
            "iss": settings.JWT_ISSUER,
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "jti": uuid.uuid4().hex,
            "type": "refresh",
            "session_id": str(session_id),
        }
        return jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )

    @classmethod
    def decode_token(cls, token: str, expected_type: str | None = None) -> dict:
        """Decode and fully validate a token.

        Enforces signature, ``exp``/``nbf``/``iat`` (jose defaults) and the
        configured issuer. If ``expected_type`` is given, the ``type`` claim is
        verified too so an access token can never be used where a refresh token
        is required (and vice versa).
        """
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
        )
        if expected_type is not None and payload.get("type") != expected_type:
            raise JWTError("token type mismatch")
        return payload
