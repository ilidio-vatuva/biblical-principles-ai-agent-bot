import json
import os
from datetime import date, timedelta

STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")
HISTORY_DIR = os.path.join(os.path.dirname(__file__), "history")

DEFAULT_STATE = {
    "current_principle": 13,
    "week_start": None,
}


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return DEFAULT_STATE.copy()
    with open(STATE_FILE) as f:
        data = json.load(f)
    if "current_principle" not in data or not isinstance(data["current_principle"], int):
        raise ValueError(f"Invalid state.json: missing or bad 'current_principle'")
    return data


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# Utils related to date calculations and principle advancement
def this_weeks_monday() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday())

# Returns 1 for Monday, 2 for Tuesday, ..., 6 for Saturday, 7 for Sunday
def current_day_number() -> int:
    """1 = Monday … 6 = Saturday … 7 = Sunday."""
    return date.today().weekday() + 1

# Advances to the next principle and resets the week start date
def advance_principle(state: dict) -> dict:
    state["current_principle"] += 1
    state["week_start"] = this_weeks_monday().isoformat()
    return state


def _history_path(principle: int) -> str:
    return os.path.join(HISTORY_DIR, f"principle_{principle}.json")


def load_history(principle: int) -> list[dict]:
    """Load previously generated content for the given principle.
    Returns a list of {"day": int, "content": str} sorted by day."""
    path = _history_path(principle)
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def save_day_content(principle: int, day: int, content: str) -> None:
    """Append or update this day's content in the principle history."""
    os.makedirs(HISTORY_DIR, exist_ok=True)
    history = load_history(principle)
    # Replace if this day already exists
    history = [h for h in history if h["day"] != day]
    history.append({"day": day, "content": content})
    history.sort(key=lambda h: h["day"])
    with open(_history_path(principle), "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
