from fastapi import HTTPException, Request, APIRouter, Depends
from starlette import status
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from fastapi_pagination import add_pagination, Params
from fastapi_pagination.ext.sqlalchemy import paginate
import requests
from app.http.middlewares.AuthRequestMiddleware import verify_token
from app.database.models import Product, User, Role, Category, ProductSeller
from app.database.database import SessionLocal


router = APIRouter()
add_pagination(router)
def currency_exchange_rate(from_: str, to_:str):
    res = requests.get(f'https://api.exchangerate.host/latest?base={from_.upper()}&symbols={to_.upper()}')
    data = res.json()
    return data['rates'][to_.upper()]

def conver_currency(amount, exchange_rate):
    return round(amount / exchange_rate if exchange_rate <= 1 else amount * exchange_rate, 2)


@router.get('/api/products', operation_id='get_products')
async def get_products(
    category_id: int = 0,
    order_by_column: str = 'id',
    order_by: str = 'ASC',
    min_price: int = 0,
    max_price: int = None,
    currency: str = 'USD'
    ):
    with SessionLocal() as s:
        try:
            range_ = [i for i in [min_price, max_price] if i is not None]
            print(range_)
            if currency.upper() != 'USD':
                exchaned_arr = []
                exchange_rate = currency_exchange_rate(currency, 'usd')
                for i in range_:
                    exchaned_arr.append(conver_currency(i, exchange_rate))
            else:
                exchaned_arr = range_

            col = getattr(Product, order_by_column) if order_by_column != 'price' else getattr(ProductSeller, order_by_column)
            col = col.asc() if order_by == 'ASC' else col.desc()

            _min_ = None
            _max_ = None
            print(exchaned_arr)
            if len(exchaned_arr) >= 1 and exchaned_arr[0] >= 0:
                _min_ = ProductSeller.price >= exchaned_arr[0]

            if len(exchaned_arr) == 2:
                _max_ = ProductSeller.price <= exchaned_arr[1]

            query_range = None
            if _min_ is not None and _max_ is not None:
                query_range = and_(_min_, _max_)
            elif _min_ is not None:
                query_range = _min_
            elif _max_ is not None:
                query_range = _max_

            if category_id <= 0:
                prod = paginate(s.query(Product).join(ProductSeller).where(query_range).order_by(col),
                Params(page=1, size=10))
            else:
                category = s.query(Category).where(Category.id == category_id).first()
                if category:
                    prod = s.query(Product).join(ProductSeller).where(and_(query_range, Product.category_id == category.id)).order_by(col).options(joinedload('*')).all()
                else:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category {category} not found")

            exchange_rate = currency_exchange_rate('usd', currency)
            for p in prod.items:
                for s in p.sellers:
                    setattr(s, 'local_price', conver_currency(s.price, exchange_rate))
            return prod

        
        except (
            AttributeError
        ) as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Invalid Query data {str(e)}")

    

@router.post(
    '/api/products',
    status_code=status.HTTP_201_CREATED,
    operation_id='create_product'
)
async def create_product(
    user_id=Depends(verify_token)
    ):
    pass

@router.get('/api/products/{product_id}', operation_id='get_product')
async def get_product(product_id: int):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Product with id {product_id} not found'
    )

@router.put('/api/products/{product_id}', operation_id='update_product')
async def put_product(product_id: int, payload, user_id=Depends(verify_token)):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Product with id {product_id} not found'
    )

@router.delete(
    '/api/products/{product_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id='delete_product'
)
async def delete_product(product_id: int, user_id=Depends(verify_token)):
    # raise HTTPException(
    #     status_code=status.HTTP_404_NOT_FOUND,
    #     detail=f'Product with id {product_id} not found'
    # )
    pass

