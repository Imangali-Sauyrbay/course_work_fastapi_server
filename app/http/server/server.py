from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routes.api import router as api_router
from app.utils.oas_utils import add_oas_auth
from app.http.middlewares.AuthRequestMiddleware import AuthRequestMiddleware

def main():
    server = FastAPI(debug=True)
    server.include_router(api_router)

    oas = server.openapi()
    server.openapi = lambda: add_oas_auth(oas)


    server.add_middleware(AuthRequestMiddleware)
    server.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return server

if __name__ == '__main__':
    main()
