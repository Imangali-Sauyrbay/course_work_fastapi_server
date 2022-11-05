from datetime import datetime
from pydantic import BaseModel
from fastapi import UploadFile, File

class Error(BaseModel):
    detail: str | None = None

class CreateProductSchema(BaseModel):
    imgs: list[UploadFile] = File()
    name: str
    desc: str
    price: int
    currency: str = "usd"

class ProductSchema(BaseModel):
    id: int
    created: datetime
    imgs: list[UploadFile]= File()
    name: str
    desc: str
    price: int
    currency: str = "usd"

class ListOfProductsSchema(BaseModel):
    products: list[ProductSchema]
    page: int
    