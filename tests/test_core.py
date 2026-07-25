import io, json, zipfile
from pathlib import Path
import pytest
from PIL import Image
from prompt_master.core.config import atomic_write_json, read_json
from prompt_master.core.models import PromptRequest
from prompt_master.imaging.preprocess import image_data_url
from prompt_master.inference.sse import assistant_chunks
from prompt_master.prompt_engine.adapter import PromptEngine
from prompt_master.provisioning.extractor import extract_zip_atomic


def test_multimodal_and_negative_dedup(tmp_path):
    image=tmp_path/"x.png"; Image.new("RGB",(1000,500),"red").save(image); url=image_data_url(image)
    request=PromptRequest("A runner",image_data_url=url,video_mode="I2V",negative_extra="logo, custom")
    content=PromptEngine().build_messages(request)[1]["content"]
    assert content[0]["image_url"]["url"].startswith("data:image/jpeg;base64,")
    negative=PromptEngine().build_base_negative(request); assert negative.lower().count("logo")==1 and "custom" in negative


def test_atomic_json(tmp_path):
    path=tmp_path/"data"/"settings.json"; atomic_write_json(path,{"unicode":"雪"}); assert read_json(path)=={"unicode":"雪"}


def test_sse_ignores_reasoning():
    lines=['data: {"choices":[{"delta":{"reasoning_content":"secret","content":"hello"}}]}','data: [DONE]']
    assert list(assistant_chunks(lines))==["hello"]


def test_zip_slip_rejected(tmp_path):
    archive=tmp_path/"bad.zip"
    with zipfile.ZipFile(archive,"w") as z: z.writestr("../escape",b"bad")
    with pytest.raises(ValueError): extract_zip_atomic(archive,tmp_path/"out")
