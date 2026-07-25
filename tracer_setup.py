from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

resource = Resource.create({"service.name": "non-determinism-catcher"})

# --- Traces ---
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True, timeout=5)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("non-determinism-catcher")

# --- Metrics ---
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True, timeout=5)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("non-determinism-catcher")

schema_validity_counter = meter.create_counter(
    "schema_valid_metric", description="1 if output was valid JSON, else 0"
)
task_success_counter = meter.create_counter(
    "task_success_metric", description="1 if the model reported can_answer=1"
)
variance_histogram = meter.create_histogram(
    "variance_score", description="Semantic drift vs baseline"
)
structural_consistency_histogram = meter.create_histogram(
    "structural_consistency_score",
    description="Fraction of N runs that were structurally valid JSON",
)