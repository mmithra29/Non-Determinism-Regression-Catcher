"""
tracer_setup.py — ONE shared place for BOTH traces and metrics.
Every other file (tools.py, agent.py, task2_metrics.py, etc.) imports
`tracer` and `meter`/counters from here. Never create a second
TracerProvider or MeterProvider anywhere else in the project.
"""

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

resource = Resource.create({"service.name": "non-determinism-catcher"})

# --- Traces setup ---
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True, timeout=5)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("non-determinism-catcher")

# --- Metrics setup ---
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True, timeout=5)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

meter = metrics.get_meter("non-determinism-catcher")

# --- Shared metric instruments (defined ONCE here, imported everywhere) ---
schema_validity_counter = meter.create_counter(
    "schema_valid_metric",
    description="Tracks if the output schema is valid (1=pass)",
)
task_success_counter = meter.create_counter(
    "task_success_metric",
    description="Tracks if the task was successful (1=pass)",
)
variance_histogram = meter.create_histogram(
    "variance_score",
    description="Tracks the variance/drift score across a run batch",
)
structural_consistency_histogram = meter.create_histogram(
    "structural_consistency_score",
    description="Tracks how consistently the output structure holds across a batch of runs",
)