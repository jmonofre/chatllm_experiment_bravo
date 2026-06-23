from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt

from backend.config import SECRET_KEY, ALGORITHM


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def generate_token() -> str:
    return str(uuid.uuid4()) + str(uuid.uuid4()).replace("-", "")


def compute_expiry(minutes: int = 60 * 24 * 7) -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=minutes)