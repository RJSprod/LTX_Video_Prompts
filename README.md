# Prompt Master Standalone

## Install and generate

1. Download **PromptMasterSetup.exe** from [GitHub Releases](https://github.com/RJSprod/LTX_Video_Prompts/releases).
2. Run it.
3. Choose the installation folder, GPU, and model.
4. Wait for the verified downloads and text/image validation to finish.
5. Enter text or attach an image.
6. Generate positive and negative prompts.

Windows Qt desktop client which provisions a pinned `llama.cpp`/Gemma runtime and creates LTX-Video 2.3 prompts. Models and runtimes remain beneath the user-selected installation root.

## Development

Requires Python 3.12. Create a development virtual environment, install with `pip install -e .`, and run `prompt-master`. The release build is produced on Windows with `build/build.ps1`; it uses `pyside6-deploy` in directory mode and Inno Setup.

The application owns one `llama-server` process and stops it on exit. Generation streams the positive prompt, creates the full base negative prompt, and optionally asks the model for scene-specific negative terms. Attached images are EXIF-normalized, converted to RGB, resized to 768 pixels, JPEG encoded, and sent in the same multimodal request as the text.

## Release manifest

Production builds must include `src/prompt_master/release-manifest.json`. Each entry is immutable and contains `component_id`, a version-pinned HTTPS `url`, exact `size`, SHA-256, `destination`, and `version`. Required IDs are `llama-runtime`, `model-Q4_K_M`, `model-Q6_K_P`, `model-Q8_0`, and `mmproj`. The setup wizard rejects missing, zero-size, malformed, or `latest` entries rather than downloading an unverified artifact. Publisher-controlled model artifacts are deliberately not represented by fabricated hashes.
