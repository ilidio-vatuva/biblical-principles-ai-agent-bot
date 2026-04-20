import os

import requests

import anthropic

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")


def _load_system_prompt() -> str:
    if(os.path.exists(os.path.join(KNOWLEDGE_DIR, "system_prompt.md"))):
        with open(os.path.join(KNOWLEDGE_DIR, "system_prompt.md")) as f:
            return f.read()
    prompt_url = os.environ.get("SYSTEM_PROMPT_URL")
    if prompt_url:
        response = requests.get(prompt_url, timeout=15)
        response.raise_for_status()
        return response.text
    raise RuntimeError("No system prompt found: neither knowledge/system_prompt.md nor SYSTEM_PROMPT_URL env var is available.")


def generate_daily_content(principle_number: int, day_number: int) -> str:
    """
    Generate the Telegram message for the given principle and day.

    day_number: 1–5 = Monday–Friday (daily content)
                6   = Saturday (weekly meeting questions)
    """
    client = anthropic.Anthropic()
    system_prompt = _load_system_prompt()

    if day_number <= 5:
        user_message = (
            f"Gera o conteúdo para o **Dia {day_number}/5** do **Princípio {principle_number}**.\n\n"
            "Segue o template de resposta definido no teu sistema. "
            "Inclui: nome do princípio, frase-chave, versículo âncora, "
            "leitura bíblica do dia, reflexão (2 perguntas) e treino (1 ação prática)."
        )
    else:  # day 6 — Saturday
        user_message = (
            f"Gera o **Encontro Semanal (Sábado)** para o **Princípio {principle_number}**.\n\n"
            "Inclui: resumo do princípio da semana, 3–4 perguntas de discussão "
            "para o encontro e a pergunta de alinhamento profunda."
        )

    message = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    return next(block.text for block in message.content if block.type == "text")
