BASE = (
    "worst quality", "low quality", "low resolution", "blurry", "out of focus", "compression artifacts",
    "posterization", "banding", "flicker", "jitter", "strobing", "temporal inconsistency", "identity drift",
    "morphing", "warped face", "asymmetrical eyes", "deformed anatomy", "extra limbs", "missing limbs",
    "bad hands", "fused fingers", "extra fingers", "floating objects", "broken physics", "duplicate subject",
    "unmotivated camera movement", "text", "subtitles", "watermark", "logo",
)


def terms(image_conditioned: bool) -> list[str]:
    result = list(BASE)
    if image_conditioned:
        result.extend(("reference image mismatch", "changed composition", "unmotivated scene change"))
    return result
