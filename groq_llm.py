import os
import json
import time
import requests
from schema import PaperList, SinglePaper

PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY is not set")

BASE_URL = "https://api.groq.com/openai/v1"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
}

SYSTEM_PROMPT = """
You are a data extraction system.

You MUST return raw JSON only.
DO NOT use markdown.
DO NOT wrap output in ``` or ```json.

Return JSON matching this schema exactly:

{
  "papers": [
    {
      "title": string,
      "summary": string | null,
      "github_link": string | null,
      "paper_link": string,
      "published_at": string | null
    }
  ]
}
Rules:
- No explanation
- No markdown
- No extra fields
- Use null if missing
"""
def parse_one_paper(item: dict, max_retry=3) -> SinglePaper:
    for attempt in range(max_retry):
        try:
            payload = {
                "model": PRIMARY_MODEL if attempt == 0 else FALLBACK_MODEL,
                "temperature": 0,
                "max_tokens": 800,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(item, ensure_ascii=False)},
                ],
            }

            r = requests.post(
                f"{BASE_URL}/chat/completions",
                headers=HEADERS,
                json=payload,
                timeout=30,
            )

            if r.status_code == 429:
                wait = 2 + attempt
                print(f"⏳ Rate limited, retry in {wait}s...")
                time.sleep(wait)
                continue

            r.raise_for_status()

            content = extract_json(r.json()["choices"][0]["message"]["content"])
            data = json.loads(content)

            if "papers" in data:
                data = data["papers"][0]

            time.sleep(2)

            return SinglePaper.model_validate(data)

        except Exception as e:
            if attempt == max_retry - 1:
                raise e


def extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]
    return text.strip()


def parse_with_groq(items: list[dict]) -> PaperList:
    compact_items = [
        {
            "title": i["title"],
            "paper_link": i["paper_link"],
            "text": i["raw_text"][:1200],
        }
        for i in items
    ]

    payload = {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0,
        "max_tokens": 2000,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(compact_items, ensure_ascii=False)},
        ],
    }

    r = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=HEADERS,
        json=payload,
        timeout=60,
    )

    if r.status_code != 200:
        print("❌ Groq error response:")
        print(r.text)
        r.raise_for_status()

    content = r.json()["choices"][0]["message"]["content"]
    clean_json = extract_json(content)

    return PaperList.model_validate_json(clean_json)
