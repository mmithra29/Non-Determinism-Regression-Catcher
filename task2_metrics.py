"""
task2_metrics.py — runs N test iterations, using REAL checks, real metrics.
"""

import time
import statistics
from tracer_setup import (
    tracer,
    schema_validity_counter,
    task_success_counter,
    variance_histogram,
    provider,
    meter_provider,
)
from tools import tool_syntax_inspector

N_RUNS = 5
similarity_scores_this_batch = []  # collect for real variance calc


def fake_llm_call(run_number: int) -> str:
    # TODO: replace with real LLM call (Ollama/Gemini) when ready
    # returning different outputs to simulate real variation
    outputs = [
        '{"answer": 7}',
        '{"answer": 7}',
        'the answer is seven',       # structurally broken on purpose
        '{"answer": 7}',
        '{"answer": "7"}',
    ]
    return outputs[run_number % len(outputs)]


def run_one_test(run_index: int):
    run_id = f"run-{run_index:03d}"
    with tracer.start_as_current_span("test_run") as run_span:
        run_span.set_attribute("run_id", run_id)
        run_span.set_attribute("prompt_version", "v1.0")

        with tracer.start_as_current_span("prompt_build"):
            time.sleep(0.05)

        with tracer.start_as_current_span("llm_call"):
            output = fake_llm_call(run_index)
            time.sleep(0.1)

        with tracer.start_as_current_span("parse_validate") as parse_span:
            structure_score = tool_syntax_inspector(output)
            parse_span.set_attribute("schema_valid", structure_score)

            schema_validity_counter.add(int(structure_score), {"prompt_version": "v1.0"})
            task_success_counter.add(int(structure_score), {"prompt_version": "v1.0"})

            similarity_scores_this_batch.append(structure_score)


def run_batch():
    print(f"Running {N_RUNS} test iterations...")
    for i in range(N_RUNS):
        run_one_test(run_index=i)

    if len(similarity_scores_this_batch) > 1:
        real_variance = statistics.stdev(similarity_scores_this_batch)
    else:
        real_variance = 0.0

    variance_histogram.record(real_variance, {"prompt_version": "v1.0"})
    print(f"Batch variance (stddev): {real_variance:.4f}")


if __name__ == "__main__":
    run_batch()
    provider.force_flush()
    meter_provider.force_flush()
    print("Batch complete. Real traces + real metrics sent to SigNoz.")