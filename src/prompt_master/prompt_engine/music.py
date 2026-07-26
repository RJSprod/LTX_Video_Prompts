def describe(kind: str, background: str) -> str:
    if kind.casefold() == "off":
        return "No added score; retain only story-motivated ambient sound and effects."
    detail = f" ({background.strip()})" if background.strip() else ""
    return f"A {kind} score{detail} supports the action without masking dialogue; specify its timing and dynamics."
