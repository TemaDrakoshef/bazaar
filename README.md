# 🛍️ Bazaar

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Bazaar** is an open-source, microservices-based marketplace designed to give sellers freedom from
centralized marketplaces. It is a **uv-workspace monorepo** of Python services (a FastAPI gateway +
async gRPC domain services backed by PostgreSQL) with a Next.js storefront and a built-in
seller cabinet, plus a Docker Compose stack for observability (OpenTelemetry → Prometheus/Loki →
Grafana) and S3-compatible media storage (MinIO).

> **Status:** early-stage platform. Auth, catalog, sellers, product media, the buyer storefront and
> the seller inventory cabinet are implemented. Checkout/orders, payments, server-side cart,
> search/filter and RBAC on the [roadmap](docs/roadmap.md).

---

## ✨ Features

- **Microservice architecture** — independently deployable `auth`, `catalog`, and `seller` services
  behind a single HTTP **API Gateway**.
- **Typed RPC contracts** — services communicate over **async gRPC** with versioned protobuf
  contracts in [`protos/`](protos) (`auth.v1`, `catalog.v1`, `seller.v1`).
- **Hierarchical categories** — category tree on **PostgreSQL `ltree`** with fast
  subtree/ancestor queries and a `MoveCategory` operation that recomputes all descendant paths.
- **Multi-tenant sellers** — merchant organizations with owner/manager/viewer membership;
  products belong to a merchant and access is verified via `VerifyAccess` on every seller route.
- **Direct-to-storage media** — product images/video uploaded **straight to MinIO** via S3
  presigned PUT URLs (binary traffic never proxies through the gateway).
- **Secure auth** — bcrypt (cost 12) password hashing, short-lived JWT access tokens + rotating
  refresh tokens (stored as SHA-256 hashes, replay-protected), server-side session invalidation.
- **Clean Architecture + DI** — every service separates `domain` / `application` /
  `infrastructure` / `presentation`, wired with **dishka** and repository + unit-of-work patterns.
- **Observability** — structured logs (`structlog`), metrics and OTLP export through an OpenTelemetry
  collector; a provisioned **Grafana** dashboard ships in `infrastructure/`.
- **Modern frontend** — Next.js 16 App Router, Tailwind CSS 4, shadcn/ui, TanStack Query,
  Zustand, react-hook-form + zod; dark/light theme and SEO (sitemap, robots, JSON-LD).

---

## 🏗️ Architecture

```
┌────────────────┐  HTTP /api   ┌───────────────┐   gRPC    ┌──────────────────┐  SQL   ┌─────────────┐
│   Frontend     │ ───────────▶ │  API Gateway  │ ────────▶ │  auth_service    │ ─────▶ │   auth_db   │
│  Next.js :3001 │              │ FastAPI :8000 │ ────────▶ │  catalog_service │ ─────▶ │  catalog_db │──▶ MinIO
└────────────────┘              └───────────────┘ ────────▶ │  seller_service  │ ─────▶ │  seller_db  │
                                                            └──────────────────┘        └─────────────┘
```

Each service owns its **own PostgreSQL database and Alembic migrations** (database-per-service).
The gateway is the only HTTP surface: it translates REST → gRPC and maps gRPC status codes → HTTP.
Telemetry from services and gateway flows to the OTel collector, fanned out to Prometheus (metrics)
and Loki (logs), visualized in Grafana.

📖 Full detail — request flows, identity model, cross-service references, error mapping:
**[docs/architecture.md](docs/architecture.md)** ·
**[docs/database.md](docs/database.md)** ·
**[docs/api.md](docs/api.md)** ·
**[docs/services.md](docs/services.md)**

---

## 🧰 Tech Stack

| Layer | Technologies |
|---|---|
| **Backend services** | Python 3.12, gRPC (`grpc.aio`), SQLAlchemy 2 (async, `asyncpg`), Alembic, Pydantic v2 / pydantic-settings, `dishka` (DI), `structlog`, `python-jose`, `bcrypt`, `aioboto3`, OpenTelemetry |
| **API Gateway** | FastAPI, gRPC async clients, `dishka`, OpenTelemetry auto-instrumentation, CORS + logging middleware |
| **Databases** | PostgreSQL 16 (with `ltree`) — one DB per service; MinIO (S3-compatible) for product media |
| **Contracts** | Protocol Buffers / gRPC (versioned `*.v1` APIs) |
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS 4, shadcn/ui + Radix, Zustand, TanStack Query, Axios, react-hook-form + zod, lucide-react |
| **Infra & Observability** | Docker Compose, OpenTelemetry Collector, Prometheus, Loki, Grafana |
| **DX / Quality** | uv (workspace), Ruff (lint + format), mypy `--strict`, pytest (`unit`/`integration`/`e2e`) |

---

## 🚀 Quick Start

Requirements: **Docker + Docker Compose**; for local development without Docker also **uv** and **Node 20+**.

