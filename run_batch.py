from config import PROMPT, BASELINE, N_RUNS
from tracer_setup import tracer, provider, meter_provider
from llm_call import llm_call
from tools import tool_syntax_inspector, tool_similarity_ranker, check_structural_consistency

structure_scores_this_batch = []


def run_one(run_index: int):
    run_id = f"run-{run_index:03d}"
    with tracer.start_as_current_span("test_run") as run_span:
        run_span.set_attribute("run_id", run_id)
        run_span.set_attribute("prompt_version", "v1.0")

        output = llm_call(PROMPT)

        with tracer.start_as_current_span("parse_validate") as parse_span:
            result = tool_syntax_inspector(output)
            similarity = tool_similarity_ranker(output, BASELINE)

            parse_span.set_attribute("schema_valid", result["structure_score"])
            parse_span.set_attribute("can_answer", result["can_answer"])
            parse_span.set_attribute("similarity_score", similarity)

            structure_scores_this_batch.append(result["structure_score"])


if __name__ == "__main__":
    print(f"Running {N_RUNS} iterations of the same prompt...")
    for i in range(N_RUNS):
        print(f"Run {i + 1}/{N_RUNS}...")
        run_one(i)

    consistency = check_structural_consistency(structure_scores_this_batch)
    print(f"Structural consistency across {N_RUNS} runs: {consistency:.2f}")

    provider.force_flush()
    meter_provider.force_flush()
    print("Done. All real traces + metrics sent to SigNoz.")