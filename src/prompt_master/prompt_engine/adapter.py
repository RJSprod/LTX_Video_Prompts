from __future__ import annotations

import re

from prompt_master.core.models import PromptRequest


SYSTEM = """You are Prompt Master LD. Produce only a production-ready LTX-Video 2.3 positive prompt. Describe subject identity, action, environment, lighting, cinematography, camera motion, temporal continuity, and synchronized audio. Never explain your work, use markdown, or emit a negative prompt."""


class PromptEngine:
    def build_messages(self, request: PromptRequest) -> list[dict]:
        details = (
            f"Create a {request.seconds:g}-second {request.video_mode} prompt at {request.fps} fps, "
            f"{request.output_width}x{request.output_height}. Intent: {request.intent}\n"
            f"Style: {request.style}; camera: {request.camera}; transition: {request.transition}; POV: {request.pov}; "
            f"dialogue amount: {request.dialogue}%; accent: {request.accent} ({request.accent_strength}%); "
            f"wardrobe: {request.wardrobe or 'unspecified'}; music: {request.music}; lexicon: {request.lexicon}; "
            f"format: {request.output_format}. Maintain coherent motion and identity across every frame."
        )
        content: str | list[dict]
        if request.image_data_url:
            content = [{"type": "image_url", "image_url": {"url": request.image_data_url}}, {"type": "text", "text": details}]
        else:
            content = details
        return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": content}]

    def build_base_negative(self, request: PromptRequest) -> str:
        terms = ["low quality", "blurry", "compression artifacts", "flicker", "temporal inconsistency", "identity drift", "deformed anatomy", "extra limbs", "bad hands", "warped face", "text", "watermark", "logo"]
        if request.video_mode == "I2V": terms += ["reference image mismatch", "unmotivated scene change"]
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
