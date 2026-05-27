from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import JSONResponse

from app.repositories.base import ConflictError, ProductRepository
from app.schemas import Error, Product, ProductCreate, ProductList, ProductPatch, ProductReplace


router = APIRouter()


def _get_repo(request: Request) -> ProductRepository:
    return request.app.state.repo


def _error(status_code: int, *, code: str, message: str, details: dict | None = None) -> JSONResponse:
    payload = Error(code=code, message=message, details=details).model_dump(mode="json")
    return JSONResponse(status_code=status_code, content=payload)


@router.get("/products", response_model=ProductList)
def list_products(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: ProductRepository = Depends(_get_repo),
) -> ProductList:
    items, total = repo.list_products(limit=limit, offset=offset)
    return ProductList(items=items, total=total, limit=limit, offset=offset)


@router.post("/products", status_code=status.HTTP_201_CREATED, response_model=Product)
def create_product(
    body: ProductCreate,
    repo: ProductRepository = Depends(_get_repo),
) -> Product | JSONResponse:
    try:
        return repo.create_product(body)
    except ConflictError as exc:
        return _error(status.HTTP_409_CONFLICT, code="conflict", message=str(exc))


@router.get("/products/{productId}", response_model=Product)
def get_product(
    productId: UUID,
    repo: ProductRepository = Depends(_get_repo),
) -> Product | JSONResponse:
    product = repo.get_product(str(productId))
    if not product:
        return _error(status.HTTP_404_NOT_FOUND, code="not_found", message="Produto não encontrado.")
    return product


@router.put("/products/{productId}", response_model=Product)
def replace_product(
    productId: UUID,
    body: ProductReplace,
    repo: ProductRepository = Depends(_get_repo),
) -> Product | JSONResponse:
    try:
        product = repo.replace_product(str(productId), body)
    except ConflictError as exc:
        return _error(status.HTTP_409_CONFLICT, code="conflict", message=str(exc))

    if not product:
        return _error(status.HTTP_404_NOT_FOUND, code="not_found", message="Produto não encontrado.")
    return product


@router.patch("/products/{productId}", response_model=Product)
def patch_product(
    productId: UUID,
    body: ProductPatch,
    repo: ProductRepository = Depends(_get_repo),
) -> Product | JSONResponse:
    patch = body.model_dump(exclude_unset=True)
    if not patch:
        return _error(
            status.HTTP_400_BAD_REQUEST,
            code="validation_error",
            message="Payload vazio. Informe pelo menos um campo para atualizar.",
        )

    try:
        product = repo.patch_product(str(productId), body)
    except ConflictError as exc:
        return _error(status.HTTP_409_CONFLICT, code="conflict", message=str(exc))

    if not product:
        return _error(status.HTTP_404_NOT_FOUND, code="not_found", message="Produto não encontrado.")
    return product


@router.delete(
    "/products/{productId}",
    response_class=Response,
    response_model=None,
)
def delete_product(
    productId: UUID,
    repo: ProductRepository = Depends(_get_repo),
) -> Response:
    deleted = repo.delete_product(str(productId))
    if not deleted:
        return _error(status.HTTP_404_NOT_FOUND, code="not_found", message="Produto não encontrado.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
