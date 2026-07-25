import os
import time
from google import genai
from tracer_setup import tracer
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def llm_call(prompt: str, model: str = "gemma-4-26b-a4b-it") -> str:
    """
    Sends a prompt to the target LLM and returns its raw text output.
    Wrapped in a span so latency and output show up in SigNoz.
    """
    with tracer.start_as_current_span("llm_call") as span:
        span.set_attribute("model_name", model)
        span.set_attribute("prompt", prompt)

        start_time = time.time()
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        latency_ms = (time.time() - start_time) * 1000

        output_text = str(response.text)

        span.set_attribute("latency_ms", latency_ms)
        span.set_attribute("output_hash", str(hash(output_text)))
        span.set_attribute("output_len", len(output_text))

        return output_text