from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.db.mysql import ProductRow, create_session_factory
from app.repositories.base import ConflictError, ProductRepository
from app.schemas import Product, ProductCreate, ProductPatch, ProductReplace


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_naive_utc(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def _to_aware_utc(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=timezone.utc)


def _row_to_product(row: ProductRow) -> Product:
    return Product(
        id=row.id,
        name=row.name,
        description=row.description,
        price=Decimal(str(row.price)),
        currency=row.currency,
        sku=row.sku,
        stock=row.stock,
        active=row.active,
        createdAt=_to_aware_utc(row.created_at),
        updatedAt=_to_aware_utc(row.updated_at),
    )


class MySQLProductRepository(ProductRepository):
    def __init__(self, *, mysql_url: str) -> None:
        self._factory = create_session_factory(mysql_url)

    def list_products(self, *, limit: int, offset: int) -> tuple[list[Product], int]:
        with self._factory.session_local() as session:
            total = session.execute(select(func.count(ProductRow.id))).scalar_one()
            rows = session.execute(
                select(ProductRow).order_by(ProductRow.created_at.desc()).offset(offset).limit(limit)
            ).scalars()
            return ([_row_to_product(r) for r in rows], int(total))

    def create_product(self, data: ProductCreate) -> Product:
        now = _utcnow()
        row = ProductRow(
            id=str(uuid4()),
            name=data.name,
            description=data.description,
            price=float(data.price),
            currency=data.currency,
            sku=data.sku,
            stock=data.stock,
            active=data.active,
            created_at=_to_naive_utc(now),
            updated_at=_to_naive_utc(now),
        )

        with self._factory.session_local() as session:
            session.add(row)
            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise ConflictError("Conflito ao criar produto (possível SKU duplicado).") from exc
            session.refresh(row)
            return _row_to_product(row)

    def get_product(self, product_id: str) -> Product | None:
        with self._factory.session_local() as session:
            row = session.get(ProductRow, product_id)
            return _row_to_product(row) if row else None

    def replace_product(self, product_id: str, data: ProductReplace) -> Product | None:
        now = _utcnow()
        with self._factory.session_local() as session:
            row = session.get(ProductRow, product_id)
            if not row:
                return None

            row.name = data.name
            row.description = data.description
            row.price = float(data.price)
            row.currency = data.currency
            row.sku = data.sku
            row.stock = data.stock
            row.active = data.active
            row.updated_at = _to_naive_utc(now)

            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise ConflictError("Conflito ao atualizar produto (possível SKU duplicado).") from exc
            session.refresh(row)
            return _row_to_product(row)

    def patch_product(self, product_id: str, data: ProductPatch) -> Product | None:
        patch = data.model_dump(exclude_unset=True)
        if "price" in patch and patch["price"] is not None:
            patch["price"] = float(patch["price"])

        now = _utcnow()
        with self._factory.session_local() as session:
            row = session.get(ProductRow, product_id)
            if not row:
                return None

            for key, value in patch.items():
                setattr(row, key, value)
            row.updated_at = _to_naive_utc(now)

            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise ConflictError("Conflito ao atualizar produto (possível SKU duplicado).") from exc
            session.refresh(row)
            return _row_to_product(row)

    def delete_product(self, product_id: str) -> bool:
        with self._factory.session_local() as session:
            row = session.get(ProductRow, product_id)
            if not row:
                return False
            session.delete(row)
            session.commit()
            return True

