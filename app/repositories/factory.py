from __future__ import annotations

from app.config import Settings
from app.repositories.base import ProductRepository
from app.repositories.mongo_repo import MongoProductRepository
from app.repositories.mysql_repo import MySQLProductRepository


def create_repository(settings: Settings) -> ProductRepository:
    if settings.db_backend == "mysql":
        if not settings.mysql_url:
            raise RuntimeError("MYSQL_URL (ou variáveis MYSQL_*) não configuradas.")
        return MySQLProductRepository(mysql_url=settings.mysql_url)

    if settings.db_backend == "mongodb":
        if not settings.mongo_uri:
            raise RuntimeError("MONGO_URI não configurado.")
        return MongoProductRepository(
            mongo_uri=settings.mongo_uri,
            database=settings.mongo_database,
        )

    raise RuntimeError(f"DB_BACKEND inválido: {settings.db_backend}")

