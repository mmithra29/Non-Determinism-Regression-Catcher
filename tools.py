import json
from sentence_transformers import SentenceTransformer, util
from tracer_setup import (
    tracer,
    schema_validity_counter,
    task_success_counter,
    variance_histogram,
    structural_consistency_histogram,
)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def tool_similarity_ranker(actual_text: str, baseline_text: str) -> float:
    with tracer.start_as_current_span("tool_similarity_ranker") as span:
        vec_a = embedding_model.encode(actual_text, convert_to_tensor=True)
        vec_b = embedding_model.encode(baseline_text, convert_to_tensor=True)
        similarity_score = util.cos_sim(vec_a, vec_b).item()
        drift_score = 1.0 - similarity_score

        span.set_attribute("similarity_score", similarity_score)
        span.set_attribute("drift_score", drift_score)
        variance_histogram.record(drift_score, {"prompt_version": "v1.0"})
        return similarity_score


def tool_syntax_inspector(raw_output: str) -> dict:
    """
    Checks if raw_output matches the expected JSON schema:
    {"can_answer": 0 or 1, "answer": "..."}

    - schema_valid_metric: 1 if it's valid JSON at all (structure check)
    - task_success_metric: 1 if the model itself reported can_answer=1
      (task-appropriate check — fixes Row 1, Option B)
    """
    with tracer.start_as_current_span("tool_syntax_inspector") as span:
        structure_score = 0.0
        can_answer = 0
        try:
            parsed = json.loads(raw_output)
            structure_score = 1.0
            can_answer = int(parsed.get("can_answer", 0))
        except (json.JSONDecodeError, ValueError, AttributeError):
            structure_score = 0.0
            can_answer = 0

        span.set_attribute("structure_score", structure_score)
        span.set_attribute("can_answer", can_answer)

        schema_validity_counter.add(int(structure_score), {"prompt_version": "v1.0"})
        task_success_counter.add(can_answer, {"prompt_version": "v1.0"})

        return {"structure_score": structure_score, "can_answer": can_answer}


def check_structural_consistency(structure_scores: list[float]) -> float:
    with tracer.start_as_current_span("check_structural_consistency") as span:
        if not structure_scores:
            return 0.0
        consistency_ratio = sum(structure_scores) / len(structure_scores)
        span.set_attribute("n_runs", len(structure_scores))
        span.set_attribute("consistency_ratio", consistency_ratio)
        structural_consistency_histogram.record(consistency_ratio, {"prompt_version": "v1.0"})
        return consistency_ratio