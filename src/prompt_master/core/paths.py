from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    root: Path

    @classmethod
    def discover(cls) -> "AppPaths":
        executable_root = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
        if not getattr(sys, "frozen", False):
            executable_root = Path.cwd()
        marker = executable_root / "install.json"
        if marker.exists():
            configured = Path(json.loads(marker.read_text(encoding="utf-8"))["install_root"])
            return cls(configured.resolve())
        return cls(executable_root)

    @property
    def data(self) -> Path: return self.root / "data"
    @property
    def logs(self) -> Path: return self.root / "logs"
    @property
    def cache(self) -> Path: return self.root / "cache"

    def create_managed_dirs(self) -> None:
        for path in (self.data, self.logs, self.cache / "downloads", self.cache / "temp-images", self.root / "models", self.root / "runtime"):
            path.mkdir(parents=True, exist_ok=True)

    def contained(self, relative: str | Path) -> Path:
        candidate = (self.root / relative).resolve()
        if candidate != self.root.resolve() and self.root.resolve() not in candidate.parents:
            raise ValueError("Path escapes installation root")
        return candidate
