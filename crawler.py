import requests
from bs4 import BeautifulSoup

URL = "https://huggingface.co/papers/trending"

def fetch_page()->str:
    r = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'})
    r.raise_for_status()
    return r.text

def parse_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    items = []
    for article in soup.select("article"):
        title_el = article.find("h3")
        link_el = article.find("a", href=True)

        if not title_el or not link_el:
            continue

        items.append({
            "title": title_el.get_text(strip=True),
            "paper_link": "https://huggingface.co" + link_el["href"],
            "raw_text": article.get_text(" ", strip=True)
        })

    return items
