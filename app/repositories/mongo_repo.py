from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from app.db.mongo import get_products_collection
from app.repositories.base import ConflictError, ProductRepository
from app.schemas import Product, ProductCreate, ProductPatch, ProductReplace


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_aware_utc(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=timezone.utc)


def _doc_to_product(doc: dict) -> Product:
    return Product(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        price=Decimal(str(doc["price"])),
        currency=doc.get("currency", "BRL"),
        sku=doc.get("sku"),
        stock=int(doc.get("stock", 0)),
        active=bool(doc.get("active", True)),
        createdAt=_to_aware_utc(doc["created_at"]),
        updatedAt=_to_aware_utc(doc["updated_at"]),
    )


def _create_doc_from_create(product_id: str, data: ProductCreate) -> dict:
    now = _utcnow()
    return {
        "_id": product_id,
        "name": data.name,
        "description": data.description,
        "price": str(data.price),
        "currency": data.currency,
        "sku": data.sku,
        "stock": data.stock,
        "active": data.active,
        "created_at": now,
        "updated_at": now,
    }


class MongoProductRepository(ProductRepository):
    def __init__(self, *, mongo_uri: str, database: str) -> None:
        self._collection: Collection = get_products_collection(mongo_uri, database)

    def list_products(self, *, limit: int, offset: int) -> tuple[list[Product], int]:
        total = self._collection.count_documents({})
        cursor = self._collection.find({}).sort("created_at", -1).skip(offset).limit(limit)
        return ([_doc_to_product(d) for d in cursor], int(total))

    def create_product(self, data: ProductCreate) -> Product:
        product_id = str(uuid4())
        doc = _create_doc_from_create(product_id, data)
        try:
            self._collection.insert_one(doc)
        except DuplicateKeyError as exc:
            raise ConflictError("Conflito ao criar produto (possível SKU duplicado).") from exc
        return _doc_to_product(doc)

    def get_product(self, product_id: str) -> Product | None:
        doc = self._collection.find_one({"_id": product_id})
        return _doc_to_product(doc) if doc else None

    def replace_product(self, product_id: str, data: ProductReplace) -> Product | None:
        existing = self._collection.find_one({"_id": product_id})
        if not existing:
            return None

        now = _utcnow()
        new_doc = {
            "_id": product_id,
            "name": data.name,
            "description": data.description,
            "price": str(data.price),
            "currency": data.currency,
            "sku": data.sku,
            "stock": data.stock,
            "active": data.active,
            "created_at": existing["created_at"],
            "updated_at": now,
        }
        try:
            self._collection.replace_one({"_id": product_id}, new_doc, upsert=False)
        except DuplicateKeyError as exc:
            raise ConflictError("Conflito ao atualizar produto (possível SKU duplicado).") from exc
        return _doc_to_product(new_doc)

    def patch_product(self, product_id: str, data: ProductPatch) -> Product | None:
        patch = data.model_dump(exclude_unset=True)
        if not patch:
            return self.get_product(product_id)

        patch_doc = dict(patch)
        if "price" in patch_doc and patch_doc["price"] is not None:
            patch_doc["price"] = str(patch_doc["price"])

        now = _utcnow()
        patch_doc["updated_at"] = now

        try:
            result = self._collection.update_one({"_id": product_id}, {"$set": patch_doc})
        except DuplicateKeyError as exc:
            raise ConflictError("Conflito ao atualizar produto (possível SKU duplicado).") from exc

        if result.matched_count == 0:
            return None
        return self.get_product(product_id)

    def delete_product(self, product_id: str) -> bool:
        result = self._collection.delete_one({"_id": product_id})
        return result.deleted_count > 0
