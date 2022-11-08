from datetime import datetime, timedelta
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization

#seller Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiYXVkIjoiYXBpIiwiaWF0IjoxNjY3ODA4OTkxLjQxMzIwNCwiZXhwIjoxNjY3ODk1MzkxLjQxMzIwNCwic2NvcGUiOiJvcGVuaWQifQ.Fi_d4xHkUfKUCBTN_V6d_2zJV9LAnI6g_sFmtFv0VGCCJ0Y9XTU9_mQ2LY8dr79MYm4SYt6yTfGy2rYa3sev7OPTsl94s4jOlcMfnw8PSlHl56Pjp5e8a90jAr8Rl_VfWMmxdZWLC_jDyOeieoErBXOiUE3BHBykQmA2DHOALP6D5Kupz9qUNgEsd7jIAL3GT6d4Oa-I7lCe9B1B2emdriFH0aHduoG21BikU7b4WzKy-ihz982_cs4UzNvmYi5RypaBHh7IMfbcJz-ISI0JXpuL81nXGBv83RNKIJkj4UTRVO8lbyl-E43alsvnw_5iO8ZYKzt4wqTxS9I44SD5xQ
#user eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiYXVkIjoiYXBpIiwiaWF0IjoxNjY3ODY0MDc5Ljg3NzY3MSwiZXhwIjoxNjY3OTUwNDc5Ljg3NzY3MSwic2NvcGUiOiJvcGVuaWQifQ.OlgXgkoSRp6ti9ruFmjaUBMla5CIer5ztsNIcYcQvDxhOTlqnt_jD0nE4XtATTRwIwtVpD_kjYx9q82XftsJF0kZKlpeuqGooIenerq-k8U6J9k-LqAaoxdoe3d5PX-8fH7DoweZXiXTM2xiFA1hsBAc2OKOejje1-kCJTTiD1fDSKClzYwj1firfIt-mG_xqJEFVSMW9DOYkCWpX-QYBcN5vqWiUSOMBrWiJXtsVfcipDeO0qEM1-azLWcgLcV2NaaQ6rN75a5Xm4OW37Zwfdnpv6OFaUBz2smkg8FIWFBXDwIKgwh2A2Rj4YhHxwcf6VVYUQZSJC1-GjJTNGWN-Q
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

print(generate_jwt(1, 24))