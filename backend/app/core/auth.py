"""Real auth dependency — token-based with role enforcement.

Policy:
- Token signed with SECRET_KEY (JWT-style for simplicity; replace with proper OIDC if needed).
- Expiry validated (30 min default).
- Role enforced at endpoint level; object-level authorization requires ownership check.
- Never trust client-supplied user_id; derive from verified token.
- Fail startup if SECRET_KEY is placeholder in production.
"""
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.core.config import settings
from app.core.security import Role

# Only enable bearer in production; allow mock for tests with explicit flag
security_scheme = HTTPBearer(auto_error=False)


def _require_secret() -> None:
    if settings.APP_ENV == "production" and (not settings.SECRET_KEY or settings.SECRET_KEY == "replace-with-long-random-secret"):
        raise RuntimeError("Production requires SECRET_KEY set — startup blocked.")


def create_access_token(user_id: int, role: Role, expires_delta: timedelta | None = None) -> str:
    _require_secret()
    now = datetime.now(timezone.utc)
    claims = {
        "sub": str(user_id),
        "role": role.value,
        "iat": now,
        "exp": now + (expires_delta or timedelta(minutes=30)),
    }
    return jwt.encode(claims, settings.SECRET_KEY, algorithm="HS256")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    if credentials is None or not credentials.credentials:
        # Mock/development path — label explicitly; real auth requires token
        if settings.APP_ENV == "development" and settings.SECRET_KEY == "replace-with-long-random-secret":
            return {"id": 1, "role": Role.faculty, "is_mock": True, "token_verified": False}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        _require_secret()
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload.get("sub", 0))
        role_str = payload.get("role", "")
        try:
            role = Role(role_str)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid role")
        exp = payload.get("exp")
        if exp is not None and datetime.now(timezone.utc).timestamp() > exp:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})
        return {"id": user_id, "role": role, "is_mock": False, "token_verified": True}
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})


def require_role(*allowed: Role):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("is_mock") and settings.APP_ENV != "development":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Mock auth not allowed in production")
        if user.get("role") not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: insufficient role")
        return user
    return checker


def require_owner_or_admin(db, resource_owner_id: int, user: dict = Depends(get_current_user)) -> dict:
    if user.get("is_mock") and settings.APP_ENV != "development":
        raise HTTPException(status_code=403, detail="Mock auth blocked")
    if user.get("role") == Role.admin:
        return user
    if user.get("id") != resource_owner_id:
        raise HTTPException(status_code=403, detail="Access denied: not resource owner")
    return user
