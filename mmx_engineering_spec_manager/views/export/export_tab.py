from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QProgressDialog, QMessageBox


class ExportTab(QWidget):
    """
    The main widget for the 'Export' tab.
    MVVM: exposes set_view_model(vm) and reacts to VM events only.
    """
    def __init__(self):
        super().__init__()
        self._vm = None
        self._progress = None
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("Export controls will go here."))
        # Minimal UI: an Export button; params TBD
        self.btn_export = QPushButton("Export")
        self.layout.addWidget(self.btn_export)
        try:
            self.btn_export.clicked.connect(self._on_export_clicked)
        except Exception:
            pass

    def set_view_model(self, vm):
        self._vm = vm
        try:
            vm.export_started.subscribe(lambda: self._show_progress("Exporting..."))
            vm.export_progress.subscribe(self._set_progress)
            vm.export_completed.subscribe(self._on_completed)
            vm.notification.subscribe(self._on_notification)
        except Exception:
            pass

    def _on_export_clicked(self):  # pragma: no cover - thin UI glue
        try:
            if self._vm is not None and hasattr(self._vm, "export"):
                self._vm.export({})
        except Exception:
            pass

    def _show_progress(self, text: str):  # pragma: no cover - UI glue
        try:
            self._progress = QProgressDialog(text, "", 0, 100, self)
            try:
                self._progress.setCancelButton(None)
            except Exception:
                pass
            self._progress.setAutoClose(False)
            self._progress.setAutoReset(False)
            self._progress.setMinimumDuration(0)
            self._progress.setValue(0)
            self._progress.show()
        except Exception:
            self._progress = None

    def _set_progress(self, v: int):  # pragma: no cover - UI glue
        try:
            if self._progress is not None:
                self._progress.setValue(int(v))
        except Exception:
            pass

    def _on_completed(self, result):  # pragma: no cover - UI glue
        try:
            if self._progress is not None:
                self._progress.setValue(100)
                self._progress.close()
        except Exception:
            pass
        finally:
            self._progress = None
        try:
            if result:
                QMessageBox.information(self, "Export Complete", str(result))
            else:
                QMessageBox.warning(self, "Export Finished", "No output was produced.")
        except Exception:
            pass

    def _on_notification(self, msg: dict | None):  # pragma: no cover - UI glue
        try:
            level = (msg or {}).get("level")
            text = (msg or {}).get("message") or ""
            if level == "error":
                QMessageBox.critical(self, "Error", text)
            elif level == "warning":
                QMessageBox.warning(self, "Warning", text)
        except Exception:
            pass
