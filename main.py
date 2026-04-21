import logging
from datetime import date

from dotenv import load_dotenv

load_dotenv()

from agent import generate_daily_content
from bot import send_message
from repository import (
    advance_principle,
    current_day_number,
    load_history,
    load_state,
    save_day_content,
    save_state,
    this_weeks_monday,
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    day = current_day_number()

    # Sunday — rest day, no message
    if day == 7:
        logger.info("Sunday — no message scheduled.")
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
    logger.info("Principle %d — Day %s", principle, day if day <= 5 else "Sábado")

    try:
        history = load_history(principle)
        content = generate_daily_content(principle, day, history)
        save_day_content(principle, day, content)
        send_message(content)
    except Exception:
        logger.exception("Failed to generate or send message")
        raise

    logger.info("Message sent.")


if __name__ == "__main__":
    main()
