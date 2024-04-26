from pydantic import BaseModel


class Product(BaseModel):
    id: str
    name: str
    quantity: int
    price: float


class Invoice(BaseModel):
    id: str
    date: str
    title: str
    description: str
    address: str
    total: float
    products: list[Product]

