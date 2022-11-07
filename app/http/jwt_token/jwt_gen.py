import uuid
from datetime import datetime, timedelta
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization


def generate_jwt(data, expires_at_hour=10):
    now = datetime.utcnow()
    payload = {
        "sub": str(data),
        "aud": "api",
        "iat": now.timestamp(),
        "exp": (now + timedelta(hours=expires_at_hour)).timestamp(),
        "scope": "openid",
    }

    private_key_text = (Path(__file__).parent / "private_key.pem").read_text(encoding='utf-8')
    private_key = serialization.load_pem_private_key(
        private_key_text.encode('utf-8'),
        password=None,
    )
    return jwt.encode(payload=payload, key=private_key, algorithm="RS256")

