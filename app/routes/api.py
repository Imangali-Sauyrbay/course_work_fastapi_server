from fastapi import File, HTTPException, Header, Request, APIRouter, Depends, UploadFile
from starlette import status
from sqlalchemy.orm import joinedload, defer, load_only
from sqlalchemy import and_, or_
from pathlib import Path
from uuid import uuid4
import requests
import os
import re
from datetime import datetime
from app.http.middlewares.AuthRequestMiddleware import verify_token
from app.database.models import Product, User, Role, Category, ProductSeller, Address, Media, ProductMedia, BankAccount, Favourite
from app.database.database import SessionLocal
from app.http.jwt_token.jwt_gen import generate_jwt

email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

def is_valid_email(email:str):
    match = re.fullmatch(email_regex, email)
    return match is not None

router = APIRouter()

MEDIA_STORAGE_PATH = Path(__file__).parent.parent / 'storage' / 'media'

def currency_exchange_rate(from_: str, to_:str):
    if from_.lower() == to_.lower():
        return 1

    res = requests.get(f'https://api.exchangerate.host/latest?base={from_.upper()}&symbols={to_.upper()}')
    data = res.json()
    return data['rates'][to_.upper()]

def convert_currency(amount, exchange_rate):
    if amount is None or exchange_rate is None:
        return None
    return round(amount * exchange_rate if amount >= 1 or exchange_rate >= 1 else amount / exchange_rate, 2)


@router.get('/api/categories', operation_id='get_categories')
async def get_categories():
    with SessionLocal() as s:
        try:
            return s.query(Category).all()
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get('/api/products/addresses', operation_id='get_products_addresses')
async def get_products_addresses():
    with SessionLocal() as s:
        try:
            seller_addresses = s.query(Address)\
                .join(ProductSeller, ProductSeller.address_id == Address.id).all()

            city_list = set()
            country_list = set()
            
            for address in seller_addresses:
                city_list.add(address.city)
                country_list.add(address.country)

            return {
                'cities': city_list,
                'countries': country_list
            }
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get('/api/products/orderable', operation_id='get_products_orderable_column')
async def get_products_addresses():
    return [
        {
            'value': 'price',
            'alias': 'цена'
        },
        {
            'value': 'created_at',
            'alias': 'дата создания'
        },
        {
            'value': 'title',
            'alias': 'название'
        },
        {
            'value': 'description',
            'alias': 'описание'
        }
    ]

