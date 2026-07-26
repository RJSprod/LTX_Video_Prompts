from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PySide6.QtWidgets import (QComboBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QProgressBar, QPushButton, QVBoxLayout, QWizard, QWizardPage)

from prompt_master.core.config import atomic_write_json
from prompt_master.core.models import PromptRequest
from prompt_master.core.paths import AppPaths
from prompt_master.imaging.preprocess import image_data_url
from prompt_master.inference.device_detection import (detect_gpus, recommended_quantization,
    runtime_component_id, list_llama_devices)
from prompt_master.inference.service import InferenceService
from prompt_master.prompt_engine.adapter import PromptEngine
from prompt_master.provisioning.downloader import download
from prompt_master.provisioning.extractor import extract_zips_atomic
from prompt_master.provisioning.manifest import load_manifest


class SetupWizard(QWizard):
    """Provision and validate a complete local runtime; no state is saved early."""

    def __init__(self, paths: AppPaths, parent=None):
        super().__init__(parent); self.paths=paths; self.gpus=[]; self.completed=False
        self.setWindowTitle("Models and Hardware Setup"); self.setOption(QWizard.NoBackButtonOnStartPage)
        self._location_page(); self._hardware_page(); self._model_page(); self._install_page()
        self.currentIdChanged.connect(self._page_changed)

    def _location_page(self):
        page=QWizardPage(); page.setTitle("Installation directory")
        layout=QVBoxLayout(page); layout.addWidget(QLabel("Runtime, model, projector, cache, logs, and setup state remain under this directory."))
        row=QHBoxLayout(); self.location=QLineEdit(str(self.paths.root)); choose=QPushButton("Browse…"); choose.clicked.connect(self._browse); row.addWidget(self.location); row.addWidget(choose); layout.addLayout(row); self.addPage(page)

    def _hardware_page(self):
        page=QWizardPage(); page.setTitle("GPU selection"); layout=QVBoxLayout(page)
        self.hardware_status=QLabel("Open this page to scan with nvidia-smi."); self.gpu=QComboBox(); layout.addWidget(self.hardware_status); layout.addWidget(self.gpu); self.addPage(page)

    def _model_page(self):
        page=QWizardPage(); page.setTitle("Model quality"); form=QFormLayout(page)
        self.quant=QComboBox(); self.quant.addItems(["Q4_K_M", "Q6_K_P", "Q8_K_P"]); self.recommendation=QLabel(); self.recommendation.setWordWrap(True)
        form.addRow("GGUF quantization",self.quant); form.addRow(self.recommendation); self.addPage(page)

    def _install_page(self):
        page=QWizardPage(); page.setTitle("Download, verify, and validate"); layout=QVBoxLayout(page)
        text=QLabel("Finish downloads the pinned llama.cpp runtime, model, and matching vision projector; verifies size and SHA-256; then validates one text and one image request."); text.setWordWrap(True); layout.addWidget(text)
        self.progress=QProgressBar(); self.install_status=QLabel("Ready"); self.install_status.setWordWrap(True); layout.addWidget(self.progress); layout.addWidget(self.install_status); self.addPage(page)

    def _browse(self):
        value=QFileDialog.getExistingDirectory(self,"Installation directory",self.location.text())
        if value: self.location.setText(value)

    def _page_changed(self,index):
        if index == 1:
            self.gpu.clear()
            try: self.gpus=detect_gpus()
            except Exception as exc: self.gpus=[]; self.hardware_status.setText(f"GPU scan failed: {exc}"); return
            supported=[gpu for gpu in self.gpus if gpu.supported]
            for gpu in supported: self.gpu.addItem(f"{gpu.name} — {gpu.memory_total_mb} MiB — {gpu.uuid}",gpu)
            self.hardware_status.setText(f"Found {len(supported)} supported RTX 3090/5090 GPU(s).")
        elif index == 2 and self.gpu.currentData():
            value=recommended_quantization(self.gpu.currentData()); self.quant.setCurrentText(value)
            self.recommendation.setText(f"Recommended for {self.gpu.currentData().name}: {value}")

    def validateCurrentPage(self):
        if self.currentId() == 0:
            root=Path(self.location.text()).expanduser().resolve()
            try: root.mkdir(parents=True,exist_ok=True); probe=root/".write-test"; probe.write_bytes(b""); probe.unlink()
            except OSError as exc: QMessageBox.critical(self,"Invalid directory",str(exc)); return False
            self.paths=AppPaths(root); self.paths.create_managed_dirs()
        elif self.currentId() == 1 and not self.gpu.currentData():
            QMessageBox.critical(self,"Unsupported hardware","Select an NVIDIA GeForce RTX 3090 or RTX 5090."); return False
        elif self.currentId() == 3 and not self.completed:
            try: self._provision()
            except Exception as exc: self.install_status.setText(f"Setup failed: {exc}"); QMessageBox.critical(self,"Setup failed",str(exc)); return False
        return super().validateCurrentPage()

    def _provision(self):
        manifest_path=Path(__file__).resolve().parents[1]/"release-manifest.json"
        components=load_manifest(manifest_path); quant=self.quant.currentText(); gpu=self.gpu.currentData()
        runtime_id=runtime_component_id(gpu)
        ids=(runtime_id,f"{runtime_id}-cudart",f"model-{quant}","mmproj")
        if any(key not in components for key in ids): raise RuntimeError(f"Release manifest has no complete {quant} component set")
        installed={}
        runtime_archives=[]
        for number,key in enumerate(ids):
            component=components[key]; target=self.paths.contained(component.destination); self.install_status.setText(f"Downloading {key}…")
            self.progress.setValue(number*22)
            artifact=download(component,target,lambda done,total,n=number:self.progress.setValue(n*22+int(22*done/total)))
            if key.startswith("llama-runtime-"):
                runtime_archives.append(artifact)
            else: installed["model" if key.startswith("model-") else "mmproj"]=artifact.relative_to(self.paths.root).as_posix()
        runtime_dir=self.paths.root/"runtime"; extract_zips_atomic(runtime_archives,runtime_dir)
        matches=list(runtime_dir.rglob("llama-server.exe"))
        if not matches: raise RuntimeError("Combined runtime archives contain no llama-server.exe")
        installed["runtime"]=matches[0].relative_to(self.paths.root).as_posix()
        device, device_name = list_llama_devices(self.paths.contained(installed["runtime"]), gpu.physical_index)
        state={**installed,"gpu_index":gpu.physical_index,"gpu_uuid":gpu.uuid,"gpu_name":gpu.name,"gpu_device":device,"gpu_device_name":device_name,"quantization":quant,"context_size":16384}
        atomic_write_json(self.paths.data/"setup-state.pending.json",state)
        shutil.copy2(self.paths.data/"setup-state.pending.json",self.paths.data/"setup-state.json")
        service=InferenceService(self.paths)
        try:
            client=service.client(); engine=PromptEngine()
            text_probe=PromptRequest("A red ball rolls across a wooden table",video_mode="t2v",smart_negative=False)
            if not client.stream_chat(engine.build(text_probe).messages,64,1,lambda _:None).strip(): raise RuntimeError("Text validation returned no content")
            from PIL import Image
            probe=self.paths.cache/"temp-images"/"setup-probe.jpg"; Image.new("RGB",(32,32),(220,30,30)).save(probe)
            image_probe=PromptRequest("A red ball rolls across a wooden table",video_mode="i2v",image_data_url=image_data_url(probe),image_name=probe.name,smart_negative=False)
            if not client.stream_chat(engine.build(image_probe).messages,64,1,lambda _:None).strip(): raise RuntimeError("Image validation returned no content")
        except Exception:
            (self.paths.data/"setup-state.json").unlink(missing_ok=True); raise
        finally: service.stop(); (self.paths.data/"setup-state.pending.json").unlink(missing_ok=True)
        self.progress.setValue(100); self.install_status.setText("Runtime, text inference, and image inference validated."); self.completed=True
        bootstrap=Path(sys.executable).resolve().parent if getattr(sys,"frozen",False) else Path.cwd()
        atomic_write_json(bootstrap/"install.json",{"install_root":str(self.paths.root)})
