# Bazaar Frontend

Modular monolith of the marketplace's frontend: Next.js (App Router) + TypeScript +
Tailwind CSS + ShadCN UI.

```
src/
├── app/         # routing, SEO, Server Components (page assembly only)
├── modules/
│   ├── auth/    # registration, login, client sessions
│   └── client/  # catalog and shopping cart
└── shared/      # UI Kit (ShadCN), API client, utilities and types
```

## Local launch

```bash
npm ci             # installing dependencies
npm run dev        # http://localhost:3000 (NEXT_PUBLIC_API_URL from .env, default :8000)
npm run build      # production-assembly
npm run lint       # lint
npm run typecheck  # types only
```

## Docker

Multi-stage assembly process (deps → builder → runner) with
Next.js mode `output: "standalone"`: the final image contains only
production-dependencies and runs from an unprivileged user.

```bash
docker compose up --build -d     # build and run: http://localhost:3001
docker compose ps                # status (including healthcheck)
docker compose logs -f frontend  # logs
docker compose down              # stop
```

> External port — **3001** (inside the container, the application listens to 3000).

Default API Gateway URL `http://host.docker.internal:8000 ` (The API is running
on the host). For linking to the API in the docker network:

```bash
FRONTEND_API_URL=http://api_gateway:8000 docker compose up --build -d
```
