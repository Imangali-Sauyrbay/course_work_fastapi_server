import uuid
from datetime import datetime, timedelta
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization


def generate_jwt():
    now = datetime.utcnow()
    payload = {
        "sub": str(uuid.uuid4()),
        "aud": "api",
        "iat": now.timestamp(),
        "exp": (now + timedelta(hours=24)).timestamp(),
        "scope": "openid",
    }

    private_key_text = Path("private_key.pem").read_text(encoding='utf-8')
    private_key = serialization.load_pem_private_key(
        private_key_text.encode('utf-8'),
        password=None,
    )
    return jwt.encode(payload=payload, key=private_key, algorithm="RS256")


print(generate_jwt())