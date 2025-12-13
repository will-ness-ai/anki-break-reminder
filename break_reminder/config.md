# Break Reminder Configuration

## Timer Settings

- **study_duration_minutes** (default: 25)
  Minutes of active reviewing before a break reminder appears.

- **break_duration_minutes** (default: 5)
  Length of the break countdown timer.

- **snooze_duration_minutes** (default: 5)
  How long to delay the break when you click "Snooze".

## Sound Settings

- **enable_sounds** (default: true)
  Play sounds when break starts and ends.

- **break_start_volume** (default: 0.7)
  Volume for break start sound (0.0 to 1.0).

- **break_end_volume** (default: 0.7)
  Volume for break end sound (0.0 to 1.0).

## Custom Image

- **break_image_path** (default: "")
  Path to a custom image displayed in the break dialog. Leave empty for default. Supports PNG, JPG, GIF.

## Activities

- **break_activities** (default: list of 8 activities)
  Pool of activity suggestions shown during breaks. One is randomly selected each time.

  Default activities:
  - Stand up and stretch for 2 minutes
  - Get a glass of water
  - Look at something 20 feet away for 20 seconds
  - Do 10 deep breaths
  - Walk around the room
  - Do 10 jumping jacks
  - Rest your eyes (close them for 1 minute)
  - Step outside for fresh air

  Add your own or remove any you don't like.
