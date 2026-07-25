import time
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# NEW IMPORTS FOR METRICS
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# 1. Setup Resource (Shared by both Traces and Metrics)
resource = Resource.create({"service.name": "non-determinism-catcher"})

# 2. Setup Traces (Exactly the same as Task 1)
trace_provider = TracerProvider(resource=resource)
trace_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer("harness.task2")

# 3. Setup Metrics (NEW)
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("harness.task2")

# 4. Define Custom Metrics (NEW)
# Counters just add up numbers (great for counting how many times a test passed)
schema_validity_counter = meter.create_counter(
    "schema_valid_metric",
    description="Tracks if the output schema is valid (1=pass)"
)
task_success_counter = meter.create_counter(
    "task_success_metric",
    description="Tracks if the task was successful (1=pass)"
)
# Histograms track distributions (great for measuring variance or latency)
variance_histogram = meter.create_histogram(
    "variance_score",
    description="Tracks the variance/drift score of the LLM output"
)

def run_test_harness():
    with tracer.start_as_current_span("test_run") as run_span:
        run_span.set_attribute("run_id", run_id)
        run_span.set_attribute("prompt_version", "v1.0")
        
        with tracer.start_as_current_span("prompt_build"):
            time.sleep(0.1) 
            
        with tracer.start_as_current_span("llm_call"):
            time.sleep(0.5) 
            
        with tracer.start_as_current_span("parse_validate") as parse_span:
            is_valid = 1 
            parse_span.set_attribute("schema_valid", is_valid)
            
            # --- EMIT METRICS HERE ---
            # We record a '1' because it passed, and tag it with the prompt version
            schema_validity_counter.add(is_valid, {"prompt_version": "v1.0"})
            task_success_counter.add(1, {"prompt_version": "v1.0"})
            # Simulating a variance/drift score (e.g., 0.05 drift)
            variance_histogram.record(0.05, {"prompt_version": "v1.0"})
            time.sleep(0.1)

if __name__ == "__main__":
    print("Starting test run with METRICS...")
    run_test_harness()
    
    # Force flush both to ensure they send before the script closes
    trace_provider.force_flush()
    meter_provider.force_flush()
    print("Task 2 complete! Traces AND Metrics sent to SigNoz.")