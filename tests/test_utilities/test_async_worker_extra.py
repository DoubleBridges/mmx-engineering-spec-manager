from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer

from mmx_engineering_spec_manager.utilities.async_worker import FunctionWorker, run_in_thread


def _spin_until(loop: QEventLoop, timeout_ms: int = 2000):
    QTimer.singleShot(timeout_ms, loop.quit)
    loop.exec()


def test_worker_run_direct_success_progress_and_result():
    # Ensure a Qt app exists
    app = QCoreApplication.instance() or QCoreApplication([])

    progresses = []
    results = []
    finished = []

    def job(progress=None):
        if progress:
            progress(1)
            progress(2)
        return "ok"

    w = FunctionWorker(job)
    w.progress.connect(lambda v: progresses.append(v))
    w.result.connect(lambda r: results.append(r))
    w.finished.connect(lambda: finished.append(True))

    # Invoke synchronously to cover run() lines without thread coverage limitations
    w.run()

    assert results == ["ok"]
    assert finished
    assert progresses == [1, 2]


def test_worker_run_direct_error_emits_error_and_finished():
    app = QCoreApplication.instance() or QCoreApplication([])

    errors = []
    finished = []

    def bad():
        raise RuntimeError("boom-direct")

    w = FunctionWorker(bad)
    w.error.connect(lambda msg: errors.append(msg))
    w.finished.connect(lambda: finished.append(True))

    w.run()

    assert errors and "boom-direct" in errors[0]
    assert finished


def test_run_in_thread_smoke_finished():
    app = QCoreApplication.instance() or QCoreApplication([])
    loop = QEventLoop()

    def noop():
        return None

    worker, thread = run_in_thread(noop)
    thread.finished.connect(loop.quit)
    _spin_until(loop)
    # If we reach here, run_in_thread path executed and thread finished


def test_emit_progress_handles_bad_values_gracefully():
    # Directly call helper to cover exception branch
    w = FunctionWorker(lambda: None)
    try:
        w._emit_progress("not-an-int")
    except Exception as e:
        assert False, f"_emit_progress should not raise, got: {e}"
