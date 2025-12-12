from aqt import mw, gui_hooks
from aqt.qt import QTimer, QMenu, QAction
from .timer import StudyTimer
from .dialogs import BreakDialog, SettingsDialog

study_timer = None
_snooze_active = False


def _get_config():
    return mw.addonManager.getConfig(__name__)


def _show_break_dialog():
    global _snooze_active

    def on_snooze():
        global _snooze_active
        _snooze_active = True
        config = _get_config()
        snooze_ms = config.get("snooze_duration_minutes", 5) * 60 * 1000
        QTimer.singleShot(snooze_ms, _on_snooze_complete)

    def on_dismiss():
        global _snooze_active
        _snooze_active = False
        study_timer.reset()
        study_timer.start()

    dialog = BreakDialog(on_snooze=on_snooze, on_dismiss=on_dismiss, parent=mw)
    dialog.exec()


def _on_snooze_complete():
    global _snooze_active
    if _snooze_active:
        _snooze_active = False
        _show_break_dialog()


def _on_study_complete():
    _show_break_dialog()


def _on_reviewer_card(card):
    if study_timer and not _snooze_active:
        study_timer.start()


def _on_reviewer_end():
    if study_timer:
        study_timer.pause()


def _init_timer():
    global study_timer
    study_timer = StudyTimer(mw)
    study_timer.study_complete.connect(_on_study_complete)


def _start_timer():
    if study_timer:
        study_timer.start()


def _pause_timer():
    if study_timer:
        study_timer.pause()


def _reset_timer():
    if study_timer:
        study_timer.reset()


def _show_settings():
    dialog = SettingsDialog(mw)
    dialog.exec()


def _setup_menu():
    menu = QMenu("Break Reminder", mw)

    start_action = QAction("Start Timer", mw)
    start_action.triggered.connect(_start_timer)
    menu.addAction(start_action)

    pause_action = QAction("Pause Timer", mw)
    pause_action.triggered.connect(_pause_timer)
    menu.addAction(pause_action)

    reset_action = QAction("Reset Timer", mw)
    reset_action.triggered.connect(_reset_timer)
    menu.addAction(reset_action)

    menu.addSeparator()

    settings_action = QAction("Settings...", mw)
    settings_action.triggered.connect(_show_settings)
    menu.addAction(settings_action)

    mw.form.menuTools.addMenu(menu)


gui_hooks.profile_did_open.append(_init_timer)
gui_hooks.profile_did_open.append(_setup_menu)
gui_hooks.reviewer_did_show_question.append(_on_reviewer_card)
gui_hooks.reviewer_will_end.append(_on_reviewer_end)
