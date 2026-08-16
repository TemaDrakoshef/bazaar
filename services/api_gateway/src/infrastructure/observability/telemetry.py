import logging

from opentelemetry import _logs, metrics
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource


def setup_telemetry(
    service_name: str = "api-gateway",
    service_namespace: str = "bazaar",
    endpoint: str = "http://otel-collector:4317",
) -> None:
    resource = Resource.create({
        "service.name": service_name,
        "service.namespace": service_namespace,
    })
    setup_metrics(resource, endpoint)
    setup_logs(resource, endpoint)


def setup_metrics(resource: Resource, endpoint: str) -> None:
    metric_exporter = OTLPMetricExporter(
        endpoint=endpoint,
        insecure=True,
    )

    metric_reader = PeriodicExportingMetricReader(
        metric_exporter,
        # export_interval_millis=interval_ms, # default 60 sec
    )

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )

    metrics.set_meter_provider(meter_provider)


def setup_logs(
    resource: Resource,
    endpoint: str,
) -> None:
    log_exporter = OTLPLogExporter(
        endpoint=endpoint,
        insecure=True,
    )

    logger_provider = LoggerProvider(
        resource=resource,
    )

    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    _logs.set_logger_provider(logger_provider)

    otel_handler = LoggingHandler(
        level=logging.NOTSET,
        logger_provider=logger_provider,
    )

    logging.getLogger().addHandler(otel_handler)
