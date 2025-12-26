from crawler import fetch_page, parse_html
from groq_llm import parse_one_paper
from otel import setup_tracer

tracer = setup_tracer()

def main():
    with tracer.start_as_current_span("crawl_hf_trending"):
        with tracer.start_as_current_span("fetch_page"):
            html = fetch_page()

        with tracer.start_as_current_span("parse_html"):
            items = parse_html(html)

        results = []

        for item in items:
            with tracer.start_as_current_span("groq_parse_one_paper") as span:
                span.set_attribute("paper.title", item["title"])
                try:
                    paper = parse_one_paper({
                        "title": item["title"],
                        "paper_link": item["paper_link"],
                        "text": item["raw_text"][:1200],
                    })
                    results.append(paper)
                except Exception as e:
                    print("❌ Failed paper:", item["title"], e)

        for p in results:
            print(p.model_dump())

if __name__ == "__main__":
    main()
