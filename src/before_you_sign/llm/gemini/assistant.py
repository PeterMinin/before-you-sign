import dataclasses
import json
from pathlib import Path
from typing import Callable

import google.generativeai as genai
from google.api_core import retry
from google.generativeai.caching import CachedContent
from google.generativeai.types import generation_types

from before_you_sign.config import Config

from ..api import Metadata, Score, Summary
from . import prompts

MODEL_NAME = "gemini-1.5-flash-002"  # Fixed version for Context Caching


class GeminiAssistant:
    """
    Usage:

        metadata = assistant.start(document)
        summary, thoughts = assistant.summarize(metadata)
        ...
        assistant.finalize()  # Optional, but can reduce costs
    """

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

        self.base_generation_config = genai.GenerationConfig(temperature=0)
        self.cached_content = None

    def start(self, document: str) -> Metadata:
        """
        Preprocess a new document.
        """
        self.finalize()
        self.cached_content = CachedContent.create(
            MODEL_NAME,
            system_instruction=prompts.SYSTEM_PROMPT,
            contents=[document],
        )
        self._log_file(str(self.cached_content), "cached_content.txt")
        self._log_file(prompts.SYSTEM_PROMPT, "system_prompt.txt")
        self._log_file(document, "document.md")

        metadata: Metadata = self._generate_metadata(self.cached_content)
        return metadata

    def summarize(self, metadata: Metadata) -> tuple[Summary, str]:
        """
        Finish the processing started with `start()`.
        """
        assert self.cached_content
        thoughts: str = self._generate_thoughts(self.cached_content, metadata)
        summary: Summary = self._generate_summary(self.cached_content, thoughts)
        return summary, thoughts

    def finalize(self):
        """
        Free resources.
        Can reduce costs, but there is also auto-removal on a timeout.
        """
        if self.cached_content:
            self.cached_content.delete()
            self.cached_content = None

    def _generate_metadata(self, cached_content: CachedContent) -> Metadata:
        """
        Runs a structured prompt on the doc.
        """
        generation_config = dataclasses.replace(
            self.base_generation_config,
            response_mime_type="application/json",
            response_schema=Metadata,
        )
        generation_config = self._force_required_fields(generation_config)
        model = genai.GenerativeModel.from_cached_content(
            cached_content, generation_config=generation_config
        )
        self._log_file(str(model), "metadata_model.txt")

        prompt = prompts.METADATA_PROMPT
        response = model.generate_content(prompt, request_options=self.retry_policy)
        self._log_file(prompt, "metadata_prompt.txt")
        self._log_file(response.text, "metadata_response.json")

        data = json.loads(response.text)
        metadata = Metadata(**data)
        return metadata

    def _generate_thoughts(self, cached_content: CachedContent, metadata: Metadata) -> str:
        """
        Runs an unstructured prompt on the doc and its metadata.
        """
        model = genai.GenerativeModel.from_cached_content(
            cached_content, generation_config=self.base_generation_config
        )
        self._log_file(str(model), "thoughts_model.txt")

        prompt = prompts.INTERMEDIATE_PROMPT_TEMPLATE.format(
            document_type=metadata.document_type,
            document_language=metadata.document_language,
            service_nature=metadata.service_nature,
        )
        response = model.generate_content(prompt, request_options=self.retry_policy)
        self._log_file(prompt, "thoughts_prompt.txt")
        self._log_file(response.text, "thoughts_response.md")

        return response.text

    def _generate_summary(self, cached_content: CachedContent, thoughts: str) -> Summary:
        """
        Runs a structured prompt on the doc and intermediate thoughts.
        """
        generation_config = dataclasses.replace(
            self.base_generation_config,
            response_mime_type="application/json",
            response_schema=Summary,
        )
        generation_config = self._force_required_fields(generation_config)
        model = genai.GenerativeModel.from_cached_content(
            cached_content, generation_config=generation_config
        )
        self._log_file(str(model), "summary_model.txt")

        prompt_parts = [thoughts, prompts.SUMMARY_PROMPT]
        response = model.generate_content(prompt_parts, request_options=self.retry_policy)
        self._log_file(prompt_parts[-1], "summary_prompt_end.txt")
        self._log_file(response.text, "summary_response.json")

        data = json.loads(response.text)
        data["score"] = Score(data["score"])
        summary = Summary(**data)
        return summary

    @staticmethod
    def _force_required_fields(generation_config) -> dict:
        """
        Workaround for https://github.com/google-gemini/generative-ai-python/issues/560.
        """
        generation_config = generation_types.to_generation_config_dict(generation_config)
        schema = generation_config["response_schema"]
        schema.required = list(schema.properties)
        return generation_config

    def _log_file(self, text: str, name: str):
        path = self.exp_log_dir / name
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
