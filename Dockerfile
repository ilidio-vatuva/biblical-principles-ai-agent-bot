FROM python:3.11-slim

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create volume mount points
RUN mkdir -p /app/knowledge /app/logs

# Register the 00:00 cron job
RUN echo "0 0 * * * cd /app && python main.py >> /app/logs/cron.log 2>&1" | crontab -

# Pass runtime env vars to cron's environment
RUN touch /etc/environment

CMD mkdir -p /app/logs \
    && touch /app/logs/cron.log \
    && printenv | grep -E "ANTHROPIC|TELEGRAM|SYSTEM_PROMPT" >> /etc/environment \
    && cron \
    && tail -f /app/logs/cron.log
