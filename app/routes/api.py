from fastapi import File, HTTPException, Header, Request, APIRouter, Depends, UploadFile
from starlette import status
from sqlalchemy.orm import joinedload, defer
from sqlalchemy import and_
from pathlib import Path
from uuid import uuid4
import requests
import os
from datetime import datetime
from app.http.middlewares.AuthRequestMiddleware import verify_token
from app.database.models import Product, User, Role, Category, ProductSeller, Address, Media, ProductMedia, BankAccount, Favourite
from app.database.database import SessionLocal


router = APIRouter()

MEDIA_STORAGE_PATH = Path(__file__).parent.parent / 'storage' / 'media'

def currency_exchange_rate(from_: str, to_:str):
    res = requests.get(f'https://api.exchangerate.host/latest?base={from_.upper()}&symbols={to_.upper()}')
    data = res.json()
    return data['rates'][to_.upper()]

def convert_currency(amount, exchange_rate):
    return round(amount * exchange_rate if amount >= 1 or exchange_rate >= 1 else amount / exchange_rate, 2)


@router.get('/api/products', operation_id='get_products')
async def get_products(
    request: Request,
    category_id: int = 0,
    order_by_column: str = 'id',
    order_by: str = 'ASC',
    min_price: float = None,
    max_price: float = None,
    currency: str = 'USD',
    page: int = 1,
    per_page: int = 10,
    ):
    with SessionLocal() as s:
        try:

            if currency.upper() != 'USD' and (
                max_price is not None or
                min_price is not None
            ):
                exchange_rate = currency_exchange_rate(currency, 'usd')

                price_range = {
                    'min': convert_currency(min_price, exchange_rate),
                    'max': convert_currency(max_price, exchange_rate)
                }

            else:
                price_range = {
                    'min': min_price,
                    'max': max_price
                }

            col = getattr(Product, order_by_column) if order_by_column != 'price' else getattr(ProductSeller, order_by_column)
            col = col.asc() if order_by == 'ASC' else col.desc()


            cond_list = []
            if price_range.get('min') is not None and price_range.get('min') >= 0:
                cond_list.append(ProductSeller.price >= price_range.get('min'))

            if price_range.get('max') is not None:
                cond_list.append(ProductSeller.price <= price_range.get('max'))

        
            query = s.query(Product).join(ProductSeller, ProductSeller.product_id == Product.id, isouter=True)
            
            if category_id != 0:
                category = s.query(Category).where(Category.id == category_id).first()
                if category:
                    cond_list.append(Product.category_id == category.id)
                else:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category {category} not found")


            query = query.where(and_(*cond_list)).order_by(col)

            total = len(query.all())

            per_page = per_page if per_page is not None and per_page >= 1 else 10
            page = page if page is not None and page >= 1 else 1

            query = query.options(joinedload(Product.sellers).joinedload(ProductSeller.address))\
                    .options(joinedload(Product.sellers).joinedload(ProductSeller.seller).joinedload(User.role))\
                    .options(joinedload(Product.sellers).joinedload(ProductSeller.seller).defer(User.password))\
                    .offset(per_page * (page - 1))\
                    .limit(per_page)
            
            token = request.headers.get('x-token', None)
            if token is None:
                token = request.headers.get('Authorization', None)
                
            user_id = None
            try:
                user_id = await verify_token(token)
            except:
                pass

            prod = query.all()

            exchange_rate = currency_exchange_rate('usd', currency)
            for p in prod:
                likes = s.query(Favourite).where(Favourite.product_id == p.id).count()
                setattr(p, 'likes', likes)
                setattr(p, 'liked', False)

                if user_id is not None:
                    liked = s.query(Favourite).where(and_(Favourite.product_id == p.id, Favourite.user_id == user_id)).first()
                    if liked is not None:
                        setattr(p, 'liked', True)
                    
                for seller in p.sellers:
                    setattr(seller, 'local_price', convert_currency(seller.price, exchange_rate))
        

            return {
                'items': prod,
                'total': total,
                'page': page,
                'per_page': per_page
            }
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
    description: str,
    title: str,
    characteristics: str,
    category_id: int,
    price: float,
    quantity: int,
    address_id: int,
    bank_card_id: int,
    media: list[UploadFile] = File(),
    currency: str = 'USD',
    user_id=Depends(verify_token),
    ):
    global MEDIA_STORAGE_PATH
    with SessionLocal() as s:
        prod = None
        prod_seller = None
        media_to_add: list[Media] = []
        rel_to_add: list[ProductMedia] = []
    
        try:
            seller = s.query(User).where(User.id == user_id).first()

            if seller is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Продовец не найден!")

            if seller.role.name != 'seller':
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Вы не являетесь продовцом!")

            address = s.query(Address).join(User, Address.user_id == User.id).where(and_(Address.id == address_id, User.id == user_id)).first()
    
            if address is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"У вас нет адресса с id {address_id}")
  
            bank_card = s.query(BankAccount).join(User, BankAccount.user_id == User.id).where(and_(BankAccount.id == bank_card_id, User.id == user_id)).first()
            
            if bank_card is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"У вас нет банковской карты с id {bank_card_id}")
            
            category = s.query(Category).where(Category.id == category_id).first()

            if category is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Категория с id {category_id} не найдены")

            if currency.upper() != 'USD':
                ex_rate = currency_exchange_rate(currency, 'USD')
                price = convert_currency(price, ex_rate)

            prod = Product(
                created_at=datetime.utcnow(),
                title=title,
                description=description,
                characteristics=characteristics,
                category_id=category.id
            )
            s.add(prod)
            s.commit()
    
            for media in media:
                content_name = media.content_type.split('/')[0]
                if content_name not in ['image','video']:
                    continue

                media_name =  str(uuid4()) + '.' + media.content_type.split('/')[1]

                with open(MEDIA_STORAGE_PATH / media_name, 'wb') as file:
                    while contents := media.file.read(1024 * 1024):
                        file.write(contents)
                
                weight = (MEDIA_STORAGE_PATH / media_name).stat().st_size

                media_to_add.append(Media(
                    name=media_name,
                    content_type=media.content_type,
                    weight=weight
                ))

            s.add_all(media_to_add)

            prod_seller = ProductSeller(
                product_id=prod.id,
                seller_id=seller.id,
                address_id=address.id,
                to_bank_card_id=bank_card_id,
                price=price,
                quantity=quantity
            )

            s.add(prod_seller)

            s.commit()

            for media in media_to_add:
                rel_to_add.append(ProductMedia(
                    media_id=media.id,
                    product_id=prod.id
                ))
            
            s.add_all(rel_to_add)
            s.commit()

            return {
                'message': 'Success',
                'product_id': prod.id
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            msg = ''

            try:
                s.rollback()
            except Exception as err:
                msg += 'transaction rollback remove error: ' + str(err) + '\n'

            try:
                if prod is not None and prod.id is not None:
                    s.delete(prod)
            except Exception as err:
                msg += 'porduct remove error: ' + str(err) + '\n'
            
            try:
                if prod_seller is not None and prod_seller.id is not None:
                    s.delete(prod_seller)
            except Exception as err:
                msg += 'porduct seller remove error: ' + str(err) + '\n'

            
            for rta in rel_to_add:
                try:
                    s.delete(rta)
                except Exception as err:
                    msg += 'porduct media relation remove error: ' + str(err) + '\n'
            
            
            for mta in media_to_add:
                try:
                    if os.path.exists(MEDIA_STORAGE_PATH / mta.name):
                        os.remove(MEDIA_STORAGE_PATH / mta.name)
                    if mta.id is not None:
                        s.delete(mta)
                except Exception as err:
                    msg += 'porduct media remove error: ' + str(err) + '\n'

            try:
                s.commit()
            except Exception as err:
                msg += 'remove error: ' + str(err) + '\n'

            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Server error: {str(e)} \n{msg}")
 

@router.get('/api/products/{product_id}', operation_id='get_product')
async def get_product(request: Request,product_id: int, currency: str = 'USD'):
    with SessionLocal() as s:
        prod = s.query(Product).where(Product.id == product_id).options(joinedload(Product.sellers).joinedload(ProductSeller.address))\
            .options(joinedload(Product.sellers).joinedload(ProductSeller.seller).joinedload(User.role))\
            .options(joinedload(Product.sellers).joinedload(ProductSeller.seller).defer(User.password))\
            .first()
        if prod is not None:
            if currency.upper() != 'USD':
                ex_rate = currency_exchange_rate('USD', currency)

                for seller in prod.sellers:
                    price = convert_currency(seller.price, ex_rate)
                    setattr(seller, 'local_price', price)
            
            token = request.headers.get('x-token', None)
            if token is None:
                token = request.headers.get('Authorization', None)
                
            user_id = None
            try:
                user_id = await verify_token(token)
            except:
                pass
            likes = s.query(Favourite).where(Favourite.product_id == prod.id).count()
            setattr(prod, 'likes', likes)
            setattr(prod, 'liked', False)

            if user_id is not None:
                liked = s.query(Favourite).where(and_(Favourite.product_id == prod.id, Favourite.user_id == user_id)).first()
                if liked is not None:
                    setattr(prod, 'liked', True)

            return prod

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Product with id {product_id} not found'
        )


