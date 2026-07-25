"""
test_tools.py — quick manual test, now also confirms spans reach SigNoz.
"""

from tools import tool_similarity_ranker, tool_syntax_inspector
from tracer_setup import provider

score = tool_similarity_ranker(
    actual_text="The cat sat on the mat.",
    baseline_text="A cat was sitting on a mat."
)
print("Similarity score:", score)

score2 = tool_syntax_inspector('{"name": "test", "value": 5}')
print("Valid JSON score:", score2)

score3 = tool_syntax_inspector('this is not json { broken')
print("Broken JSON score:", score3)

# Force any pending spans to actually be sent to SigNoz before exiting
provider.force_flush()
print("Spans flushed to SigNoz. Check the Traces tab.")