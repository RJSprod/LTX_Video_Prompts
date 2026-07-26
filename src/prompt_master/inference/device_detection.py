from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

from prompt_master.core.models import GpuInfo


def detect_gpus(timeout: float = 15) -> list[GpuInfo]:
    command = ["nvidia-smi", "--query-gpu=index,uuid,name,memory.total,memory.free,driver_version", "--format=csv,noheader,nounits"]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, check=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    output = []
    for row in csv.reader(result.stdout.splitlines(), skipinitialspace=True):
        if len(row) != 6: continue
        output.append(GpuInfo(int(row[0]), row[1].strip(), row[2].strip(), int(row[3]), int(row[4]), row[5].strip()))
    return output


def recommended_quantization(gpu: GpuInfo) -> str:
    if gpu.name == "NVIDIA GeForce RTX 3090": return "Q4_K_M"
    if gpu.name == "NVIDIA GeForce RTX 5090": return "Q6_K_P"
    raise ValueError(f"Unsupported GPU: {gpu.name}")


def runtime_component_id(gpu: GpuInfo) -> str:
    """Return the independently pinned runtime required by this GPU family."""
    if gpu.name == "NVIDIA GeForce RTX 3090":
        return "llama-runtime-cuda12"
    if gpu.name == "NVIDIA GeForce RTX 5090":
        return "llama-runtime-cuda13"
    raise ValueError(f"Unsupported GPU: {gpu.name}")


def list_llama_devices(executable: Path, physical_index: int, timeout: float = 30) -> tuple[str, str]:
    """Ask llama.cpp for the device identifier/name after restricting visibility.

    llama.cpp has used both ``CUDA0`` and ``CUDA0: <name>``-style output over
    time, so parsing deliberately accepts the identifier wherever it occurs.
    """
    import os
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(physical_index)
    result = subprocess.run(
        [str(executable), "--list-devices"], env=env, capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=timeout,
        check=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    output = "\n".join((result.stdout, result.stderr))
    match = re.search(r"\b(CUDA\d+)\b\s*[:\-]?\s*([^\r\n]*)", output, re.I)
    if not match:
        raise RuntimeError(f"llama-server --list-devices returned no CUDA device:\n{output.strip()}")
    device = match.group(1).upper()
    name = match.group(2).strip(" -:[]") or device
    return device, name
