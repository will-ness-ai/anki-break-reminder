# Anki Break Reminder

Pomodoro-style break reminders for Anki. Tracks active study time and prompts you to take breaks with activity suggestions.

## Features

- **Study timer** - triggers after configurable minutes of active reviewing (default: 25 min)
- **Break countdown** - visual timer during breaks (default: 5 min)
- **Snooze** - delay the break reminder
- **Activity suggestions** - random break activities from a customizable pool
- **Sound notifications** - plays sounds when break starts/ends (with volume control)
- **Custom image** - display your own image in the break dialog
- **Settings dialog** - configure everything via Tools menu

## Installation

### From AnkiWeb

1. Open Anki
2. Go to Tools > Add-ons > Get Add-ons
3. Enter code: `[TODO: AnkiWeb code]`
4. Restart Anki

### Manual Install

1. Download the `.ankiaddon` file from releases
2. Double-click to install, or drag into Anki
3. Restart Anki

## Usage

1. Start reviewing cards normally
2. After the study duration, a break reminder appears
3. Choose: **Snooze**, **Start Break**, or **Back to Studying**
4. If you start a break, a countdown timer runs
5. Sound plays when break ends, timer resets

Access settings via **Tools > Break Reminder Settings**.

## Configuration

Edit via Tools > Add-ons > Break Reminder > Config, or use the settings dialog.

See [config.md](break_reminder/config.md) for all options.

## Requirements

- Anki 2.1.50+

## License

MIT
