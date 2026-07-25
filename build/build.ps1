$ErrorActionPreference = "Stop"
python -m pip install --requirement build/requirements-build.txt
pyside6-deploy src/prompt_master/app.py --name PromptMaster --force
if (-not (Get-Command ISCC.exe -ErrorAction SilentlyContinue)) { throw "Inno Setup 6 (ISCC.exe) is required" }
ISCC.exe installer/PromptMaster.iss
