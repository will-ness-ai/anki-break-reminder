from aqt import gui_hooks
from aqt.utils import showInfo


def on_profile_loaded():
    showInfo("Break Reminder loaded!")


gui_hooks.profile_did_open.append(on_profile_loaded)
