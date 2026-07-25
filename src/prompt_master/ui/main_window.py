from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox,QComboBox,QFileDialog,QFormLayout,QHBoxLayout,QLabel,QMainWindow,QMessageBox,QPlainTextEdit,QPushButton,QSpinBox,QDoubleSpinBox,QVBoxLayout,QWidget)

from prompt_master.core.models import PromptRequest
from prompt_master.imaging.preprocess import image_data_url
from prompt_master.prompt_engine.adapter import PromptEngine
from prompt_master.ui.setup_wizard import SetupWizard


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Prompt Master Standalone"); self.resize(1050, 760); self.image_path: Path | None = None; self.engine = PromptEngine()
        settings_menu=self.menuBar().addMenu("Settings"); models_action=settings_menu.addAction("Models and Hardware…"); models_action.triggered.connect(self.open_setup)
        root=QWidget(); layout=QVBoxLayout(root); self.intent=QPlainTextEdit(); self.intent.setPlaceholderText("Describe the video you want to create…"); layout.addWidget(QLabel("Intent")); layout.addWidget(self.intent)
        image_row=QHBoxLayout(); self.image_label=QLabel("Text only"); browse=QPushButton("Browse image…"); remove=QPushButton("Remove image"); browse.clicked.connect(self.browse_image); remove.clicked.connect(self.remove_image); image_row.addWidget(self.image_label,1); image_row.addWidget(browse); image_row.addWidget(remove); layout.addLayout(image_row)
        form=QFormLayout(); self.mode=self.combo(["T2V","I2V"]); self.seconds=QDoubleSpinBox(); self.seconds.setRange(1,60); self.seconds.setValue(12); self.fps=QSpinBox(); self.fps.setRange(1,120); self.fps.setValue(24); self.style=self.combo(["off","cinematic","documentary","anime"]); self.camera=self.combo(["off","static","dolly","handheld","orbit"]); self.transition=self.combo(["off","cut","dissolve"]); self.smart=QCheckBox(); self.smart.setChecked(True)
        for label,widget in [("Video mode",self.mode),("Duration (seconds)",self.seconds),("FPS",self.fps),("Style",self.style),("Camera",self.camera),("Transition",self.transition),("Smart negative",self.smart)]: form.addRow(label,widget)
        layout.addLayout(form); actions=QHBoxLayout(); generate=QPushButton("Generate"); generate.clicked.connect(self.generate_placeholder); clear=QPushButton("Clear"); clear.clicked.connect(self.clear); actions.addWidget(generate); actions.addWidget(clear); layout.addLayout(actions)
        self.positive=QPlainTextEdit(); self.negative=QPlainTextEdit(); layout.addWidget(QLabel("Positive prompt")); layout.addWidget(self.positive); layout.addWidget(QLabel("Negative prompt")); layout.addWidget(self.negative)
        copies=QHBoxLayout()
        for label,source in [("Copy Positive",self.positive),("Copy Negative",self.negative)]: button=QPushButton(label); button.clicked.connect(lambda _=False,s=source: self.copy(s)); copies.addWidget(button)
        save=QPushButton("Save both…"); save.clicked.connect(self.save); copies.addWidget(save); layout.addLayout(copies); self.status=QLabel("Server: stopped · Generation: idle"); layout.addWidget(self.status); self.setCentralWidget(root)

    @staticmethod
    def combo(values): box=QComboBox(); box.addItems(values); return box
    def browse_image(self):
        filename,_=QFileDialog.getOpenFileName(self,"Reference image","","Images (*.png *.jpg *.jpeg *.webp)")
        if filename: self.image_path=Path(filename); self.image_label.setText(filename); self.mode.setCurrentText("I2V")
    def remove_image(self): self.image_path=None; self.image_label.setText("Text only"); self.mode.setCurrentText("T2V")
    def request(self):
        data=image_data_url(self.image_path) if self.image_path else None
        return PromptRequest(intent=self.intent.toPlainText().strip(),image_data_url=data,video_mode=self.mode.currentText(),seconds=self.seconds.value(),fps=self.fps.value(),style=self.style.currentText(),camera=self.camera.currentText(),transition=self.transition.currentText(),smart_negative=self.smart.isChecked())
    def generate_placeholder(self):
        if not self.intent.toPlainText().strip(): QMessageBox.warning(self,"Missing intent","Enter a video intent first."); return
        QMessageBox.information(self,"Setup required","Complete Models and Hardware setup before generation. The inference services are available to the setup workflow.")
    def copy(self, source): source.selectAll(); source.copy()
    def save(self):
        filename,_=QFileDialog.getSaveFileName(self,"Save prompts","prompts.txt","Text (*.txt)")
        if filename: Path(filename).write_text(f"POSITIVE\n{self.positive.toPlainText()}\n\nNEGATIVE\n{self.negative.toPlainText()}\n",encoding="utf-8")
    def clear(self): self.intent.clear(); self.positive.clear(); self.negative.clear(); self.remove_image()
    def open_setup(self):
        wizard=SetupWizard(self); wizard.exec()
