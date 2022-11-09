from fastapi import Header, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette import status
from jwt import (
    ExpiredSignatureError,
    ImmatureSignatureError,
    InvalidAlgorithmError,
    InvalidAudienceError,
    InvalidKeyError,
    InvalidSignatureError,
    InvalidTokenError,
    MissingRequiredClaimError,
)
from app.http.jwt_token.auth import decode_and_validate_token


async def verify_token(x_token = Header()):
    if not x_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")
    try:
        auth_token = str(x_token).split(" ")[1].strip()
        token_payload = decode_and_validate_token(auth_token)
    except (
        ExpiredSignatureError,
        ImmatureSignatureError,
        InvalidAlgorithmError,
        InvalidAudienceError,
        InvalidKeyError,
        InvalidSignatureError,
        InvalidTokenError,
        MissingRequiredClaimError,
    ) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token veryfing error")
    else:
            return token_payload["sub"]



class AuthRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:

        if (
            request.url.path in ["/docs", "/openapi.json"] or
            not request.url.path.startswith('/api') or
            request.method == "OPTIONS"
        ):
            return await call_next(request)

        bearer_token = request.headers.get("x_token")
        if not bearer_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Missing access token",
                    "body": "Missing access token",
                },
            )

        try:
            auth_token = bearer_token.split(" ")[1].strip()
            token_payload = decode_and_validate_token(auth_token)
        except (
            ExpiredSignatureError,
            ImmatureSignatureError,
            InvalidAlgorithmError,
            InvalidAudienceError,
            InvalidKeyError,
            InvalidSignatureError,
            InvalidTokenError,
            MissingRequiredClaimError,
        ) as error:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(error), "body": str(error)},
            )
        else:
            request.state.user_id = token_payload["sub"]

        return await call_next(request)