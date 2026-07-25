import time
from tracer_setup import tracer, provider, meter_provider
from llm_call import llm_call
from tools import tool_syntax_inspector, tool_similarity_ranker
from config import PROMPT, BASELINE, N_RUNS


def run_test_harness(run_number):
    current_run_id = f"demo-loop-{run_number}"

    with tracer.start_as_current_span("test_run") as run_span:
        run_span.set_attribute("run_id", current_run_id)
        run_span.set_attribute("prompt_version", "v1.0")

        output = llm_call(PROMPT)

        with tracer.start_as_current_span("parse_validate") as parse_span:
            result = tool_syntax_inspector(output)  # CHANGED: dict, not float
            similarity = tool_similarity_ranker(output, BASELINE)

            parse_span.set_attribute("schema_valid", int(result["structure_score"]))
            parse_span.set_attribute("can_answer", result["can_answer"])
            parse_span.set_attribute("similarity_score", similarity)

if __name__ == "__main__":
    print(f"Starting {N_RUNS} consecutive test runs...")
    for i in range(1, N_RUNS + 1):
        print(f"Executing run {i}/{N_RUNS}...")
        run_test_harness(run_number=i)
        time.sleep(0.5)

    provider.force_flush()
    meter_provider.force_flush()
    print("Task 3 complete! Real multi-run data sent to SigNoz.")