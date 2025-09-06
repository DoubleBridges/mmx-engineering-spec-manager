from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer

from mmx_engineering_spec_manager.utilities.async_worker import FunctionWorker, run_in_thread


def _spin_until(loop: QEventLoop, timeout_ms: int = 2000):
    # Safety timeout to avoid hanging tests
    QTimer.singleShot(timeout_ms, loop.quit)
    loop.exec()


def test_function_worker_success_emits_result_and_finished():
    app = QCoreApplication.instance() or QCoreApplication([])
    loop = QEventLoop()

    progresses = []
    results = []
    finished = []

    def job(progress=None):
        # If progress callback provided, emit a couple of values
        if progress:
            progress(10)
            progress(100)
        return 123

    worker = FunctionWorker(job)

    worker.progress.connect(lambda v: progresses.append(v))
    worker.result.connect(lambda r: results.append(r))
    worker.finished.connect(lambda: finished.append(True))

    thread = worker.start()
    # Quit the loop only when the underlying QThread has actually finished
    thread.finished.connect(loop.quit)

    _spin_until(loop)

    # Ensure signals were emitted and values correct
    assert results == [123]
    assert finished, "finished signal not emitted"
    assert progresses in ([], [10, 100])  # progress is optional depending on injection success


def test_run_in_thread_error_emits_error_and_finished():
    app = QCoreApplication.instance() or QCoreApplication([])
    loop = QEventLoop()

    errors = []
    finished = []

    def bad_job():
        raise RuntimeError("boom")

    worker = FunctionWorker(bad_job)
    worker.error.connect(lambda msg: errors.append(msg))
    worker.finished.connect(lambda: finished.append(True))
    thread = worker.start()
    # Ensure we wait until the thread has actually finished before asserting
    thread.finished.connect(loop.quit)

    _spin_until(loop)

    assert errors and "boom" in errors[0]
    assert finished, "finished signal not emitted on error"
