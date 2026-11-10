from __future__ import annotations

import os
from typing import Any


SYSTEM_PROMPT = """You are a practical, empathetic Virtual Key Account Manager for an online marketplace seller.
Your job is to own the seller's sales-recovery problem, not answer FAQs.
Use only the verified seller metrics and action recommendations supplied in context.
Never invent data, promise sales growth, claim an action was executed, or imply access to live Snapdeal systems.
Ask one focused follow-up question at a time when information is missing.
Prioritize urgent operational blockers before suggesting discounts or ad spend.
Explain recommendations in plain, concise spoken English.
End each diagnostic turn with one clear next action or one focused question."""


def build_context(analysis: dict[str, Any], seller_message: str) -> str:
    return (
        f"Seller says: {seller_message}\n"
        f"Verified analysis JSON: {analysis}\n"
        "Create a warm spoken response of 3-6 sentences. Mention the strongest evidence, "
        "the top priority, and ask one useful question to clarify the cause or seller constraint."
    )


def generate_reply(analysis: dict[str, Any], seller_message: str) -> tuple[str, str]:
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        return fallback_reply(analysis, seller_message), "rules"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        response = client.models.generate_content(
            model=model,
            contents=build_context(analysis, seller_message),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
                max_output_tokens=220,
            ),
        )
        answer = (response.text or "").strip()
        if answer:
            return answer, "gemini"
    except Exception:
        # Keep demo available even if the optional LLM call fails.
        pass
    return fallback_reply(analysis, seller_message), "rules"


def fallback_reply(analysis: dict[str, Any], seller_message: str) -> str:
    actions = analysis["actions"]
    first = actions[0] if actions else None
    if not first:
        return "Thanks for explaining. I have reviewed the available indicators. Could you tell me whether anything changed recently in your pricing, listing content, inventory or promotions?"
    signals = analysis["signals"]
    evidence = " ".join(item["evidence"] for item in signals[:2])
    question = (
        "Did you face stock-outs or dispatch delays on your best-selling products in the last two weeks?"
        if first["priority"] == "P0"
        else "Did you recently change the main images, price, product details or delivery settings on your top listings?"
    )
    return (
        f"I understand the concern. {analysis['summary']} {evidence} "
        f"I recommend we start with {first['title'].lower()}. {first['steps']} "
        f"{question}"
    )
