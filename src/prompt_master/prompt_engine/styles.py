STYLE_GUIDANCE = {
    "off": "Use a coherent photoreal visual treatment unless the intent specifies otherwise.",
    "cinematic": "Use cinematic production design, motivated lighting, rich tonal separation, and natural film texture.",
    "documentary": "Use grounded observational realism, available light, and credible unstaged detail.",
    "anime": "Use polished anime rendering, deliberate line work, expressive animation, and stable character design.",
}


def describe(style: str) -> str:
    return STYLE_GUIDANCE.get(style.casefold(), f"Render consistently in a {style} visual style.")
