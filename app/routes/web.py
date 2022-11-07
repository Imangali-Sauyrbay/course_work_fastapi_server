from fastapi import APIRouter
from pathlib import Path
from fastapi.responses import FileResponse
from starlette import status


router = APIRouter()

path_to_html = Path(__file__).parent.parent / 'storage' / 'build' / 'index.html'

@router.get('/{rest_path:path}', status_code=status.HTTP_200_OK)
async def home(rest_path):
    return FileResponse(path=path_to_html)