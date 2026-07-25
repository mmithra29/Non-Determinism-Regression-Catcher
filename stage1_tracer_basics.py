"""
Stage 1: Understand the OTel object model with zero infrastructure.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from llm_call import llm_call

resource = Resource.create({"service.name": "non-determinism-catcher"})
provider = TracerProvider(resource=resource)

console_exporter = ConsoleSpanExporter()
provider.add_span_processor(BatchSpanProcessor(console_exporter))

trace.set_tracer_provider(provider)
tracer = trace.get_tracer("harness.stage1")


def run_one_test():
    with tracer.start_as_current_span("test_run") as run_span:
        run_span.set_attribute("run_id", "demo-001")
        run_span.set_attribute("prompt_version", "v1_baseline")

        with tracer.start_as_current_span("prompt_build") as build_span:
            prompt = "What is the Square Root of 49? Answer in one short sentence."
            build_span.set_attribute("prompt_template_id", "extract_v1")

        output = llm_call(prompt)

        with tracer.start_as_current_span("parse_validate") as parse_span:
            is_valid = isinstance(output, str) and len(output) > 0
            parse_span.set_attribute("schema_valid", int(is_valid))


if __name__ == "__main__":
    run_one_test()
    provider.force_flush()