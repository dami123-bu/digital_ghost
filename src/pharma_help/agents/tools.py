from typing import Any


def retrieve_docs(query: str, k: int = 3) -> list[dict[str, Any]]:
    all_docs = [
        {
            "id": "doc1",
            "title": "Aspirin and gastrointestinal effects",
            "content": "Aspirin may cause stomach upset, nausea, and gastrointestinal irritation.",
        },
        {
            "id": "doc2",
            "title": "Ibuprofen precautions",
            "content": "Ibuprofen may increase risk of stomach bleeding in some patients.",
        },
        {
            "id": "doc3",
            "title": "Tylenol uses",
            "content": "Tylenol is commonly used to reduce pain and fever.",
        },
    ]

    stop_words = {
        "the", "is", "a", "an", "and", "or", "of", "to", "for", "what",
        "how", "about", "today", "again", "are", "again?", "hows"
    }

    query_words = [
        word.strip("?.!,").lower()
        for word in query.split()
        if word.strip("?.!,").lower() not in stop_words
    ]

    scored_matches = []
    for doc in all_docs:
        text = f"{doc['title']} {doc['content']}".lower()
        score = sum(1 for word in query_words if word in text)

        if score > 0:
            scored_matches.append((score, doc))

    scored_matches.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored_matches[:k]]


def synthesize_answer(query: str, docs: list[dict[str, Any]], history: list[dict[str, str]]) -> str:
    if not docs:
        return "I could not find relevant documents."

    top_doc = docs[0]

    if len(history) > 1:
        return (
            f"Considering the conversation so far, based on {top_doc['title']}, "
            f"the answer to '{query}' is: {top_doc['content']}"
        )

    return (
        f"Based on {top_doc['title']}, "
        f"the answer to '{query}' is: {top_doc['content']}"
    )