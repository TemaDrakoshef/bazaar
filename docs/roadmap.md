# Bazaar — Roadmap & Known Gaps

> Honest inventory of what the platform **doesn't** do yet, grouped by theme and rough priority.

---

## 1. Commerce core (the marketplace still can't sell)

| Gap                              | State today                                                                     | Next step                                                                                                                 |
| -------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **Server-side cart**       | Zustand store persisted to `localStorage` only; "Place order" button disabled | `cart` service or an `orders` service with guest+user carts                                                           |
| **Orders / checkout**      | nothing                                                                         | new service on the standard template ([services.md](services.md#common-shape)); order lifecycle events drive everything else |
| **Payments**               | nothing                                                                         | provider-agnostic payment service + webhooks via the gateway                                                              |
| **Delivery / fulfillment** | nothing                                                                         | model alongside orders (self-pickup first)                                                                                |
| **Notifications**          | mentioned in old README, absent                                                 | email consumer on order events (needs events first, §4)                                                                  |

## 2. Catalog depth

| Gap                                     | State today                                                                                                                                          | Next step                                                                                                          |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **EAV / dynamic attributes**      | only fixed columns (`title/price/stock…`); the product page renders a fake "Характеристики" block                                   | attribute/attribute-value tables + typed per-category schemas in `catalog_db`                                    |
| **Products filtered by category** | frontend passes `categoryPath`/`search` to `catalogService.getProducts`, but `GET /product` accepts only `limit/offset` (+`merchant_id`) | extend `ListProductsRequest` (category `path` filter via ltree subtree — the query cost is already near-zero) |
| **Search**                        | header search posts `q` to `/catalog`, silently ignored                                                                                          | add `text` filter now; `pg_trgm`/tsvector when volume grows                                                    |
| **Product slug/route stability**  | slug =`title-id` (changing title changes URL)                                                                                                      | real slug column + rename handling, or accept it                                                                   |

## 3. Security & access control

| Gap                                       | State today                                                                                                                                               | Next step                                                                       |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **RBAC (platform roles)**           | no buyer/seller/admin distinction anywhere                                                                                                                | roles in auth or a dedicated identity extension                                 |
| **Unprotected admin routes** ⚠️   | category**writes** (`POST/PATCH/DELETE /api/v1/catalog/category…`) and `validate` are public — `get_current_user_id` exists but isn't wired | put catalog (and media) writes behind auth + role check; keep only reads public |
| **Session validation cost**         | every authenticated request = JWT check +`sessions` DB round-trip                                                                                       | Redis (or in-LRU with TTL) session cache; revocation events                     |
| **CORS**                            | `allow_origins=["*"]`, `allow_credentials=False`                                                                                                      | pin to the real frontend origin in prod                                         |
| **Dev secrets shipped as defaults** | `minioadmin/miniopassword`, Grafana `admin/admin`, `.env.example` passwords                                                                         | prod envs must override; add a preflight check                                  |

## 4. Platform & reliability

| Gap                                               | State today                                                                                                                                       | Next step                                                                                                                      |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Event-driven backbone**                   | all coupling is synchronous gRPC via the gateway (old README overstated Kafka)                                                                    | introduce Kafka on real fan-out (order lifecycle → notifications, search index, cart) — keep sync request/response elsewhere |
| **Distributed tracing**                     | Tempo pipeline commented out in the collector and compose                                                                                         | [observability.md §5](observability.md#5-enabling-distributed-tracing-when-ready)                                                |
| **`auth_service` telemetry**              | no OpenTelemetry wiring (others have it)                                                                                                          | copy catalog's `telemetry.py`                                                                                                |
| **Cross-context integrity**                 | orphan `merchant_id`/`user_id` possible by design ([architecture.md §5](architecture.md#5-identity--cross-service-references-no-fk-across-dbs)) | a periodic reconciler job that reports orphans before they bite                                                                |
| **Catalog migration `downgrade()` order** | first migration drops `products` **before** its CHECK constraints — downgrade-only failure                                               | reorder statements in `2026_08_09_2146-…`                                                                                   |
| **No CI**                                   | quality gates (`ruff`/`mypy`/`pytest`) are manual/README'd                                                                                  | GitHub Actions: unit+lint always, integration with a service-postgres container                                                |
| **Observability hygiene**                   | stray `bazaar-overview copy.json` dashboard; empty `prometheus/rules/`                                                                        | cleanup + first alert rules                                                                                                    |

## 5. Release blockers (before a public demo)

- replace `https://example.com` placeholders (`metadataBase`, sitemap/robots) with the real domain;
- real `.env` secrets + rotated defaults;
- DB published-port cleanup (only seller_db leaks a host mapping);
- pin dependency ranges for prod images (currently `>=` floors everywhere).

## 6. Suggested order

```
P0  auth on catalog writes → search/category filters → server cart → orders(+checkout skeleton)
P1  payments → RBAC → session cache → events backbone (Kafka) → tracing on
P2  EAV attributes → delivery/fulfillment → notifications → reconciler → alerts/CI polish
```

*(P0 = things that make it a usable marketplace, not necessarily the riskiest — the unprotected
catalog writes in §3 should be fixed ahead of everything.)*
