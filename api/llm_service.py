import json
import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()


def _get_env(name: str) -> Optional[str]:
    v = os.getenv(name)
    if v is None:
        return None
    v = v.strip()
    return v or None


def _base_url() -> str:
    return _get_env("LLM_BASE_URL") or "https://api.openai.com/v1"


def _api_key() -> Optional[str]:
    return _get_env("LLM_API_KEY")


def _model() -> str:
    return _get_env("LLM_MODEL") or "gpt-4.1-mini"


def _is_moonshot() -> bool:
    return "moonshot" in (_base_url() or "").lower()


def _should_disable_thinking() -> bool:
    return _is_moonshot() and _model() == "kimi-k2.6"


def is_configured() -> bool:
    return _api_key() is not None


def _build_prompt(context: dict[str, Any]) -> tuple[str, str]:
    system = (
        "你是专业摩托旅行规划助手。你必须只输出严格 JSON，不要输出任何额外文本。"
        "JSON 结构必须满足：{"
        "\"summary\":string,"
        "\"risk_items\":[{\"level\":\"high\"|\"medium\"|\"low\",\"type\":string,\"title\":string,\"reason\":string,\"action\":string}],"
        "\"day_plan\":[{\"day\":number,\"goal\":string,\"distance_km\":number,\"notes\":[string]}],"
        "\"equipment\":[{\"category\":string,\"items\":[string]}]"
        "}。"
    )
    user = json.dumps(context, ensure_ascii=False)
    return system, user


def ask_llm_json(system: str, user: str = "", max_tokens: int = 400) -> Optional[dict[str, Any]]:
    key = _api_key()
    if not key:
        return None

    base_payload = {
        "model": _model(),
        "temperature": 1,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if _should_disable_thinking():
        # kimi-k2.6 enables thinking by default, which can exhaust tokens in
        # reasoning_content and leave message.content empty for JSON tasks.
        base_payload["thinking"] = {"type": "disabled"}
        base_payload["temperature"] = 0.6

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    url = _base_url().rstrip("/") + "/chat/completions"

    with httpx.Client(timeout=120) as client:
        data = None
        # 对于 Moonshot Kimi，可能不支持 response_format="json_object"，我们直接不用它
        try:
            payload = base_payload
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                print(f"LLM API Error: {resp.status_code} {resp.text}")
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            print(f"LLM API Error: {e.response.status_code} {e.response.text}")
            raise e
        except Exception as e:
            print(f"LLM Network Error: {e}")
            raise e

    message = (((data or {}).get("choices") or [{}])[0].get("message") or {})
    raw_content = message.get("content") or ""
    reasoning_content = message.get("reasoning_content") or ""

    if isinstance(raw_content, list):
        raw_content = "".join(
            part.get("text", "") for part in raw_content if isinstance(part, dict)
        )
    if isinstance(reasoning_content, list):
        reasoning_content = "".join(
            part.get("text", "") for part in reasoning_content if isinstance(part, dict)
        )

    content = str(raw_content).strip() or str(reasoning_content).strip()
    if not content:
        return None

    if content.startswith("```"):
        lines = content.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].startswith("```"):
            content = "\n".join(lines[1:-1]).strip()

    try:
        return json.loads(content)
    except Exception:
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(content[start : end + 1])
            except Exception:
                return None
        return None

def generate_plan(context: dict[str, Any]) -> Optional[dict[str, Any]]:
    system, user = _build_prompt(context)
    return ask_llm_json(system, user)
