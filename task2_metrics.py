"""
task2_metrics.py — runs N test iterations against the REAL LLM.
tools.py already emits schema_valid_metric, task_success_metric, and
variance_score internally (per call) — this file does NOT re-emit them,
only collects data to compute the batch-level structural_consistency_score.
"""

from tracer_setup import provider, meter_provider, tracer
from tools import tool_similarity_ranker, tool_syntax_inspector, check_structural_consistency
from llm_call import llm_call

N_RUNS = 5

BASELINE_ANSWER = '{"can_answer": 1, "answer": "7"}'

PROMPT = (
    "What is the Square Root of 49? "
    'Respond ONLY with valid JSON in this exact format: '
    '{"can_answer": 1, "answer": "<value>"}. '
    "Do not include any text outside the JSON."
)

structure_scores_this_batch = []


def run_one_test(run_index: int):
    run_id = f"run-{run_index:03d}"
    with tracer.start_as_current_span("test_run") as run_span:
        run_span.set_attribute("run_id", run_id)
        run_span.set_attribute("prompt_version", "v1.0")

        output = llm_call(PROMPT)

        # tool_syntax_inspector already records schema_valid_metric +
        # task_success_metric internally - just use the returned dict here
        result = tool_syntax_inspector(output)
        structure_scores_this_batch.append(result["structure_score"])

        # tool_similarity_ranker already records variance_score internally
        similarity = tool_similarity_ranker(output, BASELINE_ANSWER)

        print(
            f"Run {run_index}: output={output!r} | "
            f"structure_score={result['structure_score']} | "
            f"can_answer={result['can_answer']} | "
            f"similarity={similarity:.3f}"
        )


def run_batch():
    print(f"Running {N_RUNS} test iterations...")
    for i in range(N_RUNS):
        run_one_test(run_index=i)

    consistency = check_structural_consistency(structure_scores_this_batch)
    print(f"Batch structural consistency: {consistency:.3f}")


if __name__ == "__main__":
    run_batch()
    provider.force_flush()
    meter_provider.force_flush()
    print("Batch complete. Real traces + real metrics sent to SigNoz.")