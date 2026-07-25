"""
tools.py — Person B's "Hands": deterministic tools the agent will call.
Now emits real metrics to SigNoz, not just trace spans.
"""

import json
from sentence_transformers import SentenceTransformer, util
from tracer_setup import tracer
from metrics_setup import schema_valid_metric, task_success_metric, variance_score

# Load the embedding model once (reused every time, not reloaded per call)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def tool_similarity_ranker(actual_text: str, baseline_text: str) -> float:
    """
    Compares actual_text vs baseline_text.
    Returns a similarity score between 0 (totally different) and 1 (identical meaning).
    """
    with tracer.start_as_current_span("tool_similarity_ranker") as span:
        span.set_attribute("actual_text_len", len(actual_text))
        span.set_attribute("baseline_text_len", len(baseline_text))

        vec_a = embedding_model.encode(actual_text, convert_to_tensor=True)
        vec_b = embedding_model.encode(baseline_text, convert_to_tensor=True)

        similarity_score = util.cos_sim(vec_a, vec_b).item()
        drift_score = 1.0 - similarity_score

        span.set_attribute("similarity_score", similarity_score)
        span.set_attribute("drift_score", drift_score)

        # Emit the real metric to SigNoz (this was missing before)
        variance_score.record(drift_score, {"prompt_version": "v1.0"})

        return similarity_score


def tool_syntax_inspector(raw_output: str) -> float:
    """
    Checks if raw_output is valid JSON.
    Returns 1.0 if valid, 0.0 if broken.
    """
    with tracer.start_as_current_span("tool_syntax_inspector") as span:
        span.set_attribute("raw_output_len", len(raw_output))
        try:
            json.loads(raw_output)
            structure_score = 1.0
        except json.JSONDecodeError:
            structure_score = 0.0

        span.set_attribute("structure_score", structure_score)

        # Emit real metrics to SigNoz
        schema_valid_metric.add(int(structure_score), {"prompt_version": "v1.0"})
        task_success_metric.add(int(structure_score), {"prompt_version": "v1.0"})

        return structure_score