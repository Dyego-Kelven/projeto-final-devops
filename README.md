# Products API (CRUD) - API First

API em Python para cadastro de produtos (CRUD) com persistência configurável em **MySQL** (relacional) ou **MongoDB** (NoSQL).

## Contrato (OpenAPI)

O contrato é a fonte de verdade (API First):
- `openapi/openapi.yaml`
- Swagger UI: `GET /docs`
- OpenAPI: `GET /openapi.yaml` e `GET /openapi.json`

## Endpoints

- `GET /products`
- `POST /products`
- `GET /products/{productId}`
- `PUT /products/{productId}`
- `PATCH /products/{productId}`
- `DELETE /products/{productId}`

## Rodar com Docker

1) Entre na pasta:

```powershell
cd products-api
```

2) Crie o arquivo `.env`:

```powershell
Copy-Item .env.example .env
```

3) Suba os serviços:

```powershell
docker compose up --build
```

Para um modo mais próximo de produção (Gunicorn + logs), use o profile `prod`:

```powershell
docker compose --profile prod up --build api-prod
```

Variáveis úteis no `.env`: `LOG_LEVEL`, `WEB_CONCURRENCY`, `WEB_TIMEOUT`.

4) Acesse:
- Swagger UI: `http://localhost:8000/docs`

Para trocar MySQL/MongoDB, altere `DB_BACKEND` no `.env` e reinicie o compose.

## Rodar local (sem Docker)

Pré-requisitos: Python 3.11+ e um MySQL ou MongoDB acessível.

```powershell
cd products-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Se estiver rodando fora do Docker, ajuste no .env:
# - MYSQL_HOST=localhost
# - MONGO_URI=mongodb://localhost:27017
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Exemplo rápido (cURL)

```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Teclado","price":199.90,"currency":"BRL","stock":10}'
```

## Seed de dados

Script para popular o banco (MySQL ou MongoDB):

```powershell
# Usa DB_BACKEND do .env
python scripts/seed_products.py

# Forcar backend
python scripts/seed_products.py --backend mysql --count 20
python scripts/seed_products.py --backend mongodb --count 20

# Limpar antes de inserir
python scripts/seed_products.py --backend mysql --clear
```
