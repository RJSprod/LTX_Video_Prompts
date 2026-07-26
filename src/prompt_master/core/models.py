from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PromptRequest:
    """One generation request, in the vocabulary the upstream engine speaks.

    Every field below carries an upstream key, not a display label, and the
    defaults are upstream's own node defaults (see ``upstream/node.py``
    ``INPUT_TYPES``). The UI maps labels to these values; the adapter passes
    them through untranslated wherever upstream already accepts the value.
    """

    intent: str
    image_data_url: str | None = None
    image_name: str = ""
    # upstream keys: "i2v" | "t2v"
    video_mode: str = "i2v"
    # "off" | "male" | "female"
    pov: str = "off"
    # a key from upstream accents.ACCENT_KEYS
    accent: str = "off"
    # "natural" | "strong" | "thick" — upstream accents.STRENGTHS
    accent_strength: str = "natural"
    # 0-100 dial; upstream brain.talk_pct also accepts legacy strings
    dialogue: int = 20
    # "auto" | "off" | "her" | "him"
    wardrobe: str = "auto"
    undress: bool = False
    # keys from upstream cinematics.CAMERA_KEYS / TRANSITION_KEYS
    camera: str = "off"
    transition: str = "off"
    # "auto" or a key from upstream music.MUSIC_KEYS
    music: str = "off"
    music_bg: bool = False
    # free text: "Name = description" lines, filtered against the intent
    lexicon: str = ""
    # a key from upstream shotscript.FORMATS
    fmt: str = "flowing"
    fps: int = 24
    seconds: float = 12.0
    # a key from upstream styles.STYLE_KEYS
    style: str = "off"
    seed: int = 7
    negative_extra: str = ""
    smart_negative: bool = False
    output_width: int = 704
    output_height: int = 1216


@dataclass(frozen=True, slots=True)
class GpuInfo:
    physical_index: int
    uuid: str
    name: str
    memory_total_mb: int
    memory_free_mb: int
    driver_version: str

    @property
    def supported(self) -> bool:
        return self.name in {"NVIDIA GeForce RTX 3090", "NVIDIA GeForce RTX 5090"}
