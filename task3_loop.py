import time
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# 1. Setup Resource
resource = Resource.create({"service.name": "non-determinism-catcher"})

# 2. Setup Traces 
trace_provider = TracerProvider(resource=resource)
trace_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer("harness.task3")

# 3. Setup Metrics 
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("harness.task3")

# 4. Define Custom Metrics 
schema_validity_counter = meter.create_counter("schema_valid_metric", description="Tracks if the output schema is valid (1=pass)")
task_success_counter = meter.create_counter("task_success_metric", description="Tracks if the task was successful (1=pass)")
variance_histogram = meter.create_histogram("variance_score", description="Tracks the variance/drift score of the LLM output")

def run_test_harness(run_number):
    """Runs the mock task and tags it with a specific run_id."""
    
    # We use the run_number to give each run a unique ID in SigNoz
    current_run_id = f"demo-loop-{run_number}"
    
    with tracer.start_as_current_span("test_run") as run_span:
        run_span.set_attribute("run_id", current_run_id)
        run_span.set_attribute("prompt_version", "v1.0")
        
        with tracer.start_as_current_span("prompt_build"):
            time.sleep(0.1) 
            
        with tracer.start_as_current_span("llm_call"):
            time.sleep(0.2) 
            
        with tracer.start_as_current_span("parse_validate") as parse_span:
            is_valid = 1 
            parse_span.set_attribute("schema_valid", is_valid)
            
            # Emit metrics for this specific run
            schema_validity_counter.add(is_valid, {"prompt_version": "v1.0"})
            task_success_counter.add(1, {"prompt_version": "v1.0"})
            
            # Simulating slight variance in output between each run
            simulated_variance = 0.02 + (run_number * 0.01)
            variance_histogram.record(simulated_variance, {"prompt_version": "v1.0"})

if __name__ == "__main__":
    print("Starting 5 consecutive test runs...")
    
    # This loop fires the same prompt 5 times[cite: 1]
    for i in range(1, 6):
        print(f"Executing run {i}/5...")
        run_test_harness(run_number=i)
        time.sleep(0.5)
    
    trace_provider.force_flush()
    meter_provider.force_flush()
    print("Task 3 complete! Multi-run data sent to SigNoz.")