@router.get('/api/products', operation_id='get_products')
async def get_products(
    request: Request,
    query_text: str = None,
    category_id: int = 0,
    order_by_column: str = 'id',
    order_by: str = 'ASC',
    min_price: float = None,
    max_price: float = None,
    currency: str = 'USD',
    page: int = 1,
    per_page: int = 10,
    city: str = None,
    country: str = None
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

            if query_text is not None:
                cond_list.append(or_(Product.title.like(f'%{query_text}%'), Product.description.like(f'%{query_text}%')))

            if price_range.get('min') is not None and price_range.get('min') >= 0:
                cond_list.append(ProductSeller.price >= price_range.get('min'))

            if price_range.get('max') is not None:
                cond_list.append(ProductSeller.price <= price_range.get('max'))

            if country is not None:
                cond_list.append(Address.country.like(f'%{country}%'))
        
            if city is not None:
                cond_list.append(Address.city.like(f'%{city}%'))

            query = s.query(Product).join(ProductSeller, ProductSeller.product_id == Product.id, isouter=True).join(Address, ProductSeller.address_id == Address.id, isouter=True)

            
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
                    .options(joinedload(Product.medias))\
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
                    setattr(seller, 'local_currency', currency)

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
    media: list[UploadFile] = File(None),
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
    
            if media is not None:
                for m in media:
                    content_name = m.content_type.split('/')[0]
                    if content_name not in ['image','video']:
                        continue

                    media_name =  str(uuid4()) + '.' + m.content_type.split('/')[1]

                    with open(MEDIA_STORAGE_PATH / media_name, 'wb') as file:
                        while contents := m.file.read(1024 * 1024):
                            file.write(contents)
                    
                    weight = (MEDIA_STORAGE_PATH / media_name).stat().st_size

                    media_to_add.append(Media(
                        name=media_name,
                        content_type=m.content_type,
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

#========== BANK CARD ROUTES ==============
@router.get(
    '/api/bankcards',
    operation_id='get_bankcards'
)
async def get_bankcards(user_id=Depends(verify_token)):
    with SessionLocal() as s:
        address = s.query(BankAccount).where(BankAccount.user_id == user_id).all()
        return address


@router.post(
    '/api/bankcards',
    operation_id='create_bankcard'
)
async def create_bankcard(holder: str, number:str, expires:str, cvv:int, user_id=Depends(verify_token)):
    with SessionLocal() as s:
        user = s.query(User).where(User.id == user_id).first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден!')
        
        bankcard = BankAccount(
            created_at=datetime.utcnow(),
            holder=holder,
            number=number,
            expires=expires,
            cvv=cvv,
            user_id=user.id
        )

        s.add(bankcard)
        s.commit()

        return {
            'message': 'Банковская карта добавлена!'
        }


@router.put(
    '/api/bankcards',
    operation_id='update_bankcard'
)
async def update_bankcard(
    bank_card_id: int,
    holder: str = None,
    number:str = None,
    expires:str = None,
    cvv:int = None,
    user_id=Depends(verify_token)):
    with SessionLocal() as s:
        bank_card = s.query(BankAccount).join(User, BankAccount.user_id == User.id, isouter=True).where(and_(User.id == user_id, BankAccount.id == bank_card_id)).first()

        if bank_card is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Вы не можете изменять эту банковскою карточку!')

        if holder is not None:
            bank_card.holder = holder
        
        if number is not None:
            bank_card.number = number

        if expires is not None:
            bank_card.expires = expires

        if cvv is not None:
            bank_card.cvv = cvv

        s.commit()

        return {
            'message': 'Банковская карта успешно изменена!'
        }


@router.delete(
    '/api/bankcards',
    operation_id='delete_bankcard'
)
async def delete_bankcard(bank_card_id, user_id=Depends(verify_token)):
    with SessionLocal() as s:
        bank_card = s.query(BankAccount).join(User, BankAccount.user_id == User.id, isouter=True).where(and_(User.id == user_id, BankAccount.id == bank_card_id)).first()

        if bank_card is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Вы не можете удалить эту банковскою карточку!')
        
        s.delete(bank_card)
        s.commit()

        return {
            'message': 'Удалено успешно!'
        }


#========== ADDRESS ROUTES ==============

@router.get(
    '/api/address',
    operation_id='get_addresses'
)
async def get_addresses(user_id=Depends(verify_token)):
    with SessionLocal() as s:
        address = s.query(Address).where(Address.user_id == user_id).all()
        return address

@router.post(
    '/api/address',
    operation_id='create_address'
)
async def create_address(country: str, city:str, street:str, house:str, postal_code:str, user_id=Depends(verify_token)):
    with SessionLocal() as s:
        user = s.query(User).where(User.id == user_id).first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден!')
        
        address = Address(
            created_at=datetime.utcnow(),
            country=country,
            city=city,
            street=street,
            house=house,
            postal_code=postal_code,
            user_id=user.id
        )

        s.add(address)
        s.commit()

        return {
            'message': f'Адрес ст. {address.country}, г. {address.city}, ул. {address.street}, дом/кв./офисс {address.house} успешно добавлено!'
        }


@router.put(
    '/api/address',
    operation_id='update_address'
)
async def update_address(
    address_id: int,
    country: str = None,
    city:str = None,
    street:str = None,
    house:str = None,
    postal_code:str = None,
    user_id=Depends(verify_token)):
    with SessionLocal() as s:
        address = s.query(Address).join(User, Address.user_id == User.id, isouter=True).where(and_(User.id == user_id, Address.id == address_id)).first()

        if address is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Вы не можете изменять этот аддресс!')

        if country is not None:
            address.country = country
        
        if city is not None:
            address.city = city

        if street is not None:
            address.street = street

        if house is not None:
            address.house = house

        if postal_code is not None:
            address.postal_code = postal_code

        s.commit()

        return {
            'message': f'Адрес успешно изменено (ст. {address.country}, г. {address.city}, ул. {address.street}, дом/кв./офисс {address.house})!'
        }

@router.delete(
    '/api/address',
    operation_id='delete_address'
)
async def delete_address(address_id, user_id=Depends(verify_token)):
    with SessionLocal() as s:
        address = s.query(Address).join(User, Address.user_id == User.id, isouter=True).where(and_(User.id == user_id, Address.id == address_id)).first()

        if address is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Вы не можете удалить этот аддресс!')
        
        s.delete(address)
        s.commit()

        return {
            'message': f'Удалено успешно!'
        }

@router.get(
    '/api/user',
    operation_id='get_user'
)
async def get_user(user_id = Depends(verify_token)):
    with SessionLocal() as s:
        user = s.query(User).where(User.id == user_id)\
            .options(defer(User.password))\
            .options(joinedload(User.role)).first()
        
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не существует!')
        
        return user


@router.post(
    '/api/login',
    operation_id='login'
)
async def login(email: str, password: str):
    with SessionLocal() as s:
        user = s.query(User).where(and_(User.email == email, User.password == password)).first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Некоректные данные или пользователь не существует!')
        
        return {
            'x_token': 'Bearer ' + generate_jwt(user.id)
        }


@router.post(
    '/api/reg',
    operation_id='reg'
)
async def reg(name: str, email: str, password: str, role_str: str = 'user'):
    with SessionLocal() as s:
        if len(name.strip()) < 4:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Минимальная длина имени пользователя 4 символа')
        if len(password.strip()) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Минимальная длина пароля пользователя 8 символа')

        if not is_valid_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Электронная почта некорректная')

        user = s.query(User).where(and_(User.email == email)).first()

        if user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Пользователь с такой почтой уже существует!')
        
        role = s.query(Role).where(Role.name.like(f'%{role_str}%')).first()
        
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Роль {role_str} не найден в базе!')

        new_user = User(
            created_at=datetime.utcnow(),
            name=name,
            email=email,
            password=password,
            role_id=role.id
        )

        s.add(new_user)
        s.commit()

        return {
            'x_token': 'Bearer ' + generate_jwt(new_user.id)
        }


@router.get(
    '/api/roles',
    operation_id='roles'
)
async def roles():
    with SessionLocal() as s:
        roles = s.query(Role).where(Role.name.not_like('%admin%')).all()

        roles_list = set()
        for role in roles:
            roles_list.add(role.name)

        return roles_list