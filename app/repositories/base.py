from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import Product, ProductCreate, ProductPatch, ProductReplace


class ConflictError(Exception):
    pass


class ProductRepository(ABC):
    @abstractmethod
    def list_products(self, *, limit: int, offset: int) -> tuple[list[Product], int]:
        raise NotImplementedError

    @abstractmethod
    def create_product(self, data: ProductCreate) -> Product:
        raise NotImplementedError

    @abstractmethod
    def get_product(self, product_id: str) -> Product | None:
        raise NotImplementedError

    @abstractmethod
    def replace_product(self, product_id: str, data: ProductReplace) -> Product | None:
        raise NotImplementedError

    @abstractmethod
    def patch_product(self, product_id: str, data: ProductPatch) -> Product | None:
        raise NotImplementedError

    @abstractmethod
    def delete_product(self, product_id: str) -> bool:
        raise NotImplementedError

