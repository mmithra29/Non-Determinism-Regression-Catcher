from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from metrics_setup import meter_provider, schema_valid_metric, task_success_metric, variance_score
from llm_call import llm_call
from tools import tool_syntax_inspector, tool_similarity_ranker

resource = Resource.create({"service.name": "non-determinism-catcher"})
trace_provider = TracerProvider(resource=resource)
trace_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer("harness.task2")

BASELINE = "The Square Root of 49 is 7."

def run_test_harness():
    with tracer.start_as_current_span("test_run") as run_span:
        run_span.set_attribute("run_id", "run-002")
        run_span.set_attribute("prompt_version", "v1.0")

        prompt = "What is the Square Root of 49? Answer in one short sentence."
        output = llm_call(prompt)  # CHANGED

        with tracer.start_as_current_span("parse_validate") as parse_span:
            structure_score = tool_syntax_inspector(output)
            similarity = tool_similarity_ranker(output, BASELINE)

            parse_span.set_attribute("schema_valid", int(structure_score))
            parse_span.set_attribute("similarity_score", similarity)

            task_success_metric.add(int(similarity > 0.7), {"prompt_version": "v1.0"})


if __name__ == "__main__":
    print("Starting test run with METRICS...")
    run_test_harness()
    trace_provider.force_flush()
    meter_provider.force_flush()
    print("Task 2 complete! Real traces AND metrics sent to SigNoz.")