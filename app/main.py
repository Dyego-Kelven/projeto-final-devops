from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.config import load_settings
from app.openapi import add_openapi_and_docs_routes, load_openapi_spec
from app.repositories.factory import create_repository
from app.routers.products import router as products_router
from app.schemas import Error


load_dotenv()

settings = load_settings()
repository = create_repository(settings)

app = FastAPI(
    title="Products CRUD API",
    version="1.0.0",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)

app.state.settings = settings
app.state.repo = repository


def _verify_openapi_contract(app_: FastAPI) -> None:
    spec = load_openapi_spec()
    paths = spec.get("paths", {}) if isinstance(spec, dict) else {}

    expected: set[tuple[str, str]] = set()
    for path, operations in paths.items():
        if not isinstance(operations, dict):
            continue
        for method in ("get", "post", "put", "patch", "delete"):
            if method in operations:
                expected.add((method, path))

    actual: set[tuple[str, str]] = set()
    for route in app_.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods or []:
            method_lower = method.lower()
            if method_lower in {"head", "options"}:
                continue
            actual.add((method_lower, route.path))

    missing = expected - actual
    if missing:
        missing_str = ", ".join(f"{m.upper()} {p}" for m, p in sorted(missing))
        raise RuntimeError(f"Rotas faltando para cumprir o contrato OpenAPI: {missing_str}")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    err = Error(
        code="validation_error",
        message="Requisição inválida.",
        details={"errors": exc.errors()},
    )
    return JSONResponse(status_code=400, content=err.model_dump(mode="json"))


add_openapi_and_docs_routes(app)
app.include_router(products_router)
_verify_openapi_contract(app)
