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


def generate_daily_content(
    principle_number: int,
    day_number: int,
    history: list[dict] | None = None,
    prior_principles: list[dict] | None = None,
) -> str:
    """
    Generate the Telegram message for the given principle and day.

    day_number:       1–5 = Monday–Friday (daily content)
                      6   = Saturday (weekly meeting questions)
    history:          list of {"day": int, "content": str} for prior days of THIS principle
    prior_principles: list of {"principle": int, "snippet": str} for principles already covered
                      in previous weeks (used to avoid cross-week thematic repetition)
    """
    client = anthropic.Anthropic()
    system_prompt = _load_system_prompt()

    # Cross-week anti-repeat: list of principles already covered in previous weeks.
    prior_block = ""
    if prior_principles:
        bullets = "\n\n".join(
            f"— Princípio {p['principle']}:\n{p['snippet']}" for p in prior_principles
        )
        prior_block = (
            "\n\nCONTEXTO — princípios já abordados em semanas anteriores "
            "(NÃO repitas o tema central, a frase-chave nem o versículo âncora destes):\n\n"
            f"{bullets}\n\n"
            f"O Princípio {principle_number} TEM de ser distinto de todos os anteriores em tema, "
            "frase-chave e versículo âncora."
        )

    # Same-week anti-repeat: variation across days within the current principle.
    anti_repeat = ""
    if history:
        anti_repeat = (
            "\n\nIMPORTANTE — evita repetição em relação aos dias anteriores desta semana:\n"
            "- NÃO repitas o mesmo versículo âncora nem versículos já citados nas leituras.\n"
            "- NÃO reutilizes os mesmos exemplos, metáforas ou ações práticas.\n"
            "- Aprofunda um ângulo NOVO do princípio (ex.: dimensão interior, relacional, "
            "comunitária, prática, espiritual) que ainda não foi abordado.\n"
            "- Varia o tom e a estrutura das perguntas de reflexão."
        )

    if day_number <= 5:
        user_message = (
            f"Gera o conteúdo para o **Dia {day_number}/5** do **Princípio {principle_number}**.\n\n"
            "Segue o template de resposta definido no teu sistema. "
            "Inclui: nome do princípio, frase-chave, versículo âncora, "
            "leitura bíblica do dia, reflexão (2 perguntas) e treino (1 ação prática)."
            f"{prior_block}"
            f"{anti_repeat}"
        )
    else:  # day 6 — Saturday
        user_message = (
            f"Gera o **Encontro Semanal (Sábado)** para o **Princípio {principle_number}**.\n\n"
            "Inclui: resumo do princípio da semana, 3–4 perguntas de discussão "
            "para o encontro e a pergunta de alinhamento profunda."
            f"{prior_block}"
            f"{anti_repeat}"
        )

    # Build conversation with prior days as context
    messages: list[dict] = []
    for entry in (history or []):
        messages.append({"role": "user", "content": f"Gera o conteúdo para o Dia {entry['day']} do Princípio {principle_number}."})
        messages.append({"role": "assistant", "content": entry["content"]})
    messages.append({"role": "user", "content": user_message})

    message = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )

    return next(block.text for block in message.content if block.type == "text")
