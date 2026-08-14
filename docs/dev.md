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

## Observability

The project includes a full observability stack (Prometheus, Loki, Tempo,
Grafana, Alertmanager) driven by the OpenTelemetry Collector. Service telemetry
is emitted over a single OTLP endpoint and routed by the collector to the
right backend — no per-service exporter plumbing required.

See [`infrastructure/observability/README.md`](infrastructure/observability/README.md)
for the architecture and ports.

### Adding observability to a new service

1. **Dependencies** (`pyproject.toml`):

   ```toml
   opentelemetry-api = "*"
   opentelemetry-sdk = "*"
   opentelemetry-exporter-otlp = "==1.*"
   opentelemetry-semconv = "==0.50.*"        # pin matching SDK 1.28.x
   opentelemetry-instrumentation-fastapi = "*"
   opentelemetry-instrumentation-sqlalchemy = "*"
   opentelemetry-instrumentation-requests = "*"
   ```

 2. **Telemetry bootstrap** (pattern adapted from
    `services/auth_service/src/core/telemetry.py` or
    `services/*/src/infrastructure/observability/telemetry.py`):

       ```python
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk._logs import LoggingHandler, LoggerProvider
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    import logging

    def setup_telemetry():
        resource = Resource.create({
            "service.name": "my-service",
            # NOTE: semconv has no DEPLOYMENT_ENVIRONMENT_NAME, use the
            # string form of the resource attribute key.
            "deployment.environment.name": "dev",
        })
        tp = TracerProvider(resource=resource)
        tp.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(tp)

        reader = PeriodicExportingMetricReader(OTLPMetricExporter())
        metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))

        lp = LoggerProvider(resource=resource)
        lp.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
        logging.root.addHandler(LoggingHandler(level=logging.INFO, logger_provider=lp))
        logging.root.setLevel(logging.INFO)
    ```

3. **Environment** (`.env.example`):

   ```dotenv
   OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
   OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
   OTEL_SERVICE_NAME=my-service
   OTEL_ENABLED=true
   OTEL_DEPLOYMENT_ENVIRONMENT=dev
    OTEL_SERVICE_VERSION=0.1.0
   ```

   > The services default to `http/protobuf` on port `:4318`. Switch to
   > `grpc` on `:4317` only if your collector gateway prefers gRPC.

4. **Instrument your code**
   - FastAPI: `FastAPIInstrumentor.instrument_app(app)` in `app.py`.
   - gRPC server: wrap with `aio_server_interceptor()` (see `src/server.py`);
     the api_gateway gRPC client uses `GrpcAioInstrumentorClient().instrument()`
     globally.
   - SQLAlchemy: `SQLAlchemyInstrumentor().instrument(engine.sync_engine)`.
   - AsyncPG: `AsyncPGInstrumentor().instrument()`.
   - Emit business metrics with the meter (`counter.add(1, {...})`) and log with
     JSON so every line carries `trace_id`/`span_id` for Loki↔Tempo correlation.

5. **Validate** — `uv run infrastructure/scripts/validate-configs.py`.

### Observability on Kubernetes

Deploy the whole stack with:

```bash
kubectl apply -k infrastructure/kubernetes/observability
```

After changing any observability config, refresh its K8s copy and re-apply:

```bash
sh infrastructure/kubernetes/observability/sync-configs.sh
kubectl apply -k infrastructure/kubernetes/observability
```