from __future__ import annotations

import argparse
import json
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import load_settings
from app.db.mongo import get_products_collection
from app.db.mysql import ProductRow, create_session_factory
from app.repositories.base import ConflictError, ProductRepository
from app.repositories.factory import create_repository
from app.schemas import ProductCreate

try:
    from sqlalchemy import delete as sqlalchemy_delete
except Exception:  # pragma: no cover - fallback if SQLAlchemy import fails at runtime
    sqlalchemy_delete = None


DEFAULT_PRODUCTS: list[dict] = [
    {
        "name": "Teclado Mecanico RGB",
        "description": "Switch blue, layout ABNT2.",
        "price": "249.90",
        "currency": "BRL",
        "sku": "PRD-0001",
        "stock": 12,
        "active": True,
    },
    {
        "name": "Mouse Sem Fio",
        "description": "Sensor 16000 DPI, 2.4GHz.",
        "price": "129.90",
        "currency": "BRL",
        "sku": "PRD-0002",
        "stock": 25,
        "active": True,
    },
    {
        "name": "Monitor 24",
        "description": "Full HD, 75Hz.",
        "price": "799.90",
        "currency": "BRL",
        "sku": "PRD-0003",
        "stock": 8,
        "active": True,
    },
    {
        "name": "Headset USB",
        "description": "Cancelamento de ruido, microfone removivel.",
        "price": "199.90",
        "currency": "BRL",
        "sku": "PRD-0004",
        "stock": 18,
        "active": True,
    },
    {
        "name": "Notebook 14",
        "description": "Intel i5, 8GB RAM, SSD 256GB.",
        "price": "3499.00",
        "currency": "BRL",
        "sku": "PRD-0005",
        "stock": 5,
        "active": True,
    },
    {
        "name": "Cadeira Gamer",
        "description": "Reclinavel, apoio lombar.",
        "price": "1199.00",
        "currency": "BRL",
        "sku": "PRD-0006",
        "stock": 7,
        "active": True,
    },
    {
        "name": "Webcam Full HD",
        "description": "1080p, autofocus.",
        "price": "229.90",
        "currency": "BRL",
        "sku": "PRD-0007",
        "stock": 20,
        "active": True,
    },
    {
        "name": "Hub USB-C 6 Portas",
        "description": "HDMI, SD, USB 3.0.",
        "price": "189.90",
        "currency": "BRL",
        "sku": "PRD-0008",
        "stock": 15,
        "active": True,
    },
    {
        "name": "SSD 1TB",
        "description": "NVMe, leitura 3500MB/s.",
        "price": "549.90",
        "currency": "BRL",
        "sku": "PRD-0009",
        "stock": 10,
        "active": True,
    },
    {
        "name": "Memoria RAM 16GB",
        "description": "DDR4 3200MHz.",
        "price": "299.90",
        "currency": "BRL",
        "sku": "PRD-0010",
        "stock": 22,
        "active": True,
    },
    {
        "name": "Fonte 650W",
        "description": "80 Plus Bronze.",
        "price": "399.90",
        "currency": "BRL",
        "sku": "PRD-0011",
        "stock": 9,
        "active": True,
    },
    {
        "name": "Placa de Video 8GB",
        "description": "GDDR6, 256-bit.",
        "price": "2299.90",
        "currency": "BRL",
        "sku": "PRD-0012",
        "stock": 4,
        "active": True,
    },
    {
        "name": "Roteador WiFi 6",
        "description": "Dual band, 3000Mbps.",
        "price": "499.90",
        "currency": "BRL",
        "sku": "PRD-0013",
        "stock": 11,
        "active": True,
    },
    {
        "name": "Mousepad XL",
        "description": "Base emborrachada.",
        "price": "59.90",
        "currency": "BRL",
        "sku": "PRD-0014",
        "stock": 30,
        "active": True,
    },
    {
        "name": "Impressora Laser",
        "description": "Mono, 20ppm.",
        "price": "699.90",
        "currency": "BRL",
        "sku": "PRD-0015",
        "stock": 6,
        "active": True,
    },
    {
        "name": "Scanner Portatil",
        "description": "USB, A4.",
        "price": "349.90",
        "currency": "BRL",
        "sku": "PRD-0016",
        "stock": 13,
        "active": True,
    },
    {
        "name": "Microfone Condensador",
        "description": "Cardioide, USB.",
        "price": "279.90",
        "currency": "BRL",
        "sku": "PRD-0017",
        "stock": 17,
        "active": True,
    },
    {
        "name": "Cabo HDMI 2m",
        "description": "4K 60Hz.",
        "price": "39.90",
        "currency": "BRL",
        "sku": "PRD-0018",
        "stock": 40,
        "active": True,
    },
    {
        "name": "Smartphone 128GB",
        "description": "Tela 6.5, camera 48MP.",
        "price": "1999.00",
        "currency": "BRL",
        "sku": "PRD-0019",
        "stock": 14,
        "active": True,
    },
    {
        "name": "Tablet 10",
        "description": "WiFi, 64GB.",
        "price": "1299.00",
        "currency": "BRL",
        "sku": "PRD-0020",
        "stock": 9,
        "active": True,
    },
]


