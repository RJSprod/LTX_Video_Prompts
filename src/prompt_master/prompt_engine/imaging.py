def multimodal_content(text: str, data_url: str | None) -> str | list[dict]:
    if not data_url:
        return text
    return [
        {"type": "text", "text": text + "\nTreat the attached image as binding visual evidence."},
        {"type": "image_url", "image_url": {"url": data_url}},
    ]


def image_data_url(path):
    # Pillow is loaded only when an image is actually attached, keeping the
    # text-only prompt engine usable in lightweight tooling and self-tests.
    from prompt_master.imaging.preprocess import image_data_url as preprocess
    return preprocess(path)


__all__ = ["image_data_url", "multimodal_content"]
