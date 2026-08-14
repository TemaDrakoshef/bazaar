# Development


## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/TemaDrakoshef/bazaar.git
cd bazaar

# Copy environment variables
cp .env.example .env

# Build and run all services with Docker Compose
docker compose up -d

# Access the application
# Frontend: http://localhost:3000
# API Gateway: http://localhost:8000
# API Docs: http://localhost:8000/docs


## Install Deps

```bash
uv add redis --package auth-service
uv sync --all-packages
```


## Protobuff + grpc
```bash
protoc --proto_path=protos --python_out=.\services\auth_service\src\generated --pyi_out=.\services\auth_service\src\generated protos/auth/v1/*
uv run python -m grpc_tools.protoc --proto_path=protos --python_out=.\services\auth_service\src\generated --grpc_python_out=.\services\auth_service\src\generated protos/auth/v1/*
```


## Migrations
```bash
cd .\services\{service}\
uv run alembic revision --autogenerate -m "Create Product and Category tables"
```

---