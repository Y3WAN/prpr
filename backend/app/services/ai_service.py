import json
import httpx

from app.config import settings

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)


def _build_prompt(name: str, description: str | None, menu_names: list[str], review_contents: list[str]) -> str:
    menus_text = ", ".join(menu_names) if menu_names else "정보 없음"
    reviews_text = (
        "\n".join(f"- {r}" for r in review_contents[:10]) if review_contents else "리뷰 없음"
    )
    return f"""다음 푸드트럭 정보를 바탕으로 이 가게의 특성을 잘 나타내는 한국어 키워드 3개를 생성해줘.

가게명: {name}
소개: {description or '없음'}
메뉴: {menus_text}
리뷰:
{reviews_text}

규칙:
- 키워드는 2~4글자의 짧고 인상적인 단어로
- 가게의 분위기, 음식 특성, 장점을 반영
- 반드시 JSON 배열 형태로만 응답 (예: ["맛집", "가성비", "매콤한"])
- 다른 설명 없이 JSON 배열만 출력"""


def _parse_json_array(text: str) -> list[str]:
    start = text.find("[")
    end = text.rfind("]") + 1
    if start < 0 or end <= start:
        raise ValueError(f"JSON 배열 없음: {text}")
    return json.loads(text[start:end])


async def _call_groq(prompt: str) -> list[str]:
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.7,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            json=payload,
        )
        resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"].strip()
    return _parse_json_array(text)


async def _call_gemini(prompt: str) -> list[str]:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 100, "temperature": 0.7},
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            GEMINI_URL,
            params={"key": settings.GEMINI_API_KEY},
            json=payload,
        )
        resp.raise_for_status()
    body = resp.json()
    candidates = body.get("candidates", [])
    if not candidates:
        raise ValueError(f"Gemini candidates 없음: {body}")
    text = candidates[0]["content"]["parts"][0]["text"].strip()
    return _parse_json_array(text)


async def generate_keywords(
    name: str,
    description: str | None,
    menu_names: list[str],
    review_contents: list[str],
) -> list[str]:
    prompt = _build_prompt(name, description, menu_names, review_contents)

    if settings.GROQ_API_KEY:
        return await _call_groq(prompt)

    if settings.GEMINI_API_KEY:
        return await _call_gemini(prompt)

    raise ValueError("AI API 키가 설정되지 않았습니다.")
