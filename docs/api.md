# Bazaar — REST API (API Gateway)

> Every public HTTP surface of the platform: routes, request/response shapes, auth requirements and the gRPC method each route calls. Interactive version always available at **http://localhost:8000/docs** (FastAPI/Swagger). 
>
> Internals: [architecture.md](architecture.md) · [services.md](services.md)

---

## 1. Conventions

| Item         | Value                                                                                                                  |
| ------------ | ---------------------------------------------------------------------------------------------------------------------- |
| Base URL     | `http://localhost:8000/api`                                                                                          |
| Content type | `application/json` (UTF-8)                                                                                           |
| Errors       | `{"detail": "<message>"}` with status per [architecture.md §6](architecture.md#6-error-model-grpc--http)               |
| Pagination   | `?limit=` (default 20) & `?offset=` (default 0); list endpoints with totals return `{products: [...], count: N}` |
| Timestamps   | ISO-8601 (`created_at`, `updated_at`)                                                                              |
| Versioning   | path version (`/v1/…`), gRPC contracts are versioned likewise (`auth.v1`, …)                                     |

### Auth headers

| Scheme           | Header(s)                                                           | Used by                                                                                                   |
| ---------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| None (public)    | —                                                                  | `/auth/*`, public catalog reads, `/healthcheck`                                                       |
| Bearer           | `Authorization: Bearer <access_token>`                            | `/merchants/*`                                                                                          |
| Merchant context | `Authorization: Bearer …` **and** `X-Merchant-ID: <int>` | `/seller/*` — gateway chains `auth.ValidateToken` → `seller.VerifyAccess`; 401/403/422 on failure |

> ⚠️ Today public catalog **reads** and **admin writes** on `/api/v1/catalog/*` are *not* behind
> auth (RBAC is a roadmap item); only `/merchants` and `/seller` require a token. See
> [roadmap.md](roadmap.md).

---

## 2. Health

| Method & path            | Auth | Calls      | Returns              |
| ------------------------ | ---- | ---------- | -------------------- |
| `GET /api/healthcheck` | –   | – (local) | `{"status": "ok"}` |

## 3. Auth — `/api/v1/auth` → `auth.v1.AuthService`

| Method & path      | gRPC              | Success       | Body → Response                                                                    |
| ------------------ | ----------------- | ------------- | ----------------------------------------------------------------------------------- |
| `POST /signup`   | `SignUp`        | **201** | `{email, phone?, password}` → `{access_token, refresh_token}`                  |
| `POST /login`    | `Login`         | 200           | `{email, password}` → `{access_token, refresh_token}`                          |
| `POST /refresh`  | `Refresh`       | 200           | `{refresh_token}` → **new pair** (old refresh is rotated, replay rejected) |
| `POST /logout`   | `Logout`        | **204** | `{session_id}` (session deactivated)                                              |
| `POST /validate` | `ValidateToken` | 200           | `{access_token}` → `{valid, user_id?, error_message}`                          |

Field rules (Pydantic at the edge + domain rules in the service): `email` = `EmailStr`;
`password` 8–100 chars with letters & digits; `phone?` matches `^\+[1-9][0-9]{6,14}$`.
Errors: 422 invalid input · 409 email already registered · 401 bad credentials / expired or
deactivated session · 404 unknown session.

## 4. Catalog (public) — `/api/v1/catalog` → `catalog.v1.CatalogService`

### Categories

| Method & path                  | gRPC                   | Success       | Notes                                                                                                      |
| ------------------------------ | ---------------------- | ------------- | ---------------------------------------------------------------------------------------------------------- |
| `POST /category`             | `CreateCategory`     | **201** | `{name, parent_id?}` → `Category`                                                                     |
| `GET /category/{id}`         | `ReadCategory`       | 200           | 404 unknown                                                                                                |
| `GET /category?limit&offset` | `ReadListCategories` | 200           | flat list; tree is rebuilt by clients via `parent_id`                                                    |
| `PATCH /category/{id}`       | `UpdateCategory`     | 200           | partial:`{name?, is_active?}`                                                                            |
| `DELETE /category/{id}`      | `DeleteCategory`     | **204** | 409 if it has children or products                                                                         |
| `PATCH /category/{id}/move`  | `MoveCategory`       | 200           | `{parent_id}` — `null` moves to root; recomputes descendant ltree paths; 422 on move-into-own-subtree |

`Category`: `{id, name, parent_id?, path, is_active, created_at, updated_at}` — `path` is the
materialized ltree string (e.g. `"electronics.audio.headphones"`).

### Products (reads)

| Method & path                 | gRPC                 | Success | Notes                              |
| ----------------------------- | -------------------- | ------- | ---------------------------------- |
| `GET /product/{id}`         | `ReadProduct`      | 200     | full `Product` incl. `media[]` |
| `GET /product?limit&offset` | `ReadListProducts` | 200     | `{products[], count}`            |

`Product`: `{id, merchant_id, category_id, title, description?, price, stock, is_active, created_at, updated_at, media[]}`; `media[i]`: `{id, product_id, media_type: "IMAGE"|"VIDEO", url, position, width?, height?, duration_seconds?, file_size}`.
Prices/stock are integers (`>= 0`), `422` on violation; product **writes** live under `/seller`.

## 5. Merchants — `/api/v1/merchants` → `seller.v1.SellerService` (Bearer)

| Method & path         | gRPC                  | Success       | Notes                                                                                                      |
| --------------------- | --------------------- | ------------- | ---------------------------------------------------------------------------------------------------------- |
| `POST /merchants`   | `CreateMerchant`    | **201** | `{name, inn}`; caller (from token) becomes **OWNER**; `inn` = 10 or 12 digits; 409 duplicate INN |
| `GET /merchants/my` | `ListUserMerchants` | 200           | merchants where caller has an active membership                                                            |

`Merchant`: `{id, name, inn, owner_user_id, status, created_at}`.

## 6. Seller catalog — products & media (Bearer + X-Merchant-ID)

All routes resolve `MerchantContext(user_id, merchant_id, role)` first; every call carries
`merchant_id` to catalog, which enforces product ownership (403 otherwise).

### Products

| Method & path                  | gRPC                 | Success       | Notes                                                                           |
| ------------------------------ | -------------------- | ------------- | ------------------------------------------------------------------------------- |
| `POST /products`             | `CreateProduct`    | **201** | `{category_id, title, description?, price, stock}`; owner = `X-Merchant-ID` |
| `GET /products?limit&offset` | `ReadListProducts` | 200           | filtered to the acting merchant (stock table)                                   |
| `GET /products/{id}`         | `ReadProduct`      | 200           | gateway additionally 403s if not owned                                          |
| `PATCH /products/{id}`       | `UpdateProduct`    | 200           | partial update; ownership checked server-side                                   |
| `DELETE /products/{id}`      | `DeleteProduct`    | **204** | cascades media rows                                                             |

### Media

| Method & path                             | gRPC                   | Success       | Flow                                                                                                                                                                              |
| ----------------------------------------- | ---------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST /products/{pid}/media/upload-url` | `GetMediaUploadUrl`  | 200           | `{media_type, content_type, file_size}` → `{upload_url, storage_key, public_url}`; presigned PUT valid ~600 s; 400 on rule violation (mime, size, 3:4, video already exists) |
| `POST /products/{pid}/media/confirm`    | `ConfirmMediaUpload` | **201** | `{media_type, storage_key, public_url, file_size, width?, height?, duration_seconds?}` → `Media`                                                                             |
| `DELETE /products/{pid}/media/{mid}`    | `DeleteMedia`        | **204** | DB row + MinIO object                                                                                                                                                             |
| `PATCH /products/{pid}/media/reorder`   | `ReorderMedia`       | **204** | `{items: [{media_id, position}…]}`                                                                                                                                             |

Upload sequence (binary never touches the gateway):

```
1. POST upload-url → 2. PUT file → MinIO (raw fetch/XHR) → 3. POST confirm → media row created
```

Media rules (validated client-side first, authoritative server-side): images `jpeg|png|bmp`
≤ 10 MB, ratio 3:4 ±0.02, ≥ 900×1200; videos `mp4|mov` ≤ 50 MB ≤ 180 s, **one per product**.

## 7. Worked curl flow: user → merchant → product → image

```bash
BASE=http://localhost:8000/api/v1

# 1. sign up (tokens)
TOKENS=$(curl -s -XPOST $BASE/auth/signup -H 'Content-Type: application/json' \
  -d '{"email":"sara@example.com","phone":"+79991234567","password":"***"}')
ACCESS=$(echo $TOKENS | jq -r .access_token)

# 2. create merchant → remember id
MID=$(curl -s -XPOST $BASE/merchants -H "Authorization: Bearer $ACCESS" \
  -H 'Content-Type: application/json' -d '{"name":"Sara Shop","inn":"7700000001"}' | jq -r .id)

# 3. create a category, then a product under it
CID=$(curl -s -XPOST $BASE/catalog/category -H 'Content-Type: application/json' \
  -d '{"name":"Electronics"}' | jq -r .id)
PID=$(curl -s -XPOST $BASE/seller/products -H "Authorization: Bearer $ACCESS" \
  -H "X-Merchant-ID: $MID" -H 'Content-Type: application/json' \
  -d "{\"category_id\":$CID,\"title\":\"Headphones X\",\"price\":4990,\"stock\":12}" | jq -r .id)

# 4. request presigned URL and push a file straight to MinIO
U=$(curl -s -XPOST $BASE/seller/products/$PID/media/upload-url \
  -H "Authorization: Bearer $ACCESS" -H "X-Merchant-ID: $MID" \
  -H 'Content-Type: application/json' \
  -d '{"media_type":"IMAGE","content_type":"image/jpeg","file_size":245000}')
curl -s -XPUT $(echo $U | jq -r .upload_url) -H 'Content-Type: image/jpeg' --data-binary @photo.jpg

# 5. confirm → media row appears in the product
curl -s -XPOST $BASE/seller/products/$PID/media/confirm \
  -H "Authorization: Bearer $ACCESS" -H "X-Merchant-ID: $MID" \
  -H 'Content-Type: application/json' \
  -d "$(echo $U | jq -c '{media_type:"IMAGE", storage_key:.storage_key, public_url:.public_url, file_size:245000, width:1200, height:1600}')"

curl -s $BASE/catalog/product/$PID | jq '.media'
```

## 8. What the frontend actually calls

Mirror of the route groups above (`frontend/src/shared/api/endpoints.ts`): `/v1/auth/*`,
`/v1/catalog/category*`, `/v1/catalog/product*`, `/v1/merchants*`, `/v1/seller/products*` — plus
the Axios instance adds `Authorization` from the persisted auth store and clears it on 401.

## 9. Breaking-change policy

Contracts are versioned: an incompatible change means a new package (`auth.v2`, path `/api/v2/…`),
never silent edits of `v1`. gRPC services keep backward-compatible field numbers (reserved/deleted
fields are not reused).
