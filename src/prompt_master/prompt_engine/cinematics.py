def describe(camera: str, transition: str, pov: str, fps: int) -> str:
    movement = "Keep the camera locked unless movement is motivated" if camera.casefold() == "off" else f"Use a controlled {camera} camera move"
    cut = "one continuous shot" if transition.casefold() == "off" else f"a clearly motivated {transition} transition"
    viewpoint = "objective viewpoint" if pov.casefold() == "off" else f"{pov} point of view"
    return f"{movement}, with precise framing and parallax, at {fps} fps; {viewpoint}; {cut}."
