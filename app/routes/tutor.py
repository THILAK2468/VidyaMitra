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
    previous_topic: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


@router.get("/topics")
async def topics():
    """Returns all available Class 8 Science topics in the curriculum."""
    return {
        "topics": get_all_topics()
    }


@router.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Text-based science question query.
    Retrieves the lesson, supports follow-up questions, and generates an age-appropriate, grounded response.
    """
    result = generate_tutor_response(
        question=request.question,
        language=request.language,
        previous_topic=request.previous_topic,
        conversation_history=request.conversation_history
    )
    return result
