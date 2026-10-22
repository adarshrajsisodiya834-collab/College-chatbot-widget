# College Chatbot MVP — Scripted Edition

A plug-and-play college query chatbot with a floating embeddable widget and a FastAPI backend.

This MVP intentionally uses **scripted, knowledge-base answers instead of an LLM API**. The matching engine accepts different phrasings of common questions and returns an authored answer from the college knowledge base. This makes the demo deterministic, free to run, easy to debug and safe from hallucinated college-specific information.

## Included
- Embeddable `widget.js` with isolated Shadow DOM UI
- Floating launcher and responsive chat window
- FastAPI backend and `/api/v1/chat` endpoint
- Per-widget configuration and knowledge isolation
- Anonymous conversation sessions
- Scripted answer engine with flexible phrase/keyword matching
- College FAQ knowledge base covering admissions, courses, eligibility, fees, scholarships, hostel, transport, exams, results, departments, faculty, placements, campus, rules and contacts
- Source references
- Feedback endpoint
- Basic rate limiting
- Text/PDF/URL ingestion for adding more scripted knowledge entries
- Demo college website

## Quick start

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000/`.

## Widget installation

```html
<script src="http://127.0.0.1:8000/widget.js"
        data-widget-id="COLLEGE_ABC_001"
        async></script>
```

The widget is an overlay and does not require a placeholder `<div>` on the host website.

## How scripted answers work

Each knowledge item can contain:

- `question` — the canonical question
- `aliases` — other ways a visitor may ask it
- `keywords` — important matching terms
- `answer` — the exact response shown to the visitor
- `content` — the source/reference text

For example, questions such as `How do I apply?`, `What is the admission process?`, and `How can I get admission?` can all map to the same authored admission answer.

No Gemini, OpenAI, or other LLM API key is required.

## Add more knowledge

The existing ingestion commands still work:

```bash
python scripts/ingest.py --widget COLLEGE_ABC_001 --text-file notes.txt
python scripts/ingest.py --widget COLLEGE_ABC_001 --pdf prospectus.pdf
python scripts/ingest.py --widget COLLEGE_ABC_001 --url https://college.example/admissions
```

For the best scripted-chat behaviour, manually add `question`, `aliases`, `keywords`, and `answer` fields to knowledge JSON entries.

## Project structure

```text
college-chatbot-mvp/
├── backend/
│   ├── app/
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── rag.py
│   │   └── store.py
│   └── data/
│       └── COLLEGE_ABC_001.json
├── demo/
│   └── index.html
├── widget/
│   └── widget.js
├── scripts/
│   └── ingest.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
