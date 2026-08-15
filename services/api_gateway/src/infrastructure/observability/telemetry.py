from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource


def setup_telemetry(
    service_name: str = "api-gateway", endpoint: str = "http://otel-collector:4317"
) -> None:
    resource = Resource.create({"service.name": service_name})
    metric_exporter = OTLPMetricExporter(
        endpoint=endpoint,
        insecure=True,
    )
    metric_reader = PeriodicExportingMetricReader(
        metric_exporter,
        # export_interval_millis=interval_ms, # default 60 sec
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
