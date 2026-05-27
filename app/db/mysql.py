from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Numeric, String, Text, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class ProductRow(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BRL")
    sku: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    stock: Mapped[int] = mapped_column(nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


def _get_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def create_mysql_engine(mysql_url: str, *, retries: int = 15, delay_seconds: float = 1.0) -> Engine:
    pool_size = _get_int_env("MYSQL_POOL_SIZE", 5)
    max_overflow = _get_int_env("MYSQL_POOL_MAX_OVERFLOW", 10)
    pool_timeout = _get_int_env("MYSQL_POOL_TIMEOUT", 30)
    pool_recycle = _get_int_env("MYSQL_POOL_RECYCLE", 1800)
    connect_timeout = _get_int_env("MYSQL_CONNECT_TIMEOUT", 5)

    engine = create_engine(
        mysql_url,
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        pool_use_lifo=True,
        connect_args={"connect_timeout": connect_timeout},
    )
    last_exc: Exception | None = None

    for _ in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except OperationalError as exc:
            last_exc = exc
            engine.dispose()
            time.sleep(delay_seconds)

    raise RuntimeError("Não foi possível conectar no MySQL.") from last_exc


@dataclass(frozen=True)
class MySQLSessionFactory:
    engine: Engine
    session_local: sessionmaker


def create_session_factory(mysql_url: str) -> MySQLSessionFactory:
    engine = create_mysql_engine(mysql_url)
    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return MySQLSessionFactory(engine=engine, session_local=session_local)
