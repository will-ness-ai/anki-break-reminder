import os
from aqt import mw
from aqt.sound import av_player

# Try QtMultimedia for volume control
try:
    from PyQt6.QtMultimedia import QSoundEffect
    from PyQt6.QtCore import QUrl
except ImportError:
    try:
        from PyQt5.QtMultimedia import QSoundEffect
        from PyQt5.QtCore import QUrl
    except ImportError:
        QSoundEffect = None
        QUrl = None

# Module-level sound instances (prevent GC)
_break_start_sound = None
_break_end_sound = None
_test_sound = None


def _get_config():
    return mw.addonManager.getConfig(__name__.split('.')[0])


def _get_sound_path(filename):
    addon_dir = os.path.dirname(__file__)
    return os.path.join(addon_dir, "user_files", filename)


def _init_sound(filename):
    if QSoundEffect is None:
        return None
    path = _get_sound_path(filename)
    if not os.path.exists(path):
        return None
    sound = QSoundEffect()
    sound.setSource(QUrl.fromLocalFile(path))
    return sound


def _play_with_volume(sound_obj, filename, volume_key):
    config = _get_config()
    if not config.get("enable_sounds", True):
        return
    volume = config.get(volume_key, 0.7)
    if sound_obj is not None:
        sound_obj.setVolume(volume)
        sound_obj.play()
    else:
        path = _get_sound_path(filename)
        if os.path.exists(path):
            av_player.play_file(path)


def play_break_start():
    global _break_start_sound
    if _break_start_sound is None:
        _break_start_sound = _init_sound("break_start.wav")
    _play_with_volume(_break_start_sound, "break_start.wav", "break_start_volume")


def play_break_end():
    global _break_end_sound
    if _break_end_sound is None:
        _break_end_sound = _init_sound("break_end.wav")
    _play_with_volume(_break_end_sound, "break_end.wav", "break_end_volume")


def play_test_sound(filename, volume):
    global _test_sound
    if QSoundEffect is None:
        path = _get_sound_path(filename)
        if os.path.exists(path):
            av_player.play_file(path)
        return
    if _test_sound is not None:
        _test_sound.stop()
    path = _get_sound_path(filename)
    if not os.path.exists(path):
        return
    _test_sound = QSoundEffect()
    _test_sound.setSource(QUrl.fromLocalFile(path))
    _test_sound.setVolume(volume)
    _test_sound.play()


def has_volume_control():
    return QSoundEffect is not None
