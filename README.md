# Biblical Principles AI Agent Bot

A cron-triggered AI agent that delivers daily biblical principle content to a Telegram channel. No user interaction — fully automated broadcast at 00:00 every day.

## How it works

Each week focuses on one biblical principle. The agent generates and sends:

| Day | Content |
|---|---|
| Monday – Friday | Daily plan: anchor verse, reading, 2 reflection questions, 1 practical action |
| Saturday | Weekly meeting: discussion questions + alignment question |
| Sunday | Rest — no message |

On Monday of each new week, the agent automatically advances to the next principle. The first 12 principles are already completed; the bot starts from principle 13.

## Architecture

```
cron (00:00)
    └── main.py          orchestration
         ├── repository.py   state (current principle + week)
         ├── agent.py        Claude API → generates content
         └── bot.py          Telegram Bot API → sends message
```

The system prompt lives in `knowledge/system_prompt.md` (not committed — see Setup).  
State is persisted in `state.json` (auto-created on first run).

## Setup

### 1. Clone and install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```
ANTHROPIC_API_KEY=your_anthropic_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=@your_channel_or_-100xxxxxxxxxx
```

- **Anthropic API key** → [console.anthropic.com](https://console.anthropic.com)
- **Telegram bot token** → talk to [@BotFather](https://t.me/BotFather) → `/newbot`
- **Chat ID** → `@channel_username` (public) or numeric ID `-100xxxxxxxxxx` (private). The bot must be an **Administrator** of the channel.

### 3. Add the system prompt

Place your system prompt at `knowledge/system_prompt.md`.  
Alternatively, host it remotely and set `SYSTEM_PROMPT_URL` in `.env`.

## Running

### Locally — manual trigger

```bash
python main.py
```

### Locally — cron at 00:00

```bash
crontab -e
```

Add:
```
0 0 * * * cd /path/to/biblical-principles-ai-agent-bot && python main.py >> logs/cron.log 2>&1
```

### Test server (preview without sending)

```bash
uvicorn server:app --reload
# Open http://localhost:8000/docs
```

| Endpoint | Description |
|---|---|
| `GET /state` | Current principle and week |
| `POST /preview` | Generate content, return it — nothing sent to Telegram |
| `POST /trigger` | Full run: generate + send to Telegram |

## Docker

### Build and run

```bash
docker build -t biblical-bot .

docker run -d \
  --name biblical-bot \
  --env-file .env \
  -v $(pwd)/knowledge:/app/knowledge \
  -v $(pwd)/state.json:/app/state.json \
  -v $(pwd)/logs:/app/logs \
  biblical-bot
```

The two volumes are important:
- `knowledge/` — mounts your `system_prompt.md` into the container
- `state.json` — persists the current principle across container restarts

### View logs

```bash
docker logs -f biblical-bot
# or
tail -f logs/cron.log
```

## State

`state.json` tracks:

```json
{
  "current_principle": 13,
  "week_start": "2026-04-06"
}
```

To manually reset or jump to a different principle, edit this file directly.
