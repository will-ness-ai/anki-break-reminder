from aqt import mw
from aqt.qt import QObject, QTimer, pyqtSignal


class StudyTimer(QObject):
    study_complete = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._elapsed_seconds = 0
        self._running = False

    def _get_study_duration(self):
        config = mw.addonManager.getConfig(__name__.split('.')[0])
        return config.get("study_duration_minutes", 25) * 60

    def start(self):
        if not self._running:
            self._running = True
            self._timer.start(1000)

    def pause(self):
        if self._running:
            self._running = False
            self._timer.stop()

    def resume(self):
        self.start()

    def reset(self):
        self._timer.stop()
        self._elapsed_seconds = 0
        self._running = False

    def _on_tick(self):
        self._elapsed_seconds += 1
        if self._elapsed_seconds >= self._get_study_duration():
            self.pause()
            self._elapsed_seconds = 0
            self.study_complete.emit()

    @property
    def elapsed(self):
        return self._elapsed_seconds

    @property
    def running(self):
        return self._running
