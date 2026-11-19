import re
from pathlib import Path


# Find the project folder and policy document folder.
BASE_DIR = Path(__file__).resolve().parent.parent
POLICY_DIR = BASE_DIR / "data" / "policy_docs"


# Common words that do not help identify a policy.
STOP_WORDS = {
    "what", "is", "the", "a", "an", "how",
    "do", "does", "can", "i", "my", "are",
    "to", "of", "for", "in", "on", "and",
    "tell", "me", "about", "please", "policy",
}


def tokenize(text: str) -> set[str]:
    """Convert text into lowercase words."""
    words = re.findall(r"[a-zA-Z]+", text.lower())

    return {
        word
        for word in words
        if word not in STOP_WORDS
    }


def search_policies(question: str, limit: int = 3) -> list[dict]:
    """Find policy documents that match the user's question."""

    question_words = tokenize(question)

    # Do not search if the question has no useful words.
    if not question_words:
        return []

    matches = []

    # Read every policy text file.
    for file_path in POLICY_DIR.glob("*.txt"):

        content = file_path.read_text(encoding="utf-8")

        # Include the filename so questions like
        # "What is the leave policy?" can match leave_policy.txt.
        searchable_text = file_path.stem.replace("_", " ") + " " + content

        document_words = tokenize(searchable_text)

        # Count how many question words appear in this document.
        score = len(question_words.intersection(document_words))

        if score > 0:
            matches.append({
                "source": file_path.name,
                "content": content,
                "score": score,
            })

    # Put the strongest matches first.
    matches.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return matches[:limit]