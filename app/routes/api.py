from fastapi import HTTPException, Request, APIRouter
from starlette import status
from app.types.schemas import ListOfProductsSchema, ProductSchema, CreateProductSchema

router = APIRouter()

@router.get('/api/products', response_model=ListOfProductsSchema, operation_id='get_products')
async def get_products(request: Request, category: str = 'all'):
    user_id = request.state.user_id
    print(user_id)
    res = {'products': [], 'page': 1}
    return res

@router.post(
    '/api/products',
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id='create_product'
)
async def create_product(payload: CreateProductSchema):
    product = payload.dict()
    print(product)

@router.get('/api/products/{product_id}', response_model=ProductSchema, operation_id='get_product')
async def get_product(product_id: int):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Product with id {product_id} not found'
    )

@router.put('/api/products/{product_id}', response_model=ProductSchema, operation_id='update_product')
async def put_product(product_id: int, payload: ProductSchema):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Product with id {product_id} not found'
    )

@router.delete(
    '/api/products/{product_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id='delete_product'
)
async def delete_product(product_id: int):
    # raise HTTPException(
    #     status_code=status.HTTP_404_NOT_FOUND,
    #     detail=f'Product with id {product_id} not found'
    # )
    pass
