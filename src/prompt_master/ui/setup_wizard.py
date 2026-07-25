from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWizard, QWizardPage


class SetupWizard(QWizard):
    """Guided provisioning shell; concrete download workers are attached by the app."""

    PAGES = [
        ("Welcome", "Prompt Master keeps its runtime, model, cache, and configuration inside the selected installation root."),
        ("Hardware scan", "Scanning NVIDIA GPUs, system RAM, and available disk space runs outside the UI thread."),
        ("GPU selection", "Select a supported RTX 3090 or RTX 5090. The GPU UUID is saved so device reordering is safe."),
        ("Model selection", "Choose the recommended quantization or another compatible option. Q8_K_P is never selected automatically."),
        ("Download summary", "Review exact download and required working-space totals before continuing."),
        ("Download and verification", "Downloads can resume and every completed component is verified with SHA-256."),
        ("Runtime setup", "The selected device, server health, text inference, and multimodal inference are validated."),
        ("Complete", "Setup is saved only after all runtime validation checks succeed."),
    ]

    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Models and Hardware Setup"); self.setOption(QWizard.NoBackButtonOnStartPage)
        for title, description in self.PAGES:
            page=QWizardPage(); page.setTitle(title); layout=QVBoxLayout(page); label=QLabel(description); label.setWordWrap(True); layout.addWidget(label); self.addPage(page)
