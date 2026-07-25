import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from llm_call import llm_call
from tools import tool_syntax_inspector

resource = Resource.create({"service.name": "non-determinism-catcher"})
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("harness.task1")


def run_test_harness():
    with tracer.start_as_current_span("test_run") as run_span:
        run_span.set_attribute("run_id", "run-001")
        run_span.set_attribute("prompt_version", "v1.0")
        run_span.set_attribute("timestamp", time.time())

        with tracer.start_as_current_span("prompt_build") as build_span:
            prompt = "What is the Square Root of 49? Answer in one short sentence."
            build_span.set_attribute("prompt_template_id", "extract_v1")
            build_span.set_attribute("input_hash", str(hash(prompt)))

        output = llm_call(prompt)

        with tracer.start_as_current_span("parse_validate") as parse_span:
            structure_score = tool_syntax_inspector(output)
            parse_span.set_attribute("schema_valid", int(structure_score))


if __name__ == "__main__":
    print("Starting test run...")
    run_test_harness()
    provider.force_flush()
    print("Task 1 complete! Real data sent to SigNoz.")