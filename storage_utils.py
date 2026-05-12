import json
from pathlib import Path
from datetime import datetime

STATE_DIR = Path("state")
HISTORY_FILE = STATE_DIR / "history.json"


def ensure_state_file() -> None:
    STATE_DIR.mkdir(exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text(
            json.dumps(
                {
                    "weekly_plans": [],
                    "training_history": [],
                    "meal_history": [],
                },
                indent=2,
            )
        )


def load_history() -> dict:
    ensure_state_file()
    try:
        return json.loads(HISTORY_FILE.read_text())
    except json.JSONDecodeError:
        return {
            "weekly_plans": [],
            "training_history": [],
            "meal_history": [],
        }


def save_history(history: dict) -> None:
    ensure_state_file()
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def append_history(section: str, content: str) -> None:
    history = load_history()
    if section not in history:
        history[section] = []

    history[section].append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "content": content,
        }
    )

    # Keep history compact for prompt use.
    history[section] = history[section][-8:]

    save_history(history)


def get_recent_history_text(section: str, limit: int = 3) -> str:
    history = load_history()
    items = history.get(section, [])[-limit:]

    if not items:
        return "No previous history available."

    return "\n\n".join(
        f"[{item.get('timestamp', 'unknown')}]\n{item.get('content', '')}"
        for item in items
    )