# Bazaar — Development Guide

> Setting up a working environment, regenerating protobuf stubs, running migrations, testing and
> the lint/typecheck gates. The Docker-only happy path lives in [README → Quick Start](../README.md#-quick-start); this file goes deeper.

---

## 1. Toolchain

| Tool                          | Version                               | Used for                                                 |
| ----------------------------- | ------------------------------------- | -------------------------------------------------------- |
| Python                        | **3.12+** (`requires-python`) | all backend code                                         |
| [uv](https://docs.astral.sh/uv/) | latest                                | workspace + lockfile (`uv.lock`)                       |
| Node.js / npm                 | 20+                                   | `frontend/`                                            |
| Docker + Compose v2           | —                                    | containers, local stack                                  |
| git                           | —                                    | the repo is a monorepo — one checkout covers everything |

## 2. Workspace & dependencies

The root `pyproject.toml` declares a **uv workspace** whose members are `services/*`. Each service
has its own `pyproject.toml` and dependencies — there are no cross-service Python imports (shared
code is *contract*, `protos/`, not source).

```bash
uv sync --all-packages              # install every member + dev groups (one .venv at root)
uv add redis --package auth-service # add a dependency to ONE service
uv run python services/auth_service/main.py
```

Dev group (root): **mypy** (`--strict`) and **ruff** (lint + format). Service dev groups: pytest,
pytest-asyncio, pytest-env, grpcio-tools.

## 3. Environment files (what loads what)

```
.env.example              → .env    (root)      Compose interpolation for infra containers:
                                               POSTGRES_*, S3_*, GRAFANA_*, OTEL ports, FRONTEND_API_URL
services/<name>/.env.example → services/<name>/.env   pydantic Settings of that service
                                               (+ loaded as env_file by its compose service)
services/<name>/.env.test(.example)             pytest env_files for that service's tests
frontend/.env.example → frontend/.env           NEXT_PUBLIC_API_URL (browser API base)
```

Gotchas:

- The gateway's compose also expects `auth_service` / `catalog_service` / `seller_service` host
  names on `app-network` — run the full `docker compose up`, or override hosts to `localhost` when
  running things outside Docker.
- Root `POSTGRES_USER/PASSWORD/DB` are interpolated into **all three** `*_db` containers; make each
  service's own `POSTGRES_DB`/credentials match what its DB container actually got.
- `auth_service/.env` **must** set a real `JWT_SECRET` (HS256 — anything <32 chars in production is
  foot-gun territory).

## 4. Running locally without Docker

Only the databases/object-storage are needed from Docker; services can run on the host:

```bash
docker compose up -d minio catalog_db        # (etc. — note: only seller_db publishes a host port)
# for auth_db/catalog_db host access either: docker exec into them, add a ports mapping locally,
# or run a native PostgreSQL instance with the ltree extension
uv run python services/auth_service/main.py     # :50051
uv run python services/catalog_service/main.py  # :50052
uv run python services/seller_service/main.py   # :50053
uv run python services/api_gateway/main.py      # :8000  (point *.env hosts at localhost)
cd frontend && npm install && npm run dev       # :3000 (dev) — API: NEXT_PUBLIC_API_URL=:8000
```

Inside containers, the equivalent is `docker compose up -d --build <service>` (each service
rebuilds its own image: `python:3.12-slim` + deps parsed from its `pyproject.toml`).

## 5. Protocol Buffers + gRPC

Contracts are the **source of truth** in `protos/<domain>/v1/*.proto`; generated stubs are
committed under each consumer's `src/generated/`. The gateway keeps its own copies of all three
APIs. After editing a `.proto`, regenerate everywhere it's consumed:

```bash
# run from repo root — example for auth (repeat with your service paths):
uv run python -m grpc_tools.protoc \
  --proto_path=protos \
  --python_out=services/auth_service/src/generated \
  --pyi_out=services/auth_service/src/generated \
  --grpc_python_out=services/auth_service/src/generated \
  protos/auth/v1/auth.proto
```

Notes:

- Generated modules import each other **from the generated root** (`from auth.v1 import ...`) —
  that's why Dockerfiles set `PYTHONPATH=/app:/app/src/generated`.
- `**/generated/**` is excluded from ruff and mypy — don't hand-edit stubs.
- Wire up handler methods by implementing the corresponding `...Servicer` in `presentation/`.

## 6. Migrations (Alembic)

Each service owns its migrations; compose runs `*_migrations` one-shot jobs (`alembic upgrade head`) before each service starts, gated on DB healthchecks.

```bash
cd services/<name>
uv run alembic current
uv run alembic revision --autogenerate -m "Add orders table"
uv run alembic upgrade head
```

House rules proven by existing migrations:

- Postgres-specific DDL (extensions, backfills) goes in `op.execute(...)` —
  e.g. `CREATE EXTENSION IF NOT EXISTS ltree;`.
- Autogenerate won't reliably produce partial/unique-expression indexes or enum nuances —
  review and hand-edit the generated file.
- Keep model + migration in the same commit; `migrations/env.py` reads the same `Settings`
  (`sqlalchemy.url` built from `POSTGRES_*`).

## 7. Testing

Per-service pytest configs (`pytest.ini`): `asyncio_mode = auto`, `testpaths = tests`,
`env_files = .env.test`, markers:

| Marker          | What it needs                                                                                     | Example                                                                     |
| --------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `unit`        | nothing (fakes/mocks:`FakeUnitOfWork`, mocked gRPC ports)                                       | use-case logic, route validation                                            |
| `integration` | a reachable PostgreSQL                                                                            | real DB round-trips                                                         |
| `e2e`         | real PostgreSQL**and** spawns `auth_service` as a subprocess against `bazaar_auth_test` | full signup→login→refresh(rotate→replay)→logout, concurrent-signup race |

```bash
cd services/api_gateway
uv run pytest                 # everything that's runnable here
uv run pytest -m unit         # fast loop
uv run pytest -m "integration or e2e"   # with a local/test PostgreSQL up
```

Integration/e2e tests **skip automatically** when PostgreSQL isn't available, so `pytest -m unit`
is always safe in CI sandboxes. When adding integration tests, create/point at a `*_test` database
via the service's `.env.test`.

Test-design pattern to follow: production code receives `extra_providers` (`create_app(*providers)`)
or a fake UoW; assert on **ports overridden with mocks**, never monkeypatch internals.

## 8. Lint & types

Shared config in root `pyproject.toml` (ruff excludes `frontend/`, `generated/`, `.venv`):

```bash
uv run ruff check .        # E, W, F, I, B, UP (B008 ignored for FastAPI Depends)
uv run ruff format .       # double quotes, 88 cols
uv run mypy .              # strict + pydantic plugin; untyped defs forbidden
```

mypy `--strict` covers the whole workspace — new code must be fully annotated;
`disallow_untyped_defs=true`. `frontend` uses its own `npm run lint` / `npm run typecheck`.

## 9. Frontend workflow

```bash
cd frontend
npm install
npm run dev          # Turbopack dev server on :3000
npm run build        # production build (standalone output used by Dockerfile)
npm run lint         # eslint (eslint-config-next)
npm run typecheck    # tsc --noEmit
```

Layout conventions (`src/`): `app/(client|auth|seller)` route groups, `modules/<feature>`
(components / api services / zustand stores), `shared/` (axios `client.ts` + `endpoints.ts`,
UI kit, theme). API calls: TanStack Query for server state; axios interceptor injects
`Authorization` from the persisted auth store and clears it on 401.

## 10. Compose topology cheat-sheet

`docker compose config` shows the merged result of root `include:`: every service directory
contributes `{ *_db, *_migrations, <service> }`, `infrastructure/docker/compose` contributes
`minio(+init), otel-collector, prometheus, loki, grafana`, `frontend/` contributes the store.
Useful one-liners:

```bash
docker compose up -d --build catalog_service    # rebuild one service
docker compose logs -f api_gateway
docker compose down                             # keep named volumes (data survives)
docker volume rm bazaar_auth_postgres_data     # nuke DB data (prefix = root dir name)
```
