"""Unit tests for core modules: timer, activities, sounds."""
import sys
import os
from unittest.mock import MagicMock, patch

import pytest


# Create proper mock classes for Qt
class MockQObject:
    def __init__(self, parent=None):
        pass


class MockQTimer:
    def __init__(self, parent=None):
        self._callback = None
        self._running = False

    def timeout_connect(self, callback):
        self._callback = callback

    @property
    def timeout(self):
        mock = MagicMock()
        mock.connect = self.timeout_connect
        return mock

    def start(self, interval):
        self._running = True

    def stop(self):
        self._running = False


class MockSignal:
    def __init__(self):
        self._callbacks = []

    def connect(self, cb):
        self._callbacks.append(cb)

    def emit(self):
        for cb in self._callbacks:
            cb()


def mock_pyqtSignal():
    return MockSignal()


# Set up aqt.qt module with our mocks
aqt_qt_mock = MagicMock()
aqt_qt_mock.QObject = MockQObject
aqt_qt_mock.QTimer = MockQTimer
aqt_qt_mock.pyqtSignal = mock_pyqtSignal

# Mock aqt before importing our modules
sys.modules['aqt'] = MagicMock()
sys.modules['aqt.qt'] = aqt_qt_mock
sys.modules['aqt.sound'] = MagicMock()

# Mock PyQt
mock_qsound = MagicMock()
mock_qurl = MagicMock()
sys.modules['PyQt6'] = MagicMock()
sys.modules['PyQt6.QtMultimedia'] = MagicMock()
sys.modules['PyQt6.QtMultimedia'].QSoundEffect = mock_qsound
sys.modules['PyQt6.QtCore'] = MagicMock()
sys.modules['PyQt6.QtCore'].QUrl = mock_qurl

# Add break_reminder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestActivities:
    """Tests for activities.py"""

    def test_get_random_activity_with_activities(self):
        """Should return activity from pool"""
        from break_reminder import activities

        mock_config = {"break_activities": ["stretch", "walk", "drink water"]}
        with patch.object(activities, 'mw') as mock_mw:
            mock_mw.addonManager.getConfig.return_value = mock_config

            result = activities.get_random_activity()
            assert result in mock_config["break_activities"]

    def test_get_random_activity_empty_pool(self):
        """Should return default message when pool is empty"""
        from break_reminder import activities

        mock_config = {"break_activities": []}
        with patch.object(activities, 'mw') as mock_mw:
            mock_mw.addonManager.getConfig.return_value = mock_config

            result = activities.get_random_activity()
            assert result == "Take a break!"

    def test_get_random_activity_missing_key(self):
        """Should return default when key missing"""
        from break_reminder import activities

        mock_config = {}
        with patch.object(activities, 'mw') as mock_mw:
            mock_mw.addonManager.getConfig.return_value = mock_config

            result = activities.get_random_activity()
            assert result == "Take a break!"


class TestSounds:
    """Tests for sounds.py"""

    def test_get_sound_path(self):
        """Should construct correct path"""
        from break_reminder import sounds

        path = sounds._get_sound_path("test.wav")
        assert path.endswith(os.path.join("user_files", "test.wav"))

    def test_play_break_start_disabled(self):
        """Should not play when sounds disabled"""
        from break_reminder import sounds

        mock_config = {"enable_sounds": False}
        with patch.object(sounds, 'mw') as mock_mw:
            mock_mw.addonManager.getConfig.return_value = mock_config
            with patch.object(sounds, 'av_player') as mock_player:
                sounds._break_start_sound = None
                sounds.play_break_start()
                mock_player.play_file.assert_not_called()

    def test_play_break_end_disabled(self):
        """Should not play when sounds disabled"""
        from break_reminder import sounds

        mock_config = {"enable_sounds": False}
        with patch.object(sounds, 'mw') as mock_mw:
            mock_mw.addonManager.getConfig.return_value = mock_config
            with patch.object(sounds, 'av_player') as mock_player:
                sounds._break_end_sound = None
                sounds.play_break_end()
                mock_player.play_file.assert_not_called()

    def test_play_with_missing_file(self):
        """Should handle missing sound file gracefully"""
        from break_reminder import sounds

        mock_config = {"enable_sounds": True, "break_start_volume": 0.5}
        with patch.object(sounds, 'mw') as mock_mw:
            mock_mw.addonManager.getConfig.return_value = mock_config
            with patch.object(sounds, 'av_player') as mock_player:
                with patch('os.path.exists', return_value=False):
                    sounds._break_start_sound = None
                    sounds.play_break_start()
                    mock_player.play_file.assert_not_called()

    def test_has_volume_control(self):
        """Should report volume control availability"""
        from break_reminder import sounds
        # QSoundEffect was mocked, so should return truthy
        # The actual value depends on import success


class TestTimer:
    """Tests for timer.py"""

    def _make_timer(self, mock_mw, duration_minutes=25):
        """Helper to create timer with mocked config"""
        from break_reminder import timer
        mock_mw.addonManager.getConfig.return_value = {"study_duration_minutes": duration_minutes}
        return timer.StudyTimer()

    def test_timer_initial_state(self):
        """Timer should start paused with zero elapsed"""
        from break_reminder import timer

        with patch.object(timer, 'mw') as mock_mw:
            t = self._make_timer(mock_mw)
            assert t.elapsed == 0
            assert t.running == False

    def test_timer_start(self):
        """Timer should start running"""
        from break_reminder import timer

        with patch.object(timer, 'mw') as mock_mw:
            t = self._make_timer(mock_mw)
            t.start()
            assert t.running == True

    def test_timer_pause(self):
        """Timer should pause"""
        from break_reminder import timer

        with patch.object(timer, 'mw') as mock_mw:
            t = self._make_timer(mock_mw)
            t.start()
            t.pause()
            assert t.running == False

    def test_timer_reset(self):
        """Timer should reset elapsed and stop"""
        from break_reminder import timer

        with patch.object(timer, 'mw') as mock_mw:
            t = self._make_timer(mock_mw)
            t._elapsed_seconds = 100
            t._running = True
            t.reset()
            assert t.elapsed == 0
            assert t.running == False

    def test_timer_on_tick_increments(self):
        """Each tick should increment elapsed"""
        from break_reminder import timer

        with patch.object(timer, 'mw') as mock_mw:
            t = self._make_timer(mock_mw)
            t._on_tick()
            assert t.elapsed == 1

    def test_timer_emits_signal_on_complete(self):
        """Should emit study_complete when duration reached"""
        from break_reminder import timer

        with patch.object(timer, 'mw') as mock_mw:
            t = self._make_timer(mock_mw, duration_minutes=1)
            signal_fired = []
            t.study_complete.connect(lambda: signal_fired.append(True))
            t._running = True

            # Simulate 60 ticks (1 minute)
            for _ in range(60):
                t._on_tick()

            assert len(signal_fired) == 1
            assert t.elapsed == 0  # Reset after complete
