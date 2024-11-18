from pathlib import Path
from typing import Callable

import google.generativeai as genai
from google.api_core import retry

from before_you_sign.config import Config

from .prompts import MAIN_PROMPT, SYSTEM_PROMPT

MODEL_NAME = "gemini-1.5-flash-002"  # Fixed version for Context Caching


class GeminiAssistant:
    def __init__(self, config: Config, exp_log_dir: Path, on_retry: Callable[[str], None] | None):
        """
        :param config: dict-like with a key "GOOGLE_API_KEY".
        :param on_retry: (optional) callable to show/log a transient error.
        """
        api_key = config["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)

        self.exp_log_dir = exp_log_dir

        on_error = (
            (lambda exc: on_retry(f"Temporary error, will retry. ({exc})")) if on_retry else None
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
        cached_content = genai.caching.CachedContent.create(
            MODEL_NAME,
            system_instruction=SYSTEM_PROMPT,
            contents=[document],
        )
        self._log_file(str(cached_content), "cached_content.txt")
        self._log_file(SYSTEM_PROMPT, "system_prompt.txt")
        self._log_file(document, "document.md")

        model = genai.GenerativeModel.from_cached_content(
            cached_content, generation_config=genai.GenerationConfig(temperature=0)
        )
        self._log_file(str(model), "model.txt")

        self._log_file(MAIN_PROMPT, "request_prompt.txt")
        response = model.generate_content(MAIN_PROMPT)
        self._log_file(response.text, "response.md")

        cached_content.delete()

        return response.text

    def _log_file(self, text: str, name: str):
        path = self.exp_log_dir / name
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