```bash
# 1. Clone
git clone https://github.com/TemaDrakoshef/bazaar.git
cd bazaar

# 2. Environment — root .env drives Compose interpolation for the infra containers
cp .env.example .env

# 3. Each app container additionally loads its own services/<name>/.env
cp services/auth_service/.env.example    services/auth_service/.env
cp services/catalog_service/.env.example services/catalog_service/.env
cp services/seller_service/.env.example  services/seller_service/.env
cp services/api_gateway/.env.example     services/api_gateway/.env
#    → set JWT_SECRET in the auth .env and a strong POSTGRES_PASSWORD everywhere

# 4. Bring everything up (services, DBs, migration jobs, MinIO, observability)
docker compose up -d --build
```

### Where to look once it's up

| What | URL | Notes |
|---|---|---|
| **Frontend** | http://localhost:3001 | Next.js standalone (container-internal `:3000`) |
| **API Gateway** | http://localhost:8000 | REST base path `/api` |
| **Interactive API docs** | http://localhost:8000/docs | FastAPI Swagger UI |
| **Auth gRPC** | `auth_service:50051` | internal `app-network`; `auth.v1.AuthService` |
| **Catalog gRPC** | `catalog_service:50052` | internal; `catalog.v1.CatalogService` |
| **Seller gRPC** | `seller_service:50053` | internal; `seller.v1.SellerService` |
| **seller_db** | http://localhost:5434 | the only DB published to the host |
| **MinIO** | API :9000 · console :9001 | bucket `bazaar-media` (public read) |
| **Grafana** | http://localhost:3000 | `admin`/`admin` by default |
| **Prometheus** | http://localhost:9090 | scrapes OTel collector `:8889` |
| **Loki** | http://localhost:3100 | log store |

### Smoke test

```bash
# Health check
curl http://localhost:8000/api/healthcheck

# Register → returns access + refresh tokens
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"buyer@example.com","phone":"+79991234567","password":"***"}'

# List products
curl 'http://localhost:8000/api/v1/catalog/product?limit=10'
```

More worked flows (auth → merchant onboarding → product + media upload) are in
**[docs/api.md](docs/api.md)**.

---

## 📂 Project Structure

```
bazaar/
├── protos/                  # gRPC contracts: auth/v1, catalog/v1, seller/v1
├── services/
│   ├── auth_service/        # accounts, sessions, JWT        (gRPC :50051, own Postgres)
│   ├── catalog_service/     # products, ltree categories,
│   │                        #   media → MinIO                (gRPC :50052, own Postgres)
│   ├── seller_service/      # merchants + role membership    (gRPC :50053, own Postgres)
│   └── api_gateway/         # FastAPI REST → gRPC translation (HTTP :8000)
│                            #  each service: src/{domain,application,infrastructure,presentation,generated},
│                            #                migrations/ + alembic.ini, tests/, Dockerfile,
│                            #                docker-compose.yml, .env.example
├── frontend/                # Next.js 16 App Router (:3001) — buyer store + seller cabinet
├── infrastructure/
│   ├── docker/compose/      # MinIO, OTel collector, Prometheus, Loki, Grafana
│   └── observability/       # collector/prometheus/loki configs + provisioned Grafana dashboard
├── docs/                    # this documentation
├── docker-compose.yml       # root compose: `include`s every service + infra stack
├── .env.example             # root env for Compose interpolation
└── pyproject.toml           # uv workspace + shared ruff/mypy config
```

Details per service in
[docs/services.md](docs/services.md).

---

## 🛠️ Development

Short version; the full guide (uv, protobuf codegen, Alembic, running one service without Docker,
frontend dev server, test strategy, lint/typecheck) is **[docs/development.md](docs/development.md)**.

```bash
uv sync --all-packages              # install every workspace member + dev tools

uv run ruff check .                 # lint
uv run ruff format .                # format
uv run mypy .                       # strict type check

uv run pytest                       # run tests (from a service dir)

cd services/auth_service && uv run python main.py            # run one service locally
cd frontend && npm install && npm run dev                    # http://localhost:3000

cd services/catalog_service && uv run alembic upgrade head   # migrations (per service)
```

---

## 📚 Documentation Index

| Document | What's inside |
|---|---|
| **[architecture.md](docs/architecture.md)** | Service topology, request/token/media flows, identity model, gRPC↔HTTP error mapping, ports |
| **[database.md](docs/database.md)** | Database-per-service, full schemas, `ltree` categories, MinIO, Alembic workflow |
| **[api.md](docs/api.md)** | Gateway REST endpoints, auth headers, gRPC method mapping, worked curl flows |
| **[services.md](docs/services.md)** | Per-service responsibilities, internals, env vars, standalone run |
| **[observability.md](docs/observability.md)** | OTel pipelines, Prometheus, Loki, Grafana dashboard, gaps |
| **[development.md](docs/development.md)** | Local setup, protobuf codegen, migrations, testing, tooling |
| **[roadmap.md](docs/roadmap.md)** | Known gaps and planned work (orders, payments, RBAC, search, EAV) |
| **[status.md](docs/status.md)** | Point-in-time implementation status report (RU) |

---

## 🗺️ Roadmap (short version)

Bazaar is a working vertical slice of a marketplace, not yet a complete one. Biggest open items:
**checkout, orders & payments**, a **server-side cart**, **product search/filtering**, platform-wide
**RBAC**, and the **EAV attribute model** teased on the product page. Full list with rationale:
**[docs/roadmap.md](docs/roadmap.md)**.

---

## 📄 License

Released under the **MIT License** — see [LICENSE](LICENSE).
