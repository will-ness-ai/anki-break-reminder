from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTimer, Qt, QFont, QSpinBox, QCheckBox, QListWidget,
    QLineEdit, QGroupBox, QFormLayout, QDialogButtonBox,
    QListWidgetItem, QInputDialog, QSlider, QFileDialog, QPixmap
)
import os
from .activities import get_random_activity
from .sounds import play_break_start, play_break_end, play_test_sound, has_volume_control


class BreakDialog(QDialog):
    def __init__(self, on_snooze=None, on_dismiss=None, parent=None):
        super().__init__(parent)
        self._on_snooze = on_snooze
        self._on_dismiss = on_dismiss
        self._break_seconds = 0
        self._break_timer = QTimer(self)
        self._break_timer.timeout.connect(self._on_break_tick)
        self._setup_ui()
        play_break_start()

    def _get_config(self):
        return mw.addonManager.getConfig(__name__.split('.')[0])

    def _setup_ui(self):
        self.setWindowTitle("Break Reminder")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Time for a Break!")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Custom image
        config = self._get_config()
        img_path = config.get("break_image_path", "")
        if img_path and os.path.isfile(img_path):
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    250, 200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                img_label = QLabel()
                img_label.setPixmap(scaled)
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(img_label)
                layout.addSpacing(10)

        # Activity
        layout.addSpacing(10)
        activity_label = QLabel("Suggested Activity:")
        layout.addWidget(activity_label)

        self._activity_text = QLabel(get_random_activity())
        self._activity_text.setWordWrap(True)
        self._activity_text.setStyleSheet("font-style: italic; padding: 10px;")
        layout.addWidget(self._activity_text)

        # Countdown display
        layout.addSpacing(10)
        self._countdown_label = QLabel()
        countdown_font = QFont()
        countdown_font.setPointSize(24)
        countdown_font.setBold(True)
        self._countdown_label.setFont(countdown_font)
        self._countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._countdown_label.hide()
        layout.addWidget(self._countdown_label)

        # Buttons row 1: Snooze + Start Break
        self._prompt_buttons = QHBoxLayout()
        config = self._get_config()
        snooze_min = config.get("snooze_duration_minutes", 5)

        self._snooze_btn = QPushButton(f"Snooze ({snooze_min} min)")
        self._snooze_btn.clicked.connect(self._on_snooze_clicked)
        self._prompt_buttons.addWidget(self._snooze_btn)

        self._start_btn = QPushButton("Start Break")
        self._start_btn.clicked.connect(self._on_start_clicked)
        self._start_btn.setDefault(True)
        self._prompt_buttons.addWidget(self._start_btn)

        layout.addLayout(self._prompt_buttons)

        # Dismiss button
        layout.addSpacing(5)
        self._dismiss_btn = QPushButton("Back to Studying")
        self._dismiss_btn.clicked.connect(self._on_dismiss_clicked)
        layout.addWidget(self._dismiss_btn)

    def _format_time(self, seconds):
        m, s = divmod(seconds, 60)
        return f"{m}:{s:02d}"

    def _on_snooze_clicked(self):
        self._break_timer.stop()
        if self._on_snooze:
            self._on_snooze()
        self.accept()

    def _on_start_clicked(self):
        config = self._get_config()
        self._break_seconds = config.get("break_duration_minutes", 5) * 60
        self._countdown_label.setText(self._format_time(self._break_seconds))
        self._countdown_label.show()
        self._snooze_btn.hide()
        self._start_btn.hide()
        self._break_timer.start(1000)

    def _on_break_tick(self):
        self._break_seconds -= 1
        self._countdown_label.setText(self._format_time(self._break_seconds))
        if self._break_seconds <= 0:
            self._break_timer.stop()
            play_break_end()
            if self._on_dismiss:
                self._on_dismiss()
            self.accept()

    def _on_dismiss_clicked(self):
        self._break_timer.stop()
        if self._on_dismiss:
            self._on_dismiss()
        self.accept()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_config()

    def _get_config(self):
        return mw.addonManager.getConfig(__name__.split('.')[0])

    def _save_config(self, config):
        mw.addonManager.writeConfig(__name__.split('.')[0], config)

    def _setup_ui(self):
        self.setWindowTitle("Break Reminder Settings")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        # Timer settings
        timer_group = QGroupBox("Timer Settings")
        timer_layout = QFormLayout()

        self._study_spin = QSpinBox()
        self._study_spin.setRange(1, 120)
        self._study_spin.setSuffix(" minutes")
        timer_layout.addRow("Study duration:", self._study_spin)

        self._break_spin = QSpinBox()
        self._break_spin.setRange(1, 60)
        self._break_spin.setSuffix(" minutes")
        timer_layout.addRow("Break duration:", self._break_spin)

        self._snooze_spin = QSpinBox()
        self._snooze_spin.setRange(1, 30)
        self._snooze_spin.setSuffix(" minutes")
        timer_layout.addRow("Snooze duration:", self._snooze_spin)

        timer_group.setLayout(timer_layout)
        layout.addWidget(timer_group)

        # Sound settings
        sound_group = QGroupBox("Sound Settings")
        sound_layout = QVBoxLayout()

        self._sound_check = QCheckBox("Enable sounds")
        self._sound_check.stateChanged.connect(self._on_sound_toggle)
        sound_layout.addWidget(self._sound_check)

        if has_volume_control():
            # Break start volume
            start_row = QHBoxLayout()
            start_row.addWidget(QLabel("Break start:"))
            self._start_vol_slider = QSlider(Qt.Orientation.Horizontal)
            self._start_vol_slider.setRange(0, 100)
            self._start_vol_slider.valueChanged.connect(self._on_start_vol_changed)
            start_row.addWidget(self._start_vol_slider)
            self._start_vol_label = QLabel("70%")
            self._start_vol_label.setMinimumWidth(35)
            start_row.addWidget(self._start_vol_label)
            self._start_test_btn = QPushButton("Test")
            self._start_test_btn.clicked.connect(self._test_break_start)
            start_row.addWidget(self._start_test_btn)
            sound_layout.addLayout(start_row)

            # Break end volume
            end_row = QHBoxLayout()
            end_row.addWidget(QLabel("Break end:"))
            self._end_vol_slider = QSlider(Qt.Orientation.Horizontal)
            self._end_vol_slider.setRange(0, 100)
            self._end_vol_slider.valueChanged.connect(self._on_end_vol_changed)
            end_row.addWidget(self._end_vol_slider)
            self._end_vol_label = QLabel("70%")
            self._end_vol_label.setMinimumWidth(35)
            end_row.addWidget(self._end_vol_label)
            self._end_test_btn = QPushButton("Test")
            self._end_test_btn.clicked.connect(self._test_break_end)
            end_row.addWidget(self._end_test_btn)
            sound_layout.addLayout(end_row)
        else:
            self._start_vol_slider = None
            self._end_vol_slider = None
            notice = QLabel("Volume control unavailable")
            notice.setStyleSheet("color: gray; font-style: italic;")
            sound_layout.addWidget(notice)

        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)

        # Image settings
        image_group = QGroupBox("Break Image")
        image_layout = QVBoxLayout()

        self._image_path = ""
        path_row = QHBoxLayout()
        self._image_path_label = QLabel("No image selected")
        self._image_path_label.setStyleSheet("color: gray; font-style: italic;")
        path_row.addWidget(self._image_path_label, 1)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_image)
        path_row.addWidget(browse_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_image)
        path_row.addWidget(clear_btn)
        image_layout.addLayout(path_row)

        self._image_preview = QLabel()
        self._image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_preview.setMinimumHeight(100)
        image_layout.addWidget(self._image_preview)

        image_group.setLayout(image_layout)
        layout.addWidget(image_group)

        # Activities
        activities_group = QGroupBox("Break Activities")
        activities_layout = QVBoxLayout()

        self._activities_list = QListWidget()
        activities_layout.addWidget(self._activities_list)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_activity)
        btn_layout.addWidget(add_btn)

        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self._edit_activity)
        btn_layout.addWidget(edit_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._remove_activity)
        btn_layout.addWidget(remove_btn)

        activities_layout.addLayout(btn_layout)
        activities_group.setLayout(activities_layout)
        layout.addWidget(activities_group)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_sound_toggle(self, state):
        enabled = bool(state)
        if self._start_vol_slider:
            self._start_vol_slider.setEnabled(enabled)
            self._end_vol_slider.setEnabled(enabled)
            self._start_test_btn.setEnabled(enabled)
            self._end_test_btn.setEnabled(enabled)

    def _on_start_vol_changed(self, value):
        self._start_vol_label.setText(f"{value}%")

    def _on_end_vol_changed(self, value):
        self._end_vol_label.setText(f"{value}%")

    def _test_break_start(self):
        volume = self._start_vol_slider.value() / 100.0
        play_test_sound("break_start.wav", volume)

    def _test_break_end(self):
        volume = self._end_vol_slider.value() / 100.0
        play_test_sound("break_end.wav", volume)

    def _browse_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Break Image", "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp)"
        )
        if path:
            self._image_path = path
            self._update_image_preview()

    def _clear_image(self):
        self._image_path = ""
        self._update_image_preview()

    def _update_image_preview(self):
        if self._image_path and os.path.isfile(self._image_path):
            pixmap = QPixmap(self._image_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    150, 100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self._image_preview.setPixmap(scaled)
                name = os.path.basename(self._image_path)
                self._image_path_label.setText(name)
                self._image_path_label.setStyleSheet("")
                return
        self._image_preview.clear()
        self._image_path_label.setText("No image selected")
        self._image_path_label.setStyleSheet("color: gray; font-style: italic;")

    def _load_config(self):
        config = self._get_config()
        self._study_spin.setValue(config.get("study_duration_minutes", 25))
        self._break_spin.setValue(config.get("break_duration_minutes", 5))
        self._snooze_spin.setValue(config.get("snooze_duration_minutes", 5))
        self._sound_check.setChecked(config.get("enable_sounds", True))

        if self._start_vol_slider:
            start_vol = int(config.get("break_start_volume", 0.7) * 100)
            end_vol = int(config.get("break_end_volume", 0.7) * 100)
            self._start_vol_slider.setValue(start_vol)
            self._end_vol_slider.setValue(end_vol)
            self._start_vol_label.setText(f"{start_vol}%")
            self._end_vol_label.setText(f"{end_vol}%")

        self._on_sound_toggle(self._sound_check.checkState())

        self._image_path = config.get("break_image_path", "")
        self._update_image_preview()

        self._activities_list.clear()
        for activity in config.get("break_activities", []):
            self._activities_list.addItem(activity)

    def _add_activity(self):
        text, ok = QInputDialog.getText(self, "Add Activity", "Activity:")
        if ok and text.strip():
            self._activities_list.addItem(text.strip())

    def _edit_activity(self):
        item = self._activities_list.currentItem()
        if not item:
            return
        text, ok = QInputDialog.getText(
            self, "Edit Activity", "Activity:", text=item.text()
        )
        if ok and text.strip():
            item.setText(text.strip())

    def _remove_activity(self):
        row = self._activities_list.currentRow()
        if row >= 0:
            self._activities_list.takeItem(row)

    def _on_accept(self):
        config = self._get_config()
        config["study_duration_minutes"] = self._study_spin.value()
        config["break_duration_minutes"] = self._break_spin.value()
        config["snooze_duration_minutes"] = self._snooze_spin.value()
        config["enable_sounds"] = self._sound_check.isChecked()
        if self._start_vol_slider:
            config["break_start_volume"] = self._start_vol_slider.value() / 100.0
            config["break_end_volume"] = self._end_vol_slider.value() / 100.0
        config["break_image_path"] = self._image_path
        config["break_activities"] = [
            self._activities_list.item(i).text()
            for i in range(self._activities_list.count())
        ]
        self._save_config(config)
        self.accept()