def _build_extra_products(start_index: int, count: int) -> list[dict]:
    categories = [
        "Teclado",
        "Mouse",
        "Monitor",
        "Notebook",
        "Cadeira",
        "Headset",
        "Webcam",
        "Roteador",
        "SSD",
        "Memoria RAM",
        "Fonte",
        "Placa de Video",
        "Hub USB-C",
        "Impressora",
        "Scanner",
        "Microfone",
        "Cabo HDMI",
        "Tablet",
        "Smartphone",
        "Mousepad",
    ]
    variants = [
        "Pro",
        "Plus",
        "Slim",
        "RGB",
        "Wireless",
        "Ergonomico",
        "Ultra",
        "Eco",
        "Mini",
        "Max",
    ]

    products: list[dict] = []
    for idx in range(count):
        serial = start_index + idx
        category = categories[serial % len(categories)]
        variant = variants[(serial // len(categories)) % len(variants)]
        price = Decimal("49.90") + Decimal(serial)
        products.append(
            {
                "name": f"{category} {variant}",
                "description": f"{category} {variant} para uso diario.",
                "price": f"{price:.2f}",
                "currency": "BRL",
                "sku": f"PRD-{serial:04d}",
                "stock": (serial * 3) % 50,
                "active": serial % 7 != 0,
            }
        )
    return products


def _load_products_from_file(path: Path) -> list[dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("O arquivo de entrada deve conter uma lista JSON de produtos.")
    return raw


def _build_products(count: int) -> list[dict]:
    if count <= len(DEFAULT_PRODUCTS):
        return DEFAULT_PRODUCTS[:count]
    extra = _build_extra_products(len(DEFAULT_PRODUCTS) + 1, count - len(DEFAULT_PRODUCTS))
    return [*DEFAULT_PRODUCTS, *extra]


def _coerce_products(raw_items: Iterable[dict]) -> list[ProductCreate]:
    products: list[ProductCreate] = []
    for idx, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"Produto {idx} invalido: esperado objeto JSON.")
        data = dict(raw)
        if "price" in data and data["price"] is not None:
            data["price"] = Decimal(str(data["price"]))
        products.append(ProductCreate(**data))
    return products


def _clear_products(settings_backend: str, *, mysql_url: str | None, mongo_uri: str | None, mongo_db: str) -> int:
    if settings_backend == "mysql":
        if not mysql_url:
            raise RuntimeError("MYSQL_URL (ou variaveis MYSQL_*) nao configuradas.")
        factory = create_session_factory(mysql_url)
        with factory.session_local() as session:
            if sqlalchemy_delete is None:
                deleted = session.execute("DELETE FROM products")
                session.commit()
                return int(getattr(deleted, "rowcount", 0) or 0)
            result = session.execute(sqlalchemy_delete(ProductRow))
            session.commit()
            return int(getattr(result, "rowcount", 0) or 0)

    if settings_backend == "mongodb":
        if not mongo_uri:
            raise RuntimeError("MONGO_URI nao configurado.")
        collection = get_products_collection(mongo_uri, mongo_db)
        result = collection.delete_many({})
        return int(result.deleted_count)

    raise RuntimeError(f"DB_BACKEND invalido: {settings_backend}")


def _seed(repo: ProductRepository, products: list[ProductCreate], *, fail_on_conflict: bool) -> tuple[int, int]:
    created = 0
    skipped = 0
    for product in products:
        try:
            repo.create_product(product)
            created += 1
        except ConflictError:
            if fail_on_conflict:
                raise
            skipped += 1
    return created, skipped


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed de produtos para MySQL ou MongoDB.")
    parser.add_argument("--backend", choices=["mysql", "mongodb"], help="Sobrescreve DB_BACKEND.")
    parser.add_argument("--count", type=int, default=None, help="Quantidade de produtos para inserir.")
    parser.add_argument("--input", type=Path, help="Arquivo JSON com lista de produtos.")
    parser.add_argument("--clear", action="store_true", help="Remove todos os produtos antes do seed.")
    parser.add_argument(
        "--fail-on-conflict",
        action="store_true",
        help="Falha se houver conflito (ex.: SKU duplicado).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Valida a carga sem inserir no banco.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    load_dotenv(dotenv_path=ROOT / ".env")
    if args.backend:
        os.environ["DB_BACKEND"] = args.backend

    settings = load_settings()
    if args.input:
        raw_products = _load_products_from_file(args.input)
        if args.count is not None:
            raw_products = raw_products[: args.count]
    else:
        count = args.count if args.count is not None else len(DEFAULT_PRODUCTS)
        if count <= 0:
            raise ValueError("--count deve ser maior que zero.")
        raw_products = _build_products(count)

    products = _coerce_products(raw_products)

    print(f"Backend: {settings.db_backend}")
    print(f"Produtos validados: {len(products)}")

    if args.dry_run:
        print("Dry run ativo. Nenhum dado foi inserido.")
        return

    if args.clear:
        deleted = _clear_products(
            settings.db_backend,
            mysql_url=settings.mysql_url,
            mongo_uri=settings.mongo_uri,
            mongo_db=settings.mongo_database,
        )
        print(f"Produtos removidos antes do seed: {deleted}")

    repo = create_repository(settings)
    created, skipped = _seed(repo, products, fail_on_conflict=args.fail_on_conflict)
    print(f"Produtos inseridos: {created}")
    print(f"Produtos ignorados por conflito: {skipped}")


if __name__ == "__main__":
    main()
