from __future__ import annotations

from prompt_master.core.models import PromptRequest
from . import accents, cinematics, music, shotscript, styles, wardrobe
from .hands import HAND_GUIDANCE
from .identity import IDENTITY_GUIDANCE

SYSTEM = """You are Prompt Master LD, an expert shot designer for LTX-Video. Convert the brief and controls into one production-ready positive prompt. Write concrete visible and audible events in chronological order. Specify subject, action, environment, lighting, composition, lens, camera motion, temporal continuity, physics, dialogue and sound. Do not mention controls, resolutions, negative terms, instructions, or the reference image. Do not explain, label, quote, or use markdown. Output only the final prompt."""


def directive(request: PromptRequest) -> str:
    dialogue = "No spoken dialogue" if request.dialogue <= 0 else f"Dialogue occupies about {request.dialogue}% of the shot; write exact spoken words only when supported by the brief"
    format_rule = "Write one flowing cinematic paragraph" if request.output_format.casefold() == "flowing" else f"Use the {request.output_format} output structure"
    return "\n".join((
        f"USER BRIEF: {request.intent.strip()}",
        f"DELIVERY: {request.video_mode}, {request.seconds:g} seconds, {request.output_width}x{request.output_height}, {request.fps} fps.",
        shotscript.timing(request.seconds), styles.describe(request.style),
        cinematics.describe(request.camera, request.transition, request.pov, request.fps),
        IDENTITY_GUIDANCE, HAND_GUIDANCE, wardrobe.describe(request.wardrobe, request.undress),
        f"Speech: {dialogue}. {accents.describe(request.accent, request.accent_strength)}",
        f"Audio: {music.describe(request.music, request.music_background)}",
        f"Language: use a {request.lexicon} lexicon. {format_rule}. Maintain causal, spatial, lighting, and motion continuity.",
    ))
