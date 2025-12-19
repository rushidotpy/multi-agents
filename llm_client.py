import os
import time
import re
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
            msg = str(e)

            # 1) If it's a daily tokens-per-day (TPD) limit, do NOT retry
            if "tokens per day (TPD)" in msg or "Tokens per day" in msg:
                raise RuntimeError(
                    "Daily token limit reached for this Groq API key. "
                    "Please try again later or upgrade your plan."
                )

            # 2) Otherwise treat as short-term rate limit (TPM/RPM): retry with backoff
            # Try to extract 'try again in Xs' if present
            m = re.search(r"try again in ([0-9.]+)s", msg)
            if m:
                sleep_for = float(m.group(1))
            else:
                sleep_for = backoff_seconds * (2 ** attempt)

            time.sleep(sleep_for)
            last_error = e

        except APIError as e:
            # Transient server-side error: retry with exponential backoff
            last_error = e
            sleep_for = backoff_seconds * (2 ** attempt)
            time.sleep(sleep_for)

    # If all retries failed, re-raise the last error so Streamlit shows a clean error
    raise last_error if last_error is not None else RuntimeError("LLM call failed with unknown error")
