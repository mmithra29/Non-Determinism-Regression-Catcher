import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# 1. Setup Connection to the local SigNoz Collector
resource = Resource.create({"service.name": "non-determinism-catcher"})
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("harness.task1")

def run_test_harness():
    """Runs the mock task and wraps steps in OTel spans."""
    
    # 2. Root Span: test_run
    with tracer.start_as_current_span("test_run") as run_span:
        # Attributes for the root span
        run_span.set_attribute("run_id", "run-001")
        run_span.set_attribute("prompt_version", "v1.0")
        run_span.set_attribute("model_name", "mock-local-model")
        run_span.set_attribute("temperature", 0.7)
        run_span.set_attribute("timestamp", time.time())
        
        # 3. Child Span 1: prompt_build
        with tracer.start_as_current_span("prompt_build") as build_span:
            dummy_prompt = "Extract user details from text."
            # Attributes for prompt construction step
            build_span.set_attribute("prompt_template_id", "extract_user_v1")
            build_span.set_attribute("input_hash", str(hash(dummy_prompt)))
            time.sleep(0.1) # Simulating a tiny bit of processing time
            
        # 4. Child Span 2: llm_call
        with tracer.start_as_current_span("llm_call") as call_span:
            start_time = time.time()
            time.sleep(0.5) # Simulating waiting for the LLM to reply
            dummy_output = '{"name": "John", "age": 30}'
            latency = (time.time() - start_time) * 1000 
            
            # Attributes for the raw model call performance and output
            call_span.set_attribute("model_name", "mock-local-model")
            call_span.set_attribute("latency_ms", latency)
            call_span.set_attribute("token_count", 15)
            call_span.set_attribute("output_hash", str(hash(dummy_output)))
            
        # 5. Child Span 3: parse_validate
        with tracer.start_as_current_span("parse_validate") as parse_span:
            # Simulating a successful JSON parse
            is_valid = 1 
            # Attributes for the structural regression check
            parse_span.set_attribute("schema_valid", is_valid)
            parse_span.set_attribute("parse_error", "none")
            time.sleep(0.1)

if __name__ == "__main__":
    print("Starting test run...")
    run_test_harness()
    # Force flush ensures the data is sent to SigNoz before the script closes
    provider.force_flush()
    print("Task 1 complete! Data sent to the local SigNoz Collector.")