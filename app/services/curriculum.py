import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "class8_science.json"
)

# Cache curriculum in memory per RULES.md / ARCHITECTURE.md
_CACHED_LESSONS = None


def load_lessons():
    global _CACHED_LESSONS
    if _CACHED_LESSONS is None:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            _CACHED_LESSONS = json.load(file)
    return _CACHED_LESSONS


def find_lesson(question: str):
    """
    Finds the best matching curriculum lesson for a question.
    Supports English, Telugu, and compound/spaced Telugu variants.
    """
    lessons = load_lessons()
    q_raw = question.lower()
    q_no_space = q_raw.replace(" ", "")

    best_lesson = None
    best_score = 0

    for lesson in lessons:
        score = 0

        for keyword in lesson["keywords"]:
            kw_raw = keyword.lower()
            kw_no_space = kw_raw.replace(" ", "")

            # Match exact keyword or space-normalized compound word
            if kw_raw in q_raw or (len(kw_no_space) >= 3 and kw_no_space in q_no_space):
                score += 2 if len(kw_no_space) > 5 else 1

        if score > best_score:
            best_score = score
            best_lesson = lesson

    return best_lesson if best_score > 0 else None


def get_all_topics():
    return [
        {
            "id": lesson["id"],
            "topic": lesson["topic"],
            "grade": lesson["grade"]
        }
        for lesson in load_lessons()
    ]
