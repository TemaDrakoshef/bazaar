# Bazaar — Services

> Per-service reference: what each process owns, its Clean Architecture layout, key settings, and
> how to run/test it in isolation. For cross-cutting behavior see [architecture.md](architecture.md); for tables see [database.md](database.md); for HTTP surface see [api.md](api.md).

---

## Common shape

Every `services/<name>` directory is a self-contained uv-workspace member:

```
services/<name>/
├── main.py                     # entry: asyncio.run(start_server())  (gateway: app.py create_app)
├── pyproject.toml              # own deps; [tool.uv] package=false
├── alembic.ini + migrations/   # own schema history (gateway has none)
├── Dockerfile                  # python:3.12-slim, installs deps, runs main.py
├── docker-compose.yml          # its *_db + *_migrations + <name> service containers
├── .env.example                # copy to .env before running
└── src/
    ├── domain/                 # entities, dtos, exceptions, interfaces — no framework imports
    ├── application/            # use cases — one callable class per operation
    ├── infrastructure/         # config(settings), di(dishka), logging, db models/repos/uow,
    │                           #   storage, observability
    ├── presentation/           # gRPC handlers+interceptors (or FastAPI routers for the gateway)
    └── generated/              # committed protobuf/grpc stubs
    tests/                      # unit / integration / e2e (pytest markers)
```

