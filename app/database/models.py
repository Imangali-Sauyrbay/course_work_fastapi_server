from sqlalchemy import Column, Float, DateTime, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), default=1)
    role = relationship("Role", back_populates='users')

    orders = relationship("Order", back_populates='user')
    addresses = relationship('Address',  back_populates='user')
    bank_accounts = relationship('BankAccount', back_populates='user')
    products = relationship('ProductSeller', back_populates='seller')
    favs = relationship('Product', secondary='favourites', back_populates='users_fav')


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    users = relationship("User", back_populates='role')


class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    characteristics = Column(Text, nullable=False)

    medias = relationship('Media', secondary='product_media', back_populates='products')
    sellers = relationship('ProductSeller', back_populates='product')
    users_fav = relationship('User', secondary='favourites', back_populates='favs')

    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship('Category', back_populates='products')


class ProductSeller(Base):
    __tablename__ = 'product_seller'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    seller_id = Column(Integer, ForeignKey('users.id'))
    address_id = Column(Integer, ForeignKey('addresses.id'))
    to_bank_card_id = Column(Integer, ForeignKey('bank_accounts.id'))
    price = Column(Float, nullable=False)
    quantity = Column(Integer)

    product = relationship('Product', back_populates='sellers')
    seller = relationship('User', back_populates='products')
    bank_card=relationship('BankAccount')
    address = relationship('Address')


class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)
    name = Column(String(255), nullable=False)
    products = relationship('Product', back_populates='category')


class Favourite(Base):
    __tablename__ = 'favourites'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)


class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_seller_id = Column(Integer, ForeignKey('product_seller.id'))
    address_id = Column(Integer, ForeignKey('addresses.id'))
    is_paid = Column(Boolean, default=False)
    quantity = Column(Integer)

    address = relationship('Address')
    user = relationship('User', back_populates='orders')
    product_seller = relationship('ProductSeller')


class Address(Base):
    __tablename__ = 'addresses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)

    country = Column(String(255))
    city = Column(String(255))
    street = Column(String(255))
    house = Column(String(255))
    postal_code = Column(String(255))

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='addresses')


class BankAccount(Base):
    __tablename__ = 'bank_accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)

    holder = Column(String(255))
    number = Column(String(32))
    expires = Column(String(10))
    cvv = Column(Integer)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='bank_accounts')



class ProductMedia(Base):
    __tablename__ = 'product_media'
    media_id = Column(Integer, ForeignKey('medias.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)


class Media(Base):
    __tablename__ = 'medias'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    content_type = Column(String(255))
    weight = Column(Integer)

    products = relationship('Product', secondary='product_media', back_populates='medias')
