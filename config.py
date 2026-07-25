BASE_QUESTION = "What is the Square Root of 49?"
BASELINE = "The Square Root of 49 is 7"

JSON_INSTRUCTION = (
    'Respond ONLY with valid JSON in this exact shape, no other text: '
    '{"can_answer": 1 or 0, "answer": "<your short answer>"}. '
    'Use can_answer=1 if you are able to answer, 0 if you cannot.'
)

PROMPT = f"{BASE_QUESTION} {JSON_INSTRUCTION}"

N_RUNS = 5