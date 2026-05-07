import re
import time
import logging
from google import genai
from google.genai import types, errors as genai_errors
from core.config import settings

logger = logging.getLogger("interview.models.gemini")

MODEL       = "gemini-2.5-flash"
TEMPERATURE = 0.0
MAX_RETRY   = 3
RETRY_WAIT  = 5

_client = genai.Client(api_key=settings.gemini_api_key)


def generate_text(messages: list[dict], system: str) -> str:
    """純文字推論，不使用 function calling，內建 retry。

    messages: [{"role": "user"|"model", "content": "..."}]
    """
    contents = [
        types.Content(role=m["role"], parts=[types.Part(text=m["content"])])
        for m in messages
    ]
    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=TEMPERATURE,
    )

    for attempt in range(MAX_RETRY):
        try:
            response = _client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=config,
            )
            return response.text
        except genai_errors.ServerError:
            if attempt < MAX_RETRY - 1:
                logger.warning("Gemini server error, retry %d/%d in %ds", attempt + 1, MAX_RETRY - 1, RETRY_WAIT)
                time.sleep(RETRY_WAIT)
            else:
                raise RuntimeError("Gemini 伺服器持續過載，請稍後再試。")
        except genai_errors.ClientError as e:
            status = getattr(e, "status_code", None) or getattr(e, "code", None)
            if status == 429:
                msg = str(e)
                if "limit: 0" in msg:
                    raise RuntimeError("API 配額已耗盡，請至 aistudio.google.com 確認 API Key。")
                match = re.search(r"'retryDelay': '(\d+)s'", msg)
                wait = int(match.group(1)) if match else 20
                if attempt < 1:
                    logger.warning("Rate limited, waiting %ds before retry", wait)
                    time.sleep(wait)
                else:
                    raise RuntimeError("請求頻率過高，請稍後再試。")
            else:
                raise
