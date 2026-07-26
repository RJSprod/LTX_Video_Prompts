from prompt_master.core.models import PromptRequest
from prompt_master.prompt_engine.adapter import PromptEngine


def test_real_engine_controls_interact():
    request = PromptRequest(
        "A violinist performs on a rain-soaked rooftop",
        seconds=12,
        style="cinematic",
        camera="dolly",
        transition="dissolve",
        wardrobe="red wool coat",
        accent="irish",
        music="orchestral",
    )
    text = PromptEngine().build_messages(request)[1]["content"]
    for expected in ("violinist", "0-3s", "dolly", "dissolve", "red wool coat", "Irish", "orchestral"):
        assert expected in text


def test_image_is_one_multimodal_user_message():
    messages = PromptEngine().build_messages(PromptRequest("Animate it", image_data_url="data:image/jpeg;base64,AA==", video_mode="I2V"))
    assert len(messages) == 2
    assert [part["type"] for part in messages[1]["content"]] == ["text", "image_url"]
    assert messages[1]["content"][1]["image_url"]["url"].startswith("data:image/jpeg;base64,")


def test_negative_is_comprehensive_and_deduplicated():
    engine = PromptEngine(); request = PromptRequest("x", video_mode="I2V", negative_extra="logo, bespoke flaw")
    negative = engine.merge_negative(request, "flicker, bespoke flaw, new defect")
    assert negative.casefold().count("logo") == 1
    assert negative.casefold().count("bespoke flaw") == 1
    assert "reference image mismatch" in negative and "new defect" in negative
