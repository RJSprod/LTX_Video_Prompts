from __future__ import annotations

import csv
import subprocess

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
