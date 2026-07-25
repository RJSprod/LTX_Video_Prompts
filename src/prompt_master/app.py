from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from prompt_master.core.paths import AppPaths
from prompt_master.ui.main_window import MainWindow
from prompt_master.ui.setup_wizard import SetupWizard


def main() -> int:
    paths=AppPaths.discover(); paths.create_managed_dirs(); app=QApplication(sys.argv); app.setApplicationName("Prompt Master Standalone"); window=MainWindow()
    if "--setup" in sys.argv: SetupWizard(window).exec()
    window.show(); return app.exec()


if __name__ == "__main__": raise SystemExit(main())
