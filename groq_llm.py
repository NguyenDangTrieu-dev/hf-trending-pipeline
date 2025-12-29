import os
import json
import time
import requests
from typing import Dict
from schema import SinglePaper

PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"

BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
}

SYSTEM_PROMPT = """
You are a data extraction system.

Your entire output MUST be a single valid JSON object.
Do NOT include explanations.
Do NOT include markdown.
Do NOT wrap output in ```.

{
  "title": string,
  "summary": string | null,
  "github_link": string | null,
  "paper_link": string,
  "published_at": string | null
}

Return ONLY the JSON object.
Use null if missing.
Any extra text is invalid.
""".strip()

def extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Invalid JSON")
    return text[start:end + 1]

def parse_one_paper(item: Dict, max_retry: int = 3) -> SinglePaper:
    for attempt in range(max_retry):
        model = PRIMARY_MODEL if attempt == 0 else FALLBACK_MODEL
        try:
            payload = {
                "model": model,
                "temperature": 0,
                "max_tokens": 600,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "title": item["title"],
                                "paper_link": item["paper_link"],
                                "text": item["text"],
                            },
                            ensure_ascii=False,
                        ),
                    },
                ],
            }

            resp = requests.post(
                BASE_URL,
                headers=HEADERS,
                json=payload,
                timeout=30,
            )

            if resp.status_code == 429:
                time.sleep(2 + attempt)
                continue

            resp.raise_for_status()

            raw = resp.json()["choices"][0]["message"]["content"]
            data = json.loads(extract_json(raw))

            paper = SinglePaper.model_validate(data)

            time.sleep(2)
            return paper

        except Exception as e:
            if attempt == max_retry - 1:
                raise e
