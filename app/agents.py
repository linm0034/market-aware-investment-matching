from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List


from . import config  

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate



llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    api_key=os.environ["OPENAI_API_KEY"],
)



RECOMMEND_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a conservative wealth management AI assistant. "
            "Do NOT promise returns. Use cautious language. "
            "Always include key risks and who should not buy. "
            "You MUST output strictly valid JSON only (no markdown, no extra text). "
            "If evidence is insufficient, explicitly say so in the reasons.",
        ),
        (
            "user",
            "Client profile (JSON):\n{client}\n\n"
            "Market context (JSON):\n{market}\n\n"
            "Candidate product (structured fields JSON):\n{product}\n\n"
            "Evidence snippets (RAG, list of dicts):\n{evidence}\n\n"
            "Task: Output JSON ONLY with this schema:\n"
            "{{"
            "\"why_client_fit\": string, "
            "\"why_market_fit\": string, "
            "\"key_risks\": [string], "
            "\"who_should_not_buy\": [string]"
            "}}",
        ),
    ]
)

AUDIT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a strict compliance/audit reviewer for wealth management recommendations. "
            "Check for: (1) guaranteed-return language, (2) missing risk disclosures, "
            "(3) suitability violations vs client profile, (4) claims not supported by evidence. "
            "You MUST output strictly valid JSON only (no markdown, no extra text).",
        ),
        (
            "user",
            "Client (JSON):\n{client}\n\n"
            "Market (JSON):\n{market}\n\n"
            "Product (JSON):\n{product}\n\n"
            "Draft recommendation JSON:\n{draft}\n\n"
            "Evidence snippets:\n{evidence}\n\n"
            "Output JSON ONLY with this schema:\n"
            "{{"
            "\"is_ok\": boolean, "
            "\"issues\": [string], "
            "\"revised\": {{"
            "\"why_client_fit\": string, "
            "\"why_market_fit\": string, "
            "\"key_risks\": [string], "
            "\"who_should_not_buy\": [string]"
            "}}"
            "}}",
        ),
    ]
)


async def recommend_one(
    client: Dict[str, Any],
    market: Dict[str, Any],
    product: Dict[str, Any],
    evidence: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Generate a recommendation rationale for ONE product.
    Always returns a dict with keys:
    why_client_fit, why_market_fit, key_risks, who_should_not_buy
    """
    msg = RECOMMEND_PROMPT.format_messages(
        client=json.dumps(client, ensure_ascii=False),
        market=json.dumps(market, ensure_ascii=False),
        product=json.dumps(product, ensure_ascii=False),
        evidence=json.dumps(evidence, ensure_ascii=False),
    )
    res = await llm.ainvoke(msg)

    data = _safe_json(res.content)
    return _ensure_reco_schema(data)


async def audit_one(
    client: Dict[str, Any],
    market: Dict[str, Any],
    product: Dict[str, Any],
    draft: Dict[str, Any],
    evidence: List[Dict[str, str]],
) -> Dict[str, Any]:
    
    msg = AUDIT_PROMPT.format_messages(
        client=json.dumps(client, ensure_ascii=False),
        market=json.dumps(market, ensure_ascii=False),
        product=json.dumps(product, ensure_ascii=False),
        draft=json.dumps(draft, ensure_ascii=False),
        evidence=json.dumps(evidence, ensure_ascii=False),
    )
    res = await llm.ainvoke(msg)

    data = _safe_json(res.content)
    return _ensure_audit_schema(data)


def _safe_json(text: str) -> Dict[str, Any]:
    
    t = (text or "").strip()

    # Remove markdown fences if any
    if t.startswith("```"):
        # keep middle part
        parts = t.split("```")
        if len(parts) >= 2:
            t = parts[1].strip()
        # remove optional leading "json"
        if t.lower().startswith("json"):
            t = t[4:].strip()

    # Extract the first JSON object block
    m = re.search(r"\{.*\}", t, flags=re.S)
    if m:
        t = m.group(0).strip()

    try:
        return json.loads(t)
    except Exception:
        return {}


def _ensure_reco_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure recommendation schema keys exist and types are reasonable,
    so the API doesn't 500.
    """
    if not isinstance(data, dict):
        data = {}

    why_client_fit = data.get("why_client_fit")
    why_market_fit = data.get("why_market_fit")
    key_risks = data.get("key_risks")
    who_should_not_buy = data.get("who_should_not_buy")

    if not isinstance(why_client_fit, str):
        why_client_fit = "Insufficient structured output; unable to generate a reliable client-fit rationale."
    if not isinstance(why_market_fit, str):
        why_market_fit = "Insufficient structured output; unable to generate a reliable market-fit rationale."

    if not isinstance(key_risks, list) or not all(isinstance(x, str) for x in key_risks):
        key_risks = ["Insufficient structured output; risks could not be fully extracted."]
    if not isinstance(who_should_not_buy, list) or not all(isinstance(x, str) for x in who_should_not_buy):
        who_should_not_buy = ["N/A"]

    return {
        "why_client_fit": why_client_fit,
        "why_market_fit": why_market_fit,
        "key_risks": key_risks,
        "who_should_not_buy": who_should_not_buy,
    }


def _ensure_audit_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure audit schema exists:
    { is_ok: bool, issues: [str], revised: reco_schema }
    """
    if not isinstance(data, dict):
        data = {}

    is_ok = data.get("is_ok")
    issues = data.get("issues")
    revised = data.get("revised")

    if not isinstance(is_ok, bool):
        is_ok = True  # be permissive if model fails
    if not isinstance(issues, list) or not all(isinstance(x, str) for x in issues):
        issues = []
    if not isinstance(revised, dict):
        revised = {}

    revised = _ensure_reco_schema(revised)

    return {
        "is_ok": is_ok,
        "issues": issues,
        "revised": revised,
    }
