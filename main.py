from datetime import date

from agent import generate_daily_content
from bot import send_message
from repository import (
    advance_principle,
    current_day_number,
    load_state,
    save_state,
    this_weeks_monday,
)


def main() -> None:
    day = current_day_number()

    # Sunday — rest day, no message
    if day == 7:
        print("Sunday — no message scheduled.")
        return

    state = load_state()
    monday = this_weeks_monday().isoformat()

    if state["week_start"] is None:
        # First ever run: anchor to this week
        state["week_start"] = monday
        save_state(state)
    elif day == 1 and state["week_start"] != monday:
        # New week started — advance to the next principle
        state = advance_principle(state)
        save_state(state)

    principle = state["current_principle"]
    print(f"[{date.today()}] Principle {principle} — Day {day}/{'5' if day <= 5 else 'Sábado'}")

    content = generate_daily_content(principle, day)
    send_message(content)

    print("Message sent.")


if __name__ == "__main__":
    main()
