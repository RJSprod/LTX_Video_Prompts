# Prompt Master Standalone

## Install and generate

1. Download **PromptMasterSetup.exe** from [GitHub Releases](https://github.com/RJSprod/LTX_Video_Prompts/releases).
2. Run it.
3. Choose the installation folder, GPU, and model.
4. Wait for the verified downloads and text/image validation to finish.
5. Enter text or attach an image.
6. Generate positive and negative prompts.

Windows Qt desktop client which provisions a pinned `llama.cpp`/Gemma runtime and creates LTX-Video 2.3 prompts. Models and runtimes remain beneath the user-selected installation root.

## Prompt engine

The prompt engine is a direct port of [Prompt Master LD](https://github.com/Brojakhoeman/Prompt-Master-LD),
not a reimplementation. The upstream modules are vendored under
`src/prompt_master/prompt_engine/upstream/`; 14 of the 15 are byte-identical,
and the single approved difference is recorded in `UPSTREAM_DIFF_NOTES.md`.

`prompt_engine/adapter.py` is a thin translation layer — it contains no prompt
text. `prompt_engine/options.py` builds every UI dropdown from the upstream
constants, so a control cannot drift from the engine that consumes its value:
47 accents, 35 music genres, 20 visual styles, 10 cameras, 10 transitions, 3
accent strengths and 3 output formats.

Parity is enforced by three checks — see `PARITY_REPORT.md` for the numbers:

```bash
python -m pytest tests/                                        # ported upstream self-test
python tools/compare_upstream_engine.py --upstream <checkout>  # output-level parity
python tools/check_upstream_sync.py     --upstream <checkout>  # file-level integrity
```

## Development

Requires Python 3.12. Create a development virtual environment, install with `pip install -e .`, and run `prompt-master`. The release build is produced on Windows with `build/build.ps1`; it uses `pyside6-deploy` in directory mode and Inno Setup.

The application owns one `llama-server` process and stops it on exit. Generation streams the positive prompt, creates the full base negative prompt, and optionally asks the model for scene-specific negative terms. Attached images are EXIF-normalized, converted to RGB, resized to 768 pixels, JPEG encoded, and sent in the same multimodal request as the text.

## Release manifest

Production builds include `src/prompt_master/release-manifest.json`. Each immutable entry contains a `component_id`, version-pinned HTTPS `url`, SHA-256, `destination`, and `version`; `size` is exact when the publisher supplied it and otherwise `null`, in which case the SHA-256 remains mandatory. Runtime program and CUDA DLL archives are separate entries and are combined during installation. Supported models are Q4_K_M (RTX 3090 default), Q6_K_P (RTX 5090 default), and optional Q8_K_P; all use the pinned f16 vision projector. The setup wizard rejects malformed hashes and `latest` URLs rather than downloading an unverified artifact.
