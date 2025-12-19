import os
import time
from groq import Groq, RateLimitError, APIError

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "openai/gpt-oss-120b"

def call_llm(system_prompt: str, user_content: str) -> str:
    max_retries = 3
    backoff_seconds = 2.0

    last_error = None

    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.7,
            )
            return resp.choices[0].message.content

        except RateLimitError as e:
            last_error = e
            # Exponential backoff: 2, 4, 8 seconds
            sleep_for = backoff_seconds * (2 ** attempt)
            time.sleep(sleep_for)

        except APIError as e:
            # Transient server-side error: retry similarly
            last_error = e
            sleep_for = backoff_seconds * (2 ** attempt)
            time.sleep(sleep_for)

    # If all retries failed, re-raise the last error so Streamlit shows a clean error
    raise last_error if last_error is not None else RuntimeError("LLM call failed with unknown error")





