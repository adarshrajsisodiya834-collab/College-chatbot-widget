"""Local, scripted chatbot engine.

No LLM or external API is used. Answers are stored in the widget's JSON
knowledge base and selected using deterministic text matching.
"""

import re
from difflib import SequenceMatcher

from .store import load_items

FALLBACK = (
    "I couldn't find that information in the college's available knowledge. "
    "Please check the official college website or contact the relevant college office."
)

STOP_WORDS = {
    "a", "an", "and", "are", "about", "can", "could", "do", "does", "for",
    "from", "how", "i", "in", "is", "it", "me", "of", "on", "please", "tell",
    "the", "to", "what", "when", "where", "which", "who", "why", "with", "you",
    "your", "my", "we", "our", "this", "that", "be", "at", "or", "any", "there",
}


def _tokens(text):
    return {
        t for t in re.findall(r"[a-z0-9]+", (text or "").lower())
        if t not in STOP_WORDS and len(t) > 1
    }


def _normalise(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (text or "").lower())).strip()


def _score(query, item):
    q = _normalise(query)
    q_tokens = _tokens(query)
    question = item.get("question", "")
    aliases = item.get("aliases", []) or []
    keywords = item.get("keywords", []) or []
    searchable = " ".join([
        item.get("title", ""),
        question,
        " ".join(aliases),
        " ".join(keywords),
        item.get("content", ""),
    ])
    text_tokens = _tokens(searchable)

    if not q:
        return 0.0

    score = 0.0
    if question:
        nq = _normalise(question)
        if q == nq:
            score += 10.0
        elif q in nq or nq in q:
            score += 6.0
        score += 5.0 * SequenceMatcher(None, q, nq).ratio()

    for alias in aliases:
        na = _normalise(alias)
        if q == na:
            score += 9.0
        elif q in na or na in q:
            score += 5.0
        score += 4.0 * SequenceMatcher(None, q, na).ratio()

    overlap = len(q_tokens & text_tokens)
    if q_tokens:
        # Do not let fuzzy similarity alone turn unrelated questions into
        # false positives. A useful match must share at least one meaningful
        # word with the knowledge item (unless the query is an exact phrase).
        if overlap == 0 and not any(q == _normalise(v) for v in [question, *aliases]):
            return 0.0
        score += 8.0 * overlap / len(q_tokens)

    # Give explicitly configured keywords extra weight.
    keyword_tokens = set()
    for keyword in keywords:
        keyword_tokens |= _tokens(keyword)
    score += 5.0 * len(q_tokens & keyword_tokens) / max(1, len(q_tokens))

    return score


def retrieve(widget_id, query, top_k=5):
    """Return matching knowledge records in the shape expected by main.py."""
    items = load_items(widget_id)
    ranked = []
    for item in items:
        if not item.get("content", "").strip():
            continue
        score = _score(query, item)
        if score <= 3.5:
            continue
        ranked.append((score, item))

    ranked.sort(key=lambda pair: pair[0], reverse=True)
    results = []
    for score, item in ranked[:top_k]:
        results.append({
            "id": item.get("id", ""),
            "title": item.get("title", "College Knowledge"),
            "text": item.get("content", ""),
            "type": item.get("type", "faq"),
            "page": item.get("page"),
            "url": item.get("source_url"),
            "question": item.get("question", ""),
            "answer": item.get("answer", item.get("content", "")),
            "score": round(score, 4),
        })
    return results


def _looks_like_greeting(query):
    tokens = _tokens(query)
    raw = _normalise(query)
    greetings = {"hi", "hello", "hey", "hii", "good morning", "good afternoon", "good evening"}
    return raw in greetings or (tokens and tokens <= {"hi", "hello", "hey", "hii"})


def _looks_like_thanks(query):
    return bool(re.search(r"\b(thanks|thank you|thx|appreciate it)\b", query.lower()))


def _contextual_query(query, history):
    """Make short follow-up questions searchable using the previous user turn."""
    if not history:
        return query
    tokens = _tokens(query)
    if len(tokens) >= 3:
        return query
    previous = [m.get("content", "") for m in history if m.get("role") == "user"]
    if previous:
        return f"{previous[-1]} {query}"
    return query


def scripted_answer(query, results, history=None):
    """Return a deterministic answer from the knowledge base."""
    if _looks_like_greeting(query):
        return "Hello! I'm the ABC College Assistant. I can help with admissions, courses, eligibility, fees, scholarships, departments, exams, results, hostel, transport, placements and campus facilities."
    if _looks_like_thanks(query):
        return "You're welcome! If you have another college-related question, feel free to ask."

    if not results and history:
        contextual = _contextual_query(query, history)
        if contextual != query:
            results = retrieve(history[-1].get("widget_id", "COLLEGE_ABC_001") if history else "COLLEGE_ABC_001", contextual)

    if not results:
        return FALLBACK

    best = results[0]
    # The answer is intentionally authored in the knowledge base. There is no generation.
    answer = best.get("answer") or best.get("text")
    return answer.strip() if answer else FALLBACK


# Kept for compatibility with older versions of main.py. It is deliberately
# not an LLM call; it returns the scripted answer.
def llm_answer(query, results, history=None):
    return scripted_answer(query, results, history)


def extractive_answer(query, results):
    return scripted_answer(query, results)
