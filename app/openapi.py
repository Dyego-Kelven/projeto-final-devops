from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import JSONResponse, Response


_SPEC_PATH = Path(__file__).resolve().parents[1] / "openapi" / "openapi.yaml"


def load_openapi_text() -> str:
    return _SPEC_PATH.read_text(encoding="utf-8")


def load_openapi_spec() -> dict[str, Any]:
    return yaml.safe_load(load_openapi_text())


def add_openapi_and_docs_routes(app: FastAPI) -> None:
    spec_text = load_openapi_text()
    spec_dict = load_openapi_spec()

    @app.get("/openapi.yaml", include_in_schema=False)
    def openapi_yaml() -> Response:
        return Response(content=spec_text, media_type="application/yaml")

    @app.get("/openapi.json", include_in_schema=False)
    def openapi_json() -> JSONResponse:
        return JSONResponse(content=spec_dict)

    @app.get("/docs", include_in_schema=False)
    def swagger_ui() -> Response:
        return get_swagger_ui_html(openapi_url="/openapi.json", title="Products API - Swagger UI")

    @app.get("/redoc", include_in_schema=False)
    def redoc() -> Response:
        return get_redoc_html(openapi_url="/openapi.json", title="Products API - ReDoc")
