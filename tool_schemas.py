"""
tool_schemas.py — describes your tools in the format the LLM needs
to understand it can call them (OpenAI function-calling format).
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "tool_similarity_ranker",
            "description": "Compares an actual output against a baseline output and returns a semantic similarity score between 0 and 1.",
            "parameters": {
                "type": "object",
                "properties": {
                    "actual_text": {"type": "string", "description": "The output being evaluated"},
                    "baseline_text": {"type": "string", "description": "The golden/expected output to compare against"},
                },
                "required": ["actual_text", "baseline_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_syntax_inspector",
            "description": "Checks whether a given output is valid JSON and returns a structure score (1.0 valid, 0.0 broken).",
            "parameters": {
                "type": "object",
                "properties": {
                    "raw_output": {"type": "string", "description": "The raw text output to check"},
                },
                "required": ["raw_output"],
            },
        },
    },
]