import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

MAX_MESSAGE_LENGTH = 4096  # Telegram's hard limit per message


def send_message(text: str) -> None:
    """Send text to the configured Telegram channel/group, splitting if needed."""
    chunks = _split(text)
    for chunk in chunks:
        _post(chunk)


def _to_html(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text


def _post(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": TELEGRAM_CHAT_ID, "text": _to_html(text), "parse_mode": "HTML"},
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(f"Telegram error {response.status_code}: {response.text}")


def _split(text: str) -> list[str]:
    if len(text) <= MAX_MESSAGE_LENGTH:
        return [text]
    chunks = []
    while text:
        chunks.append(text[:MAX_MESSAGE_LENGTH])
        text = text[MAX_MESSAGE_LENGTH:]
    return chunks
