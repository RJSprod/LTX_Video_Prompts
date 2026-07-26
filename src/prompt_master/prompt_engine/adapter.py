from __future__ import annotations

import re

from prompt_master.core.models import PromptRequest
from .brain import SYSTEM, directive
from .imaging import multimodal_content
from .negative import terms as negative_terms


class PromptEngine:
    def build_messages(self, request: PromptRequest) -> list[dict]:
        return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": multimodal_content(directive(request), request.image_data_url)}]

    def build_base_negative(self, request: PromptRequest) -> str:
        terms = negative_terms(request.image_data_url is not None or request.video_mode == "I2V")
        return self._dedupe(terms + self._terms(request.negative_extra))

    def max_tokens(self, request: PromptRequest) -> int:
        return max(384, min(1536, int(320 + request.seconds * 36 + request.dialogue * 2)))

    def clean_positive(self, text: str) -> str:
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.I | re.S)
        text = re.sub(r"```(?:\w+)?|```", "", text)
        text = re.sub(r"^\s*(?:positive prompt|answer|prompt)\s*:\s*", "", text, flags=re.I)
        return re.sub(r"\s+", " ", text).strip().strip('"')

    def clean_smart_negative(self, positive: str, text: str) -> str:
        del positive
        text = re.sub(r"<think>.*?</think>|```(?:\w+)?|```", "", text, flags=re.I | re.S)
        return self._dedupe(self._terms(text))

    def merge_negative(self, request: PromptRequest, smart: str = "") -> str:
        return self._dedupe(self._terms(self.build_base_negative(request)) + self._terms(smart))

    @staticmethod
    def smart_negative_messages(positive: str) -> list[dict]:
        return [{"role": "system", "content": "Return only a short comma-separated list of visual defects to avoid. No explanations."}, {"role": "user", "content": positive}]

    @staticmethod
    def _terms(value: str) -> list[str]:
        return [part.strip(" .-\n\t") for part in re.split(r"[,;\n]", value) if part.strip(" .-\n\t")]

    @staticmethod
    def _dedupe(terms: list[str]) -> str:
        seen: set[str] = set(); output = []
        for term in terms:
            key = term.casefold()
            if key not in seen: seen.add(key); output.append(term)
        return ", ".join(output)
