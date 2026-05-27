from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_backend: str  # mysql | mongodb
    mysql_url: str | None
    mongo_uri: str | None
    mongo_database: str


def _in_docker() -> bool:
    return os.path.exists("/.dockerenv") or os.getenv("RUNNING_IN_DOCKER") == "1"


def _build_mysql_url_from_parts() -> str:
    host = os.getenv("MYSQL_HOST")
    if not host:
        host = "mysql" if _in_docker() else "localhost"
    host = host.strip()
    port = os.getenv("MYSQL_PORT", "3306").strip()
    user = os.getenv("MYSQL_USER", "products").strip()
    password = os.getenv("MYSQL_PASSWORD", "products")
    database = os.getenv("MYSQL_DATABASE", "products").strip()
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


def load_settings() -> Settings:
    db_backend = os.getenv("DB_BACKEND", "").strip().lower()
    if db_backend not in {"mysql", "mongodb"}:
        raise RuntimeError("DB_BACKEND deve ser 'mysql' ou 'mongodb'.")

    mysql_url = os.getenv("MYSQL_URL")
    if not mysql_url:
        mysql_url = _build_mysql_url_from_parts()

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017").strip()
    mongo_database = os.getenv("MONGO_DATABASE", "products").strip()

    return Settings(
        db_backend=db_backend,
        mysql_url=mysql_url,
        mongo_uri=mongo_uri,
        mongo_database=mongo_database,
    )
