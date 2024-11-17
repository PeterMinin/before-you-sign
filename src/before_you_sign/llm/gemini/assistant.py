from typing import Callable

import google.generativeai as genai
from google.api_core import retry

from before_you_sign.config import Config
from .prompts import SYSTEM_PROMPT, MAIN_PROMPT

MODEL_NAME = "gemini-1.5-flash-002"  # Fixed version for Context Caching


class GeminiAssistant:
    def __init__(self, config: Config, on_retry: Callable[[str], None] | None):
        """
        :param config: dict-like with a key "GOOGLE_API_KEY".
        :param on_retry: (optional) callable to show/log a transient error.
        """

        genai.configure(api_key=config["GOOGLE_API_KEY"])

        on_error = (
            (lambda exc: on_retry(f"Temporary error, will retry. ({exc})"))
            if on_retry
            else None
        )
        self.retry_policy = {
            "retry": retry.Retry(predicate=retry.if_transient_error, on_error=on_error)
        }

    def process(self, document: str) -> str:
        """
        One-step dialog: takes a document, gives the final result.

        :param document: document text.

        :returns: response, including the summary and intermediate steps.
        """
        model = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(temperature=0),
        )
        response = model.generate_content([MAIN_PROMPT, document])
        return response.text
