import time
from tracer_setup import tracer, provider
from llm_call import llm_call
from tools import tool_syntax_inspector
from config import PROMPT


def run_test_harness():
    with tracer.start_as_current_span("test_run") as run_span:
        run_span.set_attribute("run_id", "run-001")
        run_span.set_attribute("prompt_version", "v1.0")
        run_span.set_attribute("timestamp", time.time())

        with tracer.start_as_current_span("prompt_build") as build_span:
            build_span.set_attribute("prompt_template_id", "extract_v1")
            build_span.set_attribute("input_hash", str(hash(PROMPT)))

        output = llm_call(PROMPT)

        with tracer.start_as_current_span("parse_validate") as parse_span:
            result = tool_syntax_inspector(output)  # CHANGED: now a dict
            parse_span.set_attribute("schema_valid", int(result["structure_score"]))
            parse_span.set_attribute("can_answer", result["can_answer"])


if __name__ == "__main__":
    print("Starting test run...")
    run_test_harness()
    provider.force_flush()
    print("Task 1 complete! Real data sent to SigNoz.")