@router.put('/api/products/{product_id}/seller', operation_id='add_seller_to_product')
async def put_product_seller(
    product_id: int,
    address_id: int,
    bank_card_id: int,
    price: float,
    quantity: int,
    currency: str = 'USD',
    user_id=Depends(verify_token)
    ):

    try:
        with SessionLocal() as s:
            seller = s.query(User).where(User.id == user_id).first()
            if seller is None or seller.role.name != 'seller':
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователя не существует или пользователь не является продовцом!')


            product = s.query(Product).where(Product.id == product_id).first()
            if product is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Продукт не найден в базе!')
            
            address = s.query(Address).join(User, Address.user_id == User.id).where(and_(Address.id == address_id, User.id == user_id)).first()
            if address is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Адресс не найден у вас в базе!')
            
            bank_card = s.query(BankAccount).join(User, BankAccount.user_id == User.id).where(and_(BankAccount.id == bank_card_id, User.id == user_id)).first()
            if bank_card is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Банковская карта не найдена у вас в базе!')
            
            if currency.upper() != 'USD':
                ex_rate = currency_exchange_rate(currency, 'USD')
                price = convert_currency(price, ex_rate)

            prod_seller = ProductSeller(
                product_id=product.id,
                seller_id=seller.id,
                address_id=address.id,
                to_bank_card_id=bank_card.id,
                price=price,
                quantity=quantity
            )

            s.add(prod_seller)
            s.commit()
            return {
                'message': 'Success',
                'product_seller_id': prod_seller.id
            }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ошибка сервера! попробуйте позднее! ' + str(e)
        )

# @router.put('/api/products/{product_id}', operation_id='update_product')
# async def put_product(product_id: int, payload, user_id=Depends(verify_token)):
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f'Product with id {product_id} not found'
#     )

@router.delete(
    '/api/products/seller',
    operation_id='delete_product_seller'
)
async def delete_product_seller(product_seller_id: int, user_id=Depends(verify_token)):
    with SessionLocal() as s:
        seller = s.query(User).where(User.id == user_id).first()
        if seller is None or seller.role.name != 'seller':
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователя не существует или пользователь не является продовцом!')

        product_seller = s.query(ProductSeller).where(ProductSeller.id == product_seller_id).first()
        if product_seller is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Продажа не найдена в базе!')
        
        try:
            s.delete(product_seller)
            s.commit()
            return {
                'message': 'Успешно удалено!'
            }
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Ошибка сервера, попробуйте позднее!')


@router.post('/api/like', operation_id='toggle favourite')
async def toggle_like(liked: bool, product_id: int, user_id=Depends(verify_token)):
        with SessionLocal() as s:
            user = s.query(User).where(User.id == user_id).first()
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователя не существует!')

            product = s.query(Product).where(Product.id == product_id).first()
            if product is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Продукт не найдена в базе!')


            
            fav = s.query(Favourite).where(and_(Favourite.user_id == user.id, Favourite.product_id == product.id)).first()
            if liked:
                if fav is not None:
                    return {
                        'liked': True
                    }

                n_fav = Favourite(
                    user_id=user.id,
                    product_id=product.id
                )
                s.add(n_fav)
                s.commit()
                return {
                    'liked': True
                }
            else:
                if fav is not None:
                    s.delete(fav)
                    s.commit()
                return {
                    'liked': False
                }           
