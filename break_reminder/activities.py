import random
from aqt import mw


def get_random_activity():
    config = mw.addonManager.getConfig(__name__.split('.')[0])
    activities = config.get("break_activities", [])
    if not activities:
        return "Take a break!"
    return random.choice(activities)
