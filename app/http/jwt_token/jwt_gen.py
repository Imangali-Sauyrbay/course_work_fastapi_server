from datetime import datetime, timedelta
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization

#seller Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiYXVkIjoiYXBpIiwiaWF0IjoxNjY3ODgwMzc5LjQ2OTA0MywiZXhwIjoxNjY3OTY2Nzc5LjQ2OTA0Mywic2NvcGUiOiJvcGVuaWQifQ.E1dnTFrktB_ybSWiu0Ko68vKyaKJnZqSkCYjZAl1RZSF4sf8vi_Kb8lKQ01MoHWMXGxAEaxwTyS3sLnbvqoTTNLbSHI3x64q7KTBxGFfOptIeU3Q39EPPuhT697i1j_7hwGeYOAxkXWhUnxUsoBOW8RJHcIknjUoaL9-R1V1g7R_bOH0Ywnxvp89YxP9g3JdTYadh2yXRu_L5vTp5sB7uE63m0W6R123S08Frg7jGIIxm84v7vYXmC8AbYliw4PAqPe7qtQLCseHWqOrsTOiWxjp4LEGV149kiZYRj5OQoVlbgoncqFB0uFKgdm3fJn7B-ZvxvZsvycSvfmQlPlRMQ
#user eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiYXVkIjoiYXBpIiwiaWF0IjoxNjY3ODY0MDc5Ljg3NzY3MSwiZXhwIjoxNjY3OTUwNDc5Ljg3NzY3MSwic2NvcGUiOiJvcGVuaWQifQ.OlgXgkoSRp6ti9ruFmjaUBMla5CIer5ztsNIcYcQvDxhOTlqnt_jD0nE4XtATTRwIwtVpD_kjYx9q82XftsJF0kZKlpeuqGooIenerq-k8U6J9k-LqAaoxdoe3d5PX-8fH7DoweZXiXTM2xiFA1hsBAc2OKOejje1-kCJTTiD1fDSKClzYwj1firfIt-mG_xqJEFVSMW9DOYkCWpX-QYBcN5vqWiUSOMBrWiJXtsVfcipDeO0qEM1-azLWcgLcV2NaaQ6rN75a5Xm4OW37Zwfdnpv6OFaUBz2smkg8FIWFBXDwIKgwh2A2Rj4YhHxwcf6VVYUQZSJC1-GjJTNGWN-Q
def generate_jwt(data, expires_at_hour=12):
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