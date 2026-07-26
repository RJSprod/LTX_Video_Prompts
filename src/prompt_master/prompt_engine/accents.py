ACCENT_GUIDANCE = {
    "off": "Use a natural voice appropriate to the character and setting.",
    "american": "Use an authentic General American accent",
    "british": "Use an authentic contemporary British accent",
    "australian": "Use an authentic Australian accent",
    "irish": "Use an authentic Irish accent",
    "scottish": "Use an authentic Scottish accent",
}


def describe(accent: str, strength: int) -> str:
    base = ACCENT_GUIDANCE.get(accent.casefold(), f"Use an authentic {accent} accent")
    return base if accent.casefold() == "off" else f"{base}, at {max(0, min(100, strength))}% intensity."
