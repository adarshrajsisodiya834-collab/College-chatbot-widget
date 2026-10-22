import argparse
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.store import add_item
from backend.app.config import WIDGET_CONFIGS

def add_text(widget, title, content, source_type="text", url=None, page=None):
    item = add_item({
        "widget_id": widget, "title": title, "content": content,
        "type": source_type, "source_url": url, "page": page
    })
    print(f"Added: {item['title']}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--widget", required=True)
    parser.add_argument("--text-file")
    parser.add_argument("--pdf")
    parser.add_argument("--url")
    parser.add_argument("--title")
    args = parser.parse_args()

    if args.widget not in WIDGET_CONFIGS:
        raise SystemExit(f"Unknown widget: {args.widget}")

    if args.text_file:
        p = Path(args.text_file)
        add_text(args.widget, args.title or p.stem, p.read_text(encoding="utf-8"))
        return

    if args.pdf:
        p = Path(args.pdf)
        for n, page in enumerate(PdfReader(str(p)).pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                add_text(args.widget, f"{p.name} — page {n}", text, "pdf", page=n)
        return

    if args.url:
        r = requests.get(args.url, timeout=20, headers={"User-Agent": "CollegeChatbot/1.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = "\n".join(soup.stripped_strings)
        add_text(args.widget, args.title or args.url, text, "url", url=args.url)
        return

    raise SystemExit("Provide --text-file, --pdf, or --url.")

if __name__ == "__main__":
    main()
