from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.middleware.cors import CORSMiddleware
from app.routes.api import router as api_router
from app.routes.web import router as web_router
from app.utils.oas_utils import add_oas_auth
from app.http.middlewares.AuthRequestMiddleware import AuthRequestMiddleware


def main():
    server = FastAPI(debug=True)
        
    path_to_storage = Path(__file__).parent.parent.parent / 'storage'
    path_to_build= Path(__file__).parent.parent.parent / 'storage' / 'build'

    path_to_assets = path_to_build / 'assets'
    server.mount('/assets', StaticFiles(directory=path_to_assets, html=False), name='static assets')

    path_to_static = path_to_build / 'static'
    server.mount('/static', StaticFiles(directory=path_to_static, html=False), name='static files')

    path_to_images = path_to_storage / 'media'
    server.mount('/media', StaticFiles(directory=path_to_images, html=False), name='static images')



    server.include_router(api_router)
    server.include_router(web_router)

    oas = server.openapi()
    server.openapi = lambda: add_oas_auth(oas)

    # server.add_middleware(AuthRequestMiddleware)
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
