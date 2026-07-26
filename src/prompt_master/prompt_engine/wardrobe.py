def describe(value: str, undress: bool) -> str:
    clothing = value.strip() or "wardrobe appropriate to the character, action, and setting"
    continuity = "Show only story-requested clothing changes with physically coherent motion" if undress else "Keep every garment, accessory, material, and color continuous"
    return f"Wardrobe: {clothing}. {continuity} throughout the shot."
