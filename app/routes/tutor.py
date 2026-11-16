from typing import Optional, List, Dict
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.curriculum import get_all_topics
from app.services.tutor_engine import generate_tutor_response

router = APIRouter(
    prefix="/tutor",
    tags=["AI Tutor"]
)


class QuestionRequest(BaseModel):
    question: str
    language: str = "te"
    subject: Optional[str] = "Science"
    student_class: Optional[str] = "Class 8"
    previous_topic: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


@router.get("/topics")
async def topics(subject: Optional[str] = "Science"):
    """Returns available topics for the selected subject."""
    return {
        "subject": subject,
        "topics": get_all_topics()
    }


@router.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Grade-adaptive and multi-subject question query.
    Generates an age-appropriate, grounded response across Science, Math, Social, English.
    """
    result = generate_tutor_response(
        question=request.question,
        language=request.language,
        subject=request.subject or "Science",
        student_class=request.student_class or "Class 8",
        previous_topic=request.previous_topic,
        conversation_history=request.conversation_history
    )
    return result
