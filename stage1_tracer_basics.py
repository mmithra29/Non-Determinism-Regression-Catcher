"""
Stage 1: Understand the OTel object model with zero infrastructure.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.resources import Resource

# 1. Resource: metadata about WHO is producing these traces.
#    Shows up on every span. Useful later when you have multiple services.
resource = Resource.create({"service.name": "non-determinism-catcher"})

# 2. TracerProvider: the factory. One per process, configured once.
provider = TracerProvider(resource=resource)

# 3. Exporter + SpanProcessor: the pipe that ships finished spans somewhere.
#    ConsoleSpanExporter just prints them. Later we swap this ONE line
#    for an OTLP exporter pointing at SigNoz -- nothing else in this
#    file changes. That's the whole design benefit of OTel.
console_exporter = ConsoleSpanExporter()
provider.add_span_processor(BatchSpanProcessor(console_exporter))

# 4. Register this provider as the GLOBAL one for the process
trace.set_tracer_provider(provider)

# 5. Get a Tracer from the provider -- this is what you actually use
tracer = trace.get_tracer("harness.stage1")


def fake_llm_call():
    """Stand-in for a real LLM call. We'll wire this to Ollama/API later."""
    return "the model said something"


def run_one_test():
    # start_as_current_span does TWO things:
    #   (a) creates a span
    #   (b) pushes it onto the "current context" stack, so any span
    #       created INSIDE this `with` block automatically becomes
    #       its CHILD.
    # If you use start_span() instead (no "as_current"), step (b)
    # never happens, and every span you open thinks it has no parent.
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
    provider.force_flush()  # make sure console output prints before exit