The three gRPC services share the **exact** skeleton: `src/server.py` starts `grpc.aio.server(...)`
on `0.0.0.0:<port>`, wrapping handlers in `LoggingServerInterceptor` + `DishkaAioInterceptor`, with
`setup_logging()` and `setup_telemetry()` at boot. `auth_service` is the only one that doesn’t yet
wire OpenTelemetry (see [observability.md §6](observability.md#6-gaps)).

The gateway differs: it has no database — it is a FastAPI app that fans requests out to the three
gRPC clients and maps errors (see [architecture.md §6](architecture.md#6-error-model-grpc--http)).

---

## auth-service

**Owns:** accounts, sessions, JWT issuance/validation. Contract `auth.v1.AuthService` on **gRPC :50051**,
DB `auth_db`.

| RPC               | Behavior (highlights)                                                                                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SignUp`        | validate email/phone/password → bcrypt(cost 12) → create account + session → return token pair; unique-email race handled via `IntegrityError` → `ALREADY_EXISTS` |
| `Login`         | verify password →**reactivate** existing session (or create) → token pair → bump `last_login_at`                                                               |
| `Refresh`       | verify refresh JWT → compare its**SHA-256 hash** to `sessions.refresh_token_hash` → rotate hash → new pair; mismatch ⇒ 401/404 (replay defense)               |
| `Logout`        | set session `is_active=false`, clear `refresh_token_hash`                                                                                                             |
| `ValidateToken` | verify signature/issuer/type/`exp` **and** session active in DB → `{valid, user_id}`                                                                           |

**Design:** *stateful* JWT — an unexpired access token still fails validation once its session is
inactive, which is how logout revocation works without a blocklist. Access 30 min, refresh 7 days.

**Key settings** (`.env.example`): `JWT_SECRET`, `JWT_ALGORITHM=HS256`, `JWT_ISSUER=bazaar-auth`,
`ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `PASSWORD_MIN/MAX_LENGTH`, `POSTGRES_*`.

**Tests:** unit coverage of every use case + domain validation rules (`tests/unit/`); domain
validation lives in `src/domain/validation.py`.

```bash
cd services/auth_service
uv run python main.py            # needs auth_db + .env
uv run pytest -m unit
```

---

## catalog-service

**Owns:** products, hierarchical categories (`ltree`), product media + MinIO/S3. Contract
`catalog.v1.CatalogService` on **gRPC :50052**, DB `catalog_db`.

| Group         | RPCs & invariants                                                                                                                                                                                                                   |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Category CRUD | create (with `parent_id`), read, list, update (name/is_active), **delete guarded** (no children/products — code + FK `RESTRICT`), `MoveCategory` recomputes all descendant paths and forbids move-into-self/descendant |
| Product CRUD  | create requires existing category; list =`limit/offset` + `count` and optional `merchant_id` filter; update checks category on change; every write ties the product to its `merchant_id` owner                              |
| Media         | `GetMediaUploadUrl` (presigned PUT, ~600 s) → client uploads to MinIO → `ConfirmMediaUpload` inserts row; `DeleteMedia` removes row + object; `ReorderMedia` sets positions                                               |

**Dual hierarchy model:** `parent_id` = structural source of truth; `path` = denormalized `ltree`
with a GiST index for subtree/ancestor queries (`CategoryRepository.get_descendants` uses
`descendant_of`). Both are written together in `MoveCategory`. See
[database.md §3](database.md#3-catalog_db--products-categories-media).

**Media rules** (`application/media_rules.py`) — images `jpeg|png|bmp`, ratio 3:4 (±0.02),
≥ 900×1200, ≤ 10 MB, many; videos `mp4|mov`, ≤ 50 MB, ≤ 180 s, exactly **one** (DB partial unique
index backs this). Validation is enforced server-side regardless of any client pre-check.

**Key settings:** `POSTGRES_*`, and S3/MinIO: `S3_ENDPOINT_URL` (internal, e.g. `http://minio:9000`),
`S3_PUBLIC_URL` (`http://localhost:9000`), `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET_NAME=bazaar-media`,
`OTEL_EXPORTER_OTLP_ENDPOINT`.

**Tests:** `FakeUnitOfWork` unit tests (category create/move/delete guards) + gRPC handler tests via
an in-process server; media use-case tests under `tests/application/`.

```bash
cd services/catalog_service
uv run python main.py
uv run pytest -m unit
```

---

## seller-service

**Owns:** merchant organizations and their members/roles. Contract `seller.v1.SellerService` on
**gRPC :50053**, DB `seller_db`. This service carries no S3/MinIO code — pure identity/tenancy.

| RPC                   | Behavior                                                                                                                                           |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CreateMerchant`    | reject duplicate `inn` (`ALREADY_EXISTS`) → insert merchant (`ACTIVE`) + `OWNER` membership atomically                                    |
| `GetMerchant`       | by id                                                                                                                                              |
| `ListUserMerchants` | all merchants the given `user_id` belongs to                                                                                                     |
| `VerifyAccess`      | is `user_id` an **active** member of `merchant_id`? → `{allowed, role}` — the gate the gateway calls for every `/seller/*` request |

**Roles:** `OWNER` / `MANAGER` / `VIEWER` (`MerchantRole`). Membership
`(merchant_id, user_id)` is unique; `merchant_members.user_id` stores the auth **UUID as a string**
(cross-context, no FK — see [architecture.md §5](architecture.md#5-identity--cross-service-references-no-fk-across-dbs)).

**Key settings:** `POSTGRES_*` (`POSTGRES_DB=bazaar-seller-db`), `OTEL_EXPORTER_OTLP_ENDPOINT`.

```bash
cd services/seller_service
uv run python main.py
uv run pytest -m unit
```

---

## api-gateway

**Owns:** the public HTTP surface. FastAPI on **HTTP :8000**, prefix `/api` (docs: `/docs`). **No
database.** Depends on all three gRPC services and is the only component that composes them
(e.g. `get_current_merchant_context` chains `auth.ValidateToken` → `seller.VerifyAccess`).

Layout (differs from the gRPC services — HTTP-flavored `presentation`):

```
src/
├── app.py                 # create_app(): dishka container, CORS, LoggingMiddleware,
│                          #   FastAPI/OTel instrumentors, routers, exception handlers
├── domain/                # interfaces (Abstract{Auth,Catalog,Seller}Gateway), dtos, exceptions
├── application/use_cases/ # thin per-route orchestration over the abstract gateways
├── infrastructure/
│   ├── grpc/              # AuthClient / CatalogClient / SellerClient + channels + error map
│   ├── di/container.py    # ApiGatewayProvider (binds ports→gRPC clients)
│   ├── config/settings.py # AUTH/CATALOG/SELLER_SERVICE_HOST/PORT, OTLP endpoint
│   └── observability/     # telemetry wiring
└── presentation/
    ├── api/               # router.py + v1/{auth,catalog,merchants,seller}.py + dependencies.py
    ├── schemas/           # Pydantic request/response (EmailStr, phone pattern, price/stock ≥0, INN)
    ├── middleware/        # LoggingMiddleware (request_id, trace_id, X-Request-ID)
    └── exception_handlers.py
```

**Ports & adapters:** routes depend on `FromDishka[UseCase]`; use cases depend on `Abstract*Gateway`
ports; `infrastructure/grpc/*` provide the gRPC adapters. In tests the ports are **overridden with
mocks** via `create_app(*extra_providers)` (dishka `override=True`).

**gRPC → HTTP mapping** and the auth dependency are detailed in
[architecture.md §6](architecture.md#6-error-model-grpc--http).

**Key settings:** `AUTH_SERVICE_HOST/PORT`, `CATALOG_SERVICE_HOST/PORT`, `SELLER_SERVICE_HOST/PORT`,
`OTEL_EXPORTER_OTLP_ENDPOINT`, `PROJECT_NAME/VERSION`.

```bash
cd services/api_gateway
uv run python main.py     # FastAPI/uvicorn on :8000 — needs the 3 gRPC services up
uv run pytest -m unit
uv run pytest -m e2e      # spawns a real auth_service against bazaar_auth_test DB; skips without PG
```

---

## Cross-service dependency matrix

| Consumer → Provider                      | Via           | For                                  |
| ----------------------------------------- | ------------- | ------------------------------------ |
| Frontend → api-gateway                   | HTTP `/api` | everything                           |
| api-gateway → auth-service               | gRPC          | signup/login/refresh/validate/logout |
| api-gateway → catalog-service            | gRPC          | all catalog + media operations       |
| api-gateway → seller-service             | gRPC          | merchant CRUD +`VerifyAccess`      |
| catalog-service → MinIO                  | S3 API        | presigned uploads, object deletes    |
| auth / catalog / seller → their Postgres | SQL           | persistence                          |

Domain services have **no** runtime calls to each other; all coupling is mediated by the gateway or
by shared identifiers.
