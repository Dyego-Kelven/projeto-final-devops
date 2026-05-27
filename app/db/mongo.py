from __future__ import annotations

import time

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


def create_mongo_client(mongo_uri: str, *, retries: int = 15, delay_seconds: float = 1.0) -> MongoClient:
    client = MongoClient(mongo_uri)
    last_exc: Exception | None = None

    for _ in range(retries):
        try:
            client.admin.command("ping")
            return client
        except Exception as exc:
            last_exc = exc
            time.sleep(delay_seconds)

    raise RuntimeError("Não foi possível conectar no MongoDB.") from last_exc


def get_products_collection(mongo_uri: str, database: str) -> Collection:
    client = create_mongo_client(mongo_uri)
    db: Database = client[database]
    collection: Collection = db["products"]
    collection.create_index("sku", unique=True, sparse=True)
    return collection

