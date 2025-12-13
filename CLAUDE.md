# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Anki Break Reminder - add-on that tracks study time and prompts breaks with activity suggestions. Targets Anki 2.1.50+.

## Technical Stack

- Python 3
- PyQt5/PyQt6 (via `aqt.qt` for compatibility)
- No external deps - uses Anki's bundled libraries

## Key Anki Add-on Patterns

```python
from aqt import mw           # Main window
from aqt import gui_hooks    # Event hooks
from aqt.qt import *         # Qt widgets (QTimer, QDialog, etc)
from aqt.utils import showInfo, showWarning
from aqt.sound import av_player  # Sound playback
```

Config access:
```python
config = mw.addonManager.getConfig(__name__)
mw.addonManager.writeConfig(__name__, config)
```

## Required Hooks

- `gui_hooks.profile_did_open` - init timer on profile load
- `gui_hooks.reviewer_did_show_question` - detect active reviewing
- `gui_hooks.reviewer_will_end` - pause timer when leaving reviewer

## File Structure (Target)

```
break_reminder/
├── __init__.py      # Entry point, hook registration
├── config.json      # Default settings
├── config.md        # User docs for config
├── timer.py         # QTimer-based study/break timer
├── dialogs.py       # Break popup, settings dialog
├── activities.py    # Activity pool management
├── sounds.py        # av_player wrapper
└── user_files/      # Preserved on upgrade
    ├── break_start.wav
    └── break_end.wav
```

## Testing

Run Anki from terminal to see print() output. Hold Shift while starting Anki to disable all add-ons.

## Distribution

Create `.ankiaddon` zip (contents only, no parent folder). Delete `__pycache__` before zipping.

## Issue tracking
Run `bd quickstart` at the start of every sesson to get context on how to use beads to do issue tracking while doing development work
