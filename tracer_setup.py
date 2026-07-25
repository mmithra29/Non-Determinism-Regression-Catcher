"""
tracer_setup.py — ONE shared place that sets up OTel and sends to SigNoz.
Every other file (tools.py, agent.py, etc.) imports `tracer` from here.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

resource = Resource.create({"service.name": "non-determinism-catcher"})
provider = TracerProvider(resource=resource)

otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

trace.set_tracer_provider(provider)

# Any file that does `from tracer_setup import tracer` gets THIS SAME
# tracer, already wired to send data to SigNoz.
tracer = trace.get_tracer("non-determinism-catcher")