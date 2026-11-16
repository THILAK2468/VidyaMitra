from typing import Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.database import (
    get_quiz_by_topic,
    submit_quiz_answers,
    get_progress_summary
)
from app.services.curriculum import get_all_topics

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz & Assessment"]
)


class QuizSubmission(BaseModel):
    topic_id: str
    answers: Dict[str, int]
    language: str = "te"


@router.get("/topics")
async def list_quiz_topics():
    """Returns topics available for quiz practice."""
    return {
        "topics": get_all_topics()
    }


@router.get("/questions/{topic_id}")
async def fetch_quiz(
    topic_id: str,
    language: str = "te",
    subject: str = "Science",
    student_class: str = "Class 8"
):
    """
    Fetches quiz questions for a specific topic across any subject/grade in Telugu or English.
    Correct answers are omitted for student evaluation integrity.
    """
    questions = get_quiz_by_topic(topic_id, language=language, subject=subject, student_class=student_class)
    if not questions:
        raise HTTPException(
            status_code=404,
            detail=f"No quiz questions found for topic '{topic_id}'."
        )
    return {
        "success": True,
        "topic_id": topic_id,
        "language": language,
        "total_questions": len(questions),
        "questions": questions
    }


@router.post("/submit")
async def submit_quiz(submission: QuizSubmission):
    """
    Submits student quiz answers, computes score, provides feedback,
    and records the attempt in SQLite.
    """
    result = submit_quiz_answers(
        topic_id=submission.topic_id,
        answers=submission.answers,
        language=submission.language
    )
    return {
        "success": True,
        "topic_id": submission.topic_id,
        **result
    }


@router.get("/progress")
async def student_progress():
    """Returns overall student learning and quiz performance summary."""
    summary = get_progress_summary()
    return {
        "success": True,
        **summary
    }

