import statistics
from tracer_setup import tracer, provider, meter_provider, variance_histogram
from llm_call import llm_call
from tools import tool_syntax_inspector, tool_similarity_ranker
from config import PROMPT, BASELINE, N_RUNS

structure_scores_this_batch = []


def run_one_test(run_index: int):
    run_id = f"run-{run_index:03d}"
    with tracer.start_as_current_span("test_run") as run_span:
        run_span.set_attribute("run_id", run_id)
        run_span.set_attribute("prompt_version", "v1.0")

        with tracer.start_as_current_span("prompt_build"):
            pass

        output = llm_call(PROMPT)

        with tracer.start_as_current_span("parse_validate") as parse_span:
            result = tool_syntax_inspector(output)
            similarity = tool_similarity_ranker(output, BASELINE)

            parse_span.set_attribute("schema_valid", int(result["structure_score"]))
            parse_span.set_attribute("can_answer", result["can_answer"])
            parse_span.set_attribute("similarity_score", similarity)

            structure_scores_this_batch.append(result["structure_score"])


def run_batch():
    print(f"Running {N_RUNS} test iterations...")
    for i in range(N_RUNS):
        run_one_test(run_index=i)

    if len(structure_scores_this_batch) > 1:
        real_variance = statistics.stdev(structure_scores_this_batch)
    else:
        real_variance = 0.0

    variance_histogram.record(real_variance, {"prompt_version": "v1.0"})
    print(f"Batch variance (stddev): {real_variance:.4f}")


if __name__ == "__main__":
    run_batch()
    provider.force_flush()
    meter_provider.force_flush()
    print("Batch complete. Real traces + real metrics sent to SigNoz.")