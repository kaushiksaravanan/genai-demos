"""
Shared LLM utility for all demos.
Auto-rotates between Gemini and Groq via CipherStack.
"""
import requests
import json
from functools import lru_cache

CIPHERSTACK_TOKEN = "CIPHERSTACK_TOKEN_REVOKED_PLACEHOLDER_0000000000"
CIPHERSTACK_URL = "https://cipherstack.kaushik.cv/api/v1"

_key_cache = {}


def vend_key(group: str) -> tuple[str, str]:
    resp = requests.get(
        f"{CIPHERSTACK_URL}/vend/{group}",
        headers={"Authorization": f"Bearer {CIPHERSTACK_TOKEN}"},
    )
    data = resp.json()
    return data["key"], data.get("key_id", "")


def report_rate_limit(key_id: str):
    requests.post(
        f"{CIPHERSTACK_URL}/report",
        headers={"Authorization": f"Bearer {CIPHERSTACK_TOKEN}", "Content-Type": "application/json"},
        json={"key_id": key_id, "error": "429_rate_limited"},
    )


def call_groq(prompt: str, system_prompt: str = "", temperature: float = 0.7, max_tokens: int = 1024) -> str:
    key, key_id = vend_key("groq")
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
    )
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"[Groq error {resp.status_code}]: {resp.text[:200]}"


def call_gemini(prompt: str, system_prompt: str = "", temperature: float = 0.7, max_tokens: int = 1024) -> str:
    key, key_id = vend_key("gemini")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    if system_prompt:
        body["systemInstruction"] = {"parts": [{"text": system_prompt}]}

    resp = requests.post(url, json=body)
    if resp.status_code == 200:
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates:
            return candidates[0]["content"]["parts"][0]["text"]
        return "[No response generated]"
    elif resp.status_code == 429:
        report_rate_limit(key_id)
        return None  # Signal to try fallback
    return f"[Gemini error {resp.status_code}]: {resp.text[:200]}"


def call_llm(prompt: str, system_prompt: str = "", temperature: float = 0.7, max_tokens: int = 1024) -> str:
    """Call LLM with automatic fallback: Gemini → Groq."""
    # Try Gemini first (up to 2 keys)
    for _ in range(2):
        result = call_gemini(prompt, system_prompt, temperature, max_tokens)
        if result is not None:
            return result

    # Fallback to Groq
    return call_groq(prompt, system_prompt, temperature, max_tokens)


def call_llm_with_tools(prompt: str, tools_schema: list, temperature: float = 0.3) -> dict:
    """Call Gemini with function calling. Falls back to simulated response if quota hit."""
    key, key_id = vend_key("gemini")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"functionDeclarations": tools_schema}],
        "generationConfig": {"temperature": temperature},
    }
    resp = requests.post(url, json=body)
    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 429:
        report_rate_limit(key_id)
    # Fallback: ask Groq to simulate tool selection
    fallback_prompt = f"""Given these available tools:
{json.dumps([{"name": t["name"], "description": t["description"]} for t in tools_schema], indent=2)}

User request: {prompt}

Which tool(s) would you call and with what arguments? Respond in JSON format:
{{"tool_calls": [{{"name": "tool_name", "args": {{...}}}}]}}"""
    text = call_groq(fallback_prompt, temperature=0.2)
    return {"fallback": True, "text": text}
