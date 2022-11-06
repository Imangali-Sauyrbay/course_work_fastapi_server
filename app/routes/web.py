from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette import status

router = APIRouter()

@router.get('/{rest_path:path}', status_code=status.HTTP_200_OK)
def home(rest_path):
    return JSONResponse({
        'path': rest_path
    })
