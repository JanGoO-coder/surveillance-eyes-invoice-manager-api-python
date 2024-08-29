from pydantic import BaseModel
from typing import List


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
    products: List[Product]


class InvoiceRequest(BaseModel):
    invoice: Invoice
    template: str

