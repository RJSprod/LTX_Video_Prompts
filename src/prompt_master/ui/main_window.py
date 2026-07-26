from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (QCheckBox,QComboBox,QFileDialog,QFormLayout,QHBoxLayout,QLabel,QMainWindow,QMessageBox,QPlainTextEdit,QPushButton,QSpinBox,QDoubleSpinBox,QVBoxLayout,QWidget,QScrollArea)
import threading

from prompt_master.core.models import PromptRequest
from prompt_master.imaging.preprocess import image_data_url
from prompt_master.prompt_engine.adapter import PromptEngine
from prompt_master.core.paths import AppPaths
from prompt_master.inference.service import InferenceService
from prompt_master.ui.setup_wizard import SetupWizard


class GenerationWorker(QObject):
    positive_chunk = Signal(str)
    positive_ready = Signal(str)
    negative_ready = Signal(str)
    status = Signal(str)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, service, engine, request):
        super().__init__(); self.service, self.engine, self.request = service, engine, request; self.cancelled = threading.Event()

    @Slot()
    def cancel(self): self.cancelled.set()

    @Slot()
    def run(self):
        try:
            self.status.emit("Starting llama-server…")
            client = self.service.client(self.request.image_data_url is not None)
            self.status.emit("Generating positive prompt…")
            raw = client.stream_chat(self.engine.build_messages(self.request), self.engine.max_tokens(self.request), self.request.seed, self.positive_chunk.emit, self.cancelled)
            if self.cancelled.is_set(): self.status.emit("Generation cancelled"); return
            positive = self.engine.clean_positive(raw)
            self.positive_ready.emit(positive)
            smart = ""
            if self.request.smart_negative:
                self.status.emit("Generating smart negative…")
                smart = client.stream_chat(self.engine.smart_negative_messages(positive), 256, self.request.seed, lambda _: None, self.cancelled)
                smart = self.engine.clean_smart_negative(positive, smart)
            self.negative_ready.emit(self.engine.merge_negative(self.request, smart))
            self.status.emit("Server: running · Generation: complete")
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self, paths: AppPaths | None = None):
        super().__init__(); self.paths = paths or AppPaths.discover(); self.service = InferenceService(self.paths); self.thread = None; self.setWindowTitle("Prompt Master Standalone"); self.resize(1050, 760); self.image_path: Path | None = None; self.engine = PromptEngine()
        settings_menu=self.menuBar().addMenu("Settings"); models_action=settings_menu.addAction("Models and Hardware…"); models_action.triggered.connect(self.open_setup)
        root=QWidget(); layout=QVBoxLayout(root); self.intent=QPlainTextEdit(); self.intent.setPlaceholderText("Describe the video you want to create…"); layout.addWidget(QLabel("Intent")); layout.addWidget(self.intent)
        image_row=QHBoxLayout(); self.image_label=QLabel("Text only"); browse=QPushButton("Browse image…"); remove=QPushButton("Remove image"); browse.clicked.connect(self.browse_image); remove.clicked.connect(self.remove_image); image_row.addWidget(self.image_label,1); image_row.addWidget(browse); image_row.addWidget(remove); layout.addLayout(image_row)
        form=QFormLayout(); self.mode=self.combo(["T2V","I2V"]); self.seconds=QDoubleSpinBox(); self.seconds.setRange(1,60); self.seconds.setValue(12); self.fps=QSpinBox(); self.fps.setRange(1,120); self.fps.setValue(24)
        self.style=self.combo(["off","cinematic","documentary","anime","photorealistic","film noir","vintage film","surreal","fantasy","science fiction","horror","music video","commercial","claymation","stop motion","watercolor","oil painting","comic book","pixel art"])
        self.camera=self.combo(["off","static","pan","tilt","dolly in","dolly out","truck left","truck right","pedestal up","pedestal down","handheld","steadicam","crane","jib","drone","orbit","zoom in","zoom out","rack focus","whip pan"])
        self.transition=self.combo(["off","cut","dissolve","fade in","fade out","match cut","wipe","whip transition","iris","smash cut"])
        self.pov=self.combo(["off","first-person","second-person","third-person","over-the-shoulder","subjective","omniscient"])
        self.accent=self.combo(["off","American","British","Australian","Irish","Scottish","Welsh","Canadian","New Zealand","South African","Indian","French","German","Italian","Spanish","Russian","Japanese","Chinese","Korean","Brazilian","Mexican","Caribbean","Southern US","New York","Boston"])
        self.accent_strength=QSpinBox(); self.accent_strength.setRange(0,100); self.accent_strength.setValue(50); self.accent_strength.setSuffix("%")
        self.dialogue=QSpinBox(); self.dialogue.setRange(0,100); self.dialogue.setValue(20); self.dialogue.setSuffix("%")
        self.music=self.combo(["off","ambient","orchestral","cinematic","electronic","acoustic","jazz","blues","rock","pop","hip hop","classical","folk","country","reggae","metal","synthwave","lo-fi","world","experimental"])
        self.music_background=QPlainTextEdit(); self.music_background.setMaximumHeight(50); self.wardrobe=QPlainTextEdit(); self.wardrobe.setMaximumHeight(50); self.undress=QCheckBox("Allow story-requested clothing changes")
        self.lexicon=self.combo(["natural","simple","concise","descriptive","cinematic","technical","poetic","documentary"]); self.output_format=self.combo(["flowing","shot list","timestamped","structured"])
        self.dimensions=self.combo(["1920x1080","1080x1920","1280x720","720x1280","1024x1024"]); self.seed=QSpinBox(); self.seed.setRange(-1,2147483647); self.seed.setValue(-1); self.seed.setSpecialValueText("Random")
        self.negative_extra=QPlainTextEdit(); self.negative_extra.setMaximumHeight(50); self.smart=QCheckBox(); self.smart.setChecked(True)
        for label,widget in [("Video mode",self.mode),("Duration (seconds)",self.seconds),("FPS",self.fps),("Dimensions",self.dimensions),("Seed",self.seed),("Style",self.style),("Camera",self.camera),("Transition",self.transition),("POV",self.pov),("Accent",self.accent),("Accent strength",self.accent_strength),("Dialogue / talk",self.dialogue),("Music",self.music),("Music background",self.music_background),("Wardrobe",self.wardrobe),("Undress",self.undress),("Lexicon",self.lexicon),("Output format",self.output_format),("Extra negative terms",self.negative_extra),("Smart negative",self.smart)]: form.addRow(label,widget)
        layout.addLayout(form); actions=QHBoxLayout(); self.generate_button=QPushButton("Generate"); self.generate_button.clicked.connect(self.generate); self.cancel_button=QPushButton("Cancel"); self.cancel_button.setEnabled(False); self.cancel_button.clicked.connect(self.cancel_generation); clear=QPushButton("Clear"); clear.clicked.connect(self.clear); actions.addWidget(self.generate_button); actions.addWidget(self.cancel_button); actions.addWidget(clear); layout.addLayout(actions)
        self.positive=QPlainTextEdit(); self.negative=QPlainTextEdit(); layout.addWidget(QLabel("Positive prompt")); layout.addWidget(self.positive); layout.addWidget(QLabel("Negative prompt")); layout.addWidget(self.negative)
        copies=QHBoxLayout()
        for label,source in [("Copy Positive",self.positive),("Copy Negative",self.negative)]: button=QPushButton(label); button.clicked.connect(lambda _=False,s=source: self.copy(s)); copies.addWidget(button)
        both=QPushButton("Copy Both"); both.clicked.connect(self.copy_both); copies.addWidget(both)
        save=QPushButton("Save .txt…"); save.clicked.connect(self.save); copies.addWidget(save); layout.addLayout(copies); self.status=QLabel("GPU: not configured · Model: not configured · Server: stopped · Generation: idle"); layout.addWidget(self.status)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(root); self.setCentralWidget(scroll); self.refresh_status()

    @staticmethod
    def combo(values): box=QComboBox(); box.addItems(values); return box
    def browse_image(self):
        filename,_=QFileDialog.getOpenFileName(self,"Reference image","","Images (*.png *.jpg *.jpeg *.webp)")
        if filename: self.image_path=Path(filename); self.image_label.setText(filename); self.mode.setCurrentText("I2V")
    def remove_image(self): self.image_path=None; self.image_label.setText("Text only"); self.mode.setCurrentText("T2V")
    def request(self):
        data=image_data_url(self.image_path) if self.image_path else None
        width,height=map(int,self.dimensions.currentText().split("x"))
        return PromptRequest(intent=self.intent.toPlainText().strip(),image_data_url=data,video_mode=self.mode.currentText(),seconds=self.seconds.value(),fps=self.fps.value(),style=self.style.currentText(),camera=self.camera.currentText(),transition=self.transition.currentText(),pov=self.pov.currentText(),accent=self.accent.currentText(),accent_strength=self.accent_strength.value(),dialogue=self.dialogue.value(),music=self.music.currentText(),music_background=self.music_background.toPlainText(),wardrobe=self.wardrobe.toPlainText(),undress=self.undress.isChecked(),lexicon=self.lexicon.currentText(),output_format=self.output_format.currentText(),negative_extra=self.negative_extra.toPlainText(),seed=self.seed.value(),smart_negative=self.smart.isChecked(),output_width=width,output_height=height)
    def generate(self):
        if not self.intent.toPlainText().strip(): QMessageBox.warning(self,"Missing intent","Enter a video intent first."); return
        if self.thread and self.thread.isRunning(): return
        try: request = self.request()
        except Exception as exc: QMessageBox.critical(self,"Image error",str(exc)); return
        self.positive.clear(); self.negative.setPlainText(self.engine.build_base_negative(request)); self.generate_button.setEnabled(False); self.cancel_button.setEnabled(True)
        self.thread=QThread(self); worker=GenerationWorker(self.service,self.engine,request); worker.moveToThread(self.thread); self._worker=worker
        self.thread.started.connect(worker.run); worker.positive_chunk.connect(self.positive.insertPlainText); worker.positive_ready.connect(self.positive.setPlainText); worker.negative_ready.connect(self.negative.setPlainText); worker.status.connect(self.status.setText); worker.failed.connect(self.generation_failed); worker.finished.connect(self.thread.quit); worker.finished.connect(worker.deleteLater); self.thread.finished.connect(self.generation_done); self.thread.start()
    def generation_failed(self, message): self.status.setText("Generation failed"); QMessageBox.critical(self,"Generation failed",message)
    def generation_done(self): self.generate_button.setEnabled(True); self.cancel_button.setEnabled(False); self.thread.deleteLater(); self.thread=None; self._worker=None
    def cancel_generation(self):
        if getattr(self,"_worker",None): self._worker.cancel()
    def copy(self, source): source.selectAll(); source.copy()
    def copy_both(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(f"POSITIVE\n{self.positive.toPlainText()}\n\nNEGATIVE\n{self.negative.toPlainText()}")
    def save(self):
        filename,_=QFileDialog.getSaveFileName(self,"Save prompts","prompts.txt","Text (*.txt)")
        if filename: Path(filename).write_text(f"POSITIVE\n{self.positive.toPlainText()}\n\nNEGATIVE\n{self.negative.toPlainText()}\n",encoding="utf-8")
    def clear(self): self.intent.clear(); self.positive.clear(); self.negative.clear(); self.remove_image()
    def refresh_status(self):
        from prompt_master.core.config import read_json
        state=read_json(self.paths.data/"setup-state.json")
        self.status.setText(f"GPU: {state.get('gpu_device_name',state.get('gpu_name','not configured'))} · Model: {state.get('quantization','not configured')} · Server: {'running' if self.service.process.running else 'stopped'} · Generation: idle")
    def open_setup(self):
        self.service.stop(); wizard=SetupWizard(self.paths,self)
        if wizard.exec() and wizard.completed:
            self.paths=wizard.paths; self.service=InferenceService(self.paths); self.refresh_status()
    def closeEvent(self,event):
        if self.thread and self.thread.isRunning(): self.thread.quit(); self.thread.wait(3000)
        self.service.stop(); event.accept()
