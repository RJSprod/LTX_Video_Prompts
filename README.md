# Prompt Master Standalone

Windows Qt desktop client which provisions a pinned `llama.cpp`/Gemma runtime and creates LTX-Video 2.3 prompts. Models and runtimes remain beneath the user-selected installation root.

## Development

Requires Python 3.12. Create a development virtual environment, install with `pip install -e .`, and run `prompt-master`. The release build is produced on Windows with `build/build.ps1`; it uses `pyside6-deploy` in directory mode and Inno Setup.

The checked-in release manifest intentionally rejects incomplete component metadata. Runtime archive and projector size metadata must be filled with values from the release publisher before a production build.
