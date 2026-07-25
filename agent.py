import os
from google import genai
from google.genai import types
from tracer_setup import tracer, provider, meter_provider
from config import PROMPT, BASELINE
from tracer_setup import tracer, provider
from tools import tool_similarity_ranker, tool_syntax_inspector
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_INSTRUCTION = (
    "You are a strict evaluation judge for LLM outputs. "
    "Given an actual output and a baseline output, use the available tools "
    "to check both structural validity and semantic similarity. "
    "Then summarize your findings clearly, stating both scores."
)


def run_evaluation_agent(actual_text: str, baseline_text: str) -> str:
    """Runs the judge agent, letting it call the real tools, wrapped in a
    parent span so the whole reasoning chain shows up in SigNoz."""

    with tracer.start_as_current_span("evaluation_agent_execution") as span:
        span.set_attribute("actual_text_len", len(actual_text))
        span.set_attribute("baseline_text_len", len(baseline_text))

        response = client.models.generate_content(
            model="gemma-4-26b-a4b-it",
            contents=(
                f"Actual output: {actual_text}\n"
                f"Baseline output: {baseline_text}\n"
                "Evaluate this using your tools and report both scores."
            ),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[tool_similarity_ranker, tool_syntax_inspector],
                temperature=0.0,
            ),
        )

        result_text = str(response.text)
        span.set_attribute("agent_summary", result_text[:200])
        return result_text


from llm_call import llm_call

if __name__ == "__main__":
    print("Running target LLM...")
    actual_output = llm_call(PROMPT)
    print("LLM said:", actual_output)

    baseline = "The Square Root of 49 is 7"

    print("Running evaluation agent...")
    output = run_evaluation_agent(
        actual_text=actual_output,
        baseline_text=BASELINE,
    )
    print("\nAgent result:\n", output)

    provider.force_flush()
    meter_provider.force_flush()
    print("\nDone. Spans sent to SigNoz.")