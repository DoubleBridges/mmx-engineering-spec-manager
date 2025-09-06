from __future__ import annotations
from typing import Any, Callable, Tuple, Dict, Optional

from PySide6.QtCore import QObject, Signal, Slot, QThread


class FunctionWorker(QObject):
    """
    Generic worker to run a callable in a separate QThread and report back via signals.
    Cross-platform, integrates with Qt's event loop using queued connections.
    """

    progress = Signal(int)  # optional progress reporting from job via callback
    result = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self, func: Callable[..., Any], args: Tuple[Any, ...] | None = None, kwargs: Dict[str, Any] | None = None):
        super().__init__()
        self._func = func
        self._args = args or ()
        self._kwargs = kwargs or {}
        self._thread: Optional[QThread] = None

    def _inject_progress_callback(self):
        # If user function accepts a 'progress' keyword arg, supply a callback that emits the signal
        if 'progress' in getattr(self._func, '__code__', None).co_varnames:
            self._kwargs.setdefault('progress', self._emit_progress)

    def _emit_progress(self, value: int):
        try:
            self.progress.emit(int(value))
        except Exception:
            # Be robust; ignore malformed progress values
            pass

    @Slot()
    def run(self):
        try:
            self._inject_progress_callback()
            res = self._func(*self._args, **self._kwargs)
            self.result.emit(res)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

    def start(self) -> QThread:
        """Create and start a new QThread for this worker. Returns the thread for lifecycle control."""
        thread = QThread()
        self._thread = thread
        self.moveToThread(thread)
        thread.started.connect(self.run)
        # Ensure proper cleanup when done
        self.finished.connect(thread.quit)
        self.finished.connect(self.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.start()
        return thread


def run_in_thread(func: Callable[..., Any], *args: Any, **kwargs: Any) -> tuple[FunctionWorker, QThread]:
    """
    Convenience to create a FunctionWorker and start it immediately.
    Returns (worker, thread) so caller can connect signals and keep references.
    """
    worker = FunctionWorker(func, args=args, kwargs=kwargs)
    thread = worker.start()
    return worker, thread
