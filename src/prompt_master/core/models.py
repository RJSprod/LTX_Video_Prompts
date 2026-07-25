from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PromptRequest:
    intent: str
    image_data_url: str | None = None
    video_mode: str = "T2V"
    pov: str = "off"
    accent: str = "off"
    accent_strength: int = 50
    dialogue: int = 20
    wardrobe: str = ""
    undress: bool = False
    camera: str = "off"
    transition: str = "off"
    music: str = "off"
    music_background: str = ""
    lexicon: str = "natural"
    output_format: str = "flowing"
    fps: int = 24
    seconds: float = 12.0
    style: str = "off"
    seed: int = -1
    negative_extra: str = ""
    smart_negative: bool = True
    output_width: int = 1920
    output_height: int = 1080


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
