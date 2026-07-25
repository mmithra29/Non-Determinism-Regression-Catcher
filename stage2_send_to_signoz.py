"""
Stage 2: Send spans to SigNoz instead of printing them.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Same as before: label for this service
resource = Resource.create({"service.name": "non-determinism-catcher"})

# Same as before: the factory
provider = TracerProvider(resource=resource)

# CHANGED: instead of ConsoleSpanExporter, we now use OTLPSpanExporter
# This sends data to SigNoz running on your machine at port 4317
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

# Same as before
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("harness.stage2")


def fake_llm_call():
    return "the model said something"


def run_one_test():
    with tracer.start_as_current_span("test_run") as run_span:
        run_span.set_attribute("run_id", "demo-001")
        run_span.set_attribute("prompt_version", "v1_baseline")

        with tracer.start_as_current_span("prompt_build") as build_span:
            prompt = "extract the fields from this text"
            build_span.set_attribute("prompt_template_id", "extract_v1")

        with tracer.start_as_current_span("llm_call") as call_span:
            output = fake_llm_call()
            call_span.set_attribute("model_name", "fake-model")
            call_span.set_attribute("output_hash", str(hash(output)))

        with tracer.start_as_current_span("parse_validate") as parse_span:
            is_valid = isinstance(output, str) and len(output) > 0
            parse_span.set_attribute("schema_valid", int(is_valid))


if __name__ == "__main__":
    run_one_test()
    provider.force_flush()
    print("Done. Now check the SigNoz dashboard in your browser.")