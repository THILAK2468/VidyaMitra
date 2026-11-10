import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
AUDIO_FILE = Path("tests/sample_telugu.wav")


def test_home():
    res = client.get("/")
    assert res.status_code == 200
    assert "విద్యామిత్ర" in res.text
    assert "VidyaMitra" in res.text


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_topics():
    res = client.get("/tutor/topics")
    assert res.status_code == 200
    topics = res.json()["topics"]
    topic_names = [t["topic"] if isinstance(t, dict) else t for t in topics]
    assert "Photosynthesis" in topic_names
    assert "Friction" in topic_names


def test_tutor_ask_grounded():
    res = client.post("/tutor/ask", json={
        "question": "కిరణజన్య సంయోగక్రియ అంటే ఏమిటి?",
        "language": "te"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["topic"] == "Photosynthesis"
    assert "answer" in data
    assert len(data["answer"]) > 0


def test_tutor_ask_out_of_scope():
    res = client.post("/tutor/ask", json={
        "question": "Who was William Shakespeare?",
        "language": "en"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert "available_topics" in data


def test_stt_transcription_validation():
    # Test empty file
    res = client.post(
        "/voice/transcribe",
        files={"audio_file": ("empty.wav", b"", "audio/wav")}
    )
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()

    # Test bad extension
    res = client.post(
        "/voice/transcribe",
        files={"audio_file": ("malicious.exe", b"fakecontent", "application/octet-stream")}
    )
    assert res.status_code == 400
    assert "unsupported" in res.json()["detail"].lower()


def test_voice_transcribe_live():
    if not AUDIO_FILE.exists():
        return

    with open(AUDIO_FILE, "rb") as f:
        res = client.post(
            "/voice/transcribe",
            files={"audio_file": ("test.wav", f, "audio/wav")},
            data={"language": "te"}
        )

    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "కిరణజన్య" in data["transcript"] or len(data["transcript"]) > 0
    assert "latency" in data


def test_voice_ask_end_to_end_vertical_slice():
    if not AUDIO_FILE.exists():
        return

    with open(AUDIO_FILE, "rb") as f:
        res = client.post(
            "/voice/ask",
            files={"audio_file": ("question.wav", f, "audio/wav")},
            data={"language": "te", "play_audio": "true"}
        )

    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "transcript" in data
    assert data["topic"] == "Photosynthesis"
    assert "answer" in data
    assert "timings" in data
    assert "stt_latency" in data["timings"]
    assert "llm_latency" in data["timings"]
    assert "tts_latency" in data["timings"]
    assert "total_latency" in data["timings"]
    print("\n[VERIFIED VERTICAL SLICE]")
    print("Transcript:", data["transcript"])
    print("Answer:", data["answer"])
    print("Audio URL:", data.get("audio_url"))
    print("Timings:", data["timings"])


def test_quiz_flow():
    # 1. Fetch questions for Photosynthesis
    res = client.get("/quiz/questions/Photosynthesis?language=te")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["questions"]) > 0
    q1 = data["questions"][0]
    assert "question" in q1
    assert "options" in q1
    assert len(q1["options"]) == 4

    # 2. Submit quiz answers
    answers = {q["id"]: 0 for q in data["questions"]}
    submit_res = client.post("/quiz/submit", json={
        "topic_id": "Photosynthesis",
        "answers": answers,
        "language": "te"
    })
    assert submit_res.status_code == 200
    sub_data = submit_res.json()
    assert sub_data["success"] is True
    assert "score" in sub_data
    assert "total" in sub_data
    assert "encouragement" in sub_data
    assert len(sub_data["feedback"]) == len(data["questions"])

    # 3. Check progress
    prog_res = client.get("/quiz/progress")
    assert prog_res.status_code == 200
    assert prog_res.json()["total_quizzes_taken"] > 0


def test_followup_question():
    # Follow-up without explicit topic keyword, relying on previous_topic
    res = client.post("/tutor/ask", json={
        "question": "మరి దీనివల్ల మనకు ఎలాంటి ప్రయోజనం ఉంటుంది?",
        "language": "te",
        "previous_topic": "Photosynthesis",
        "conversation_history": [
            {"question": "కిరణజన్య సంయోగక్రియ అంటే ఏమిటి?", "answer": "మొక్కలు ఆహారం తయారు చేసుకునే ప్రక్రియ."}
        ]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["topic"] == "Photosynthesis"
    assert len(data["answer"]) > 0


if __name__ == "__main__":
    print("Running tests...")
    test_home()
    print("test_home passed")
    test_health()
    print("test_health passed")
    test_topics()
    print("test_topics passed")
    test_tutor_ask_grounded()
    print("test_tutor_ask_grounded passed")
    test_tutor_ask_out_of_scope()
    print("test_tutor_ask_out_of_scope passed")
    test_stt_transcription_validation()
    print("test_stt_transcription_validation passed")
    test_voice_transcribe_live()
    print("test_voice_transcribe_live passed")
    test_voice_ask_end_to_end_vertical_slice()
    print("test_voice_ask_end_to_end_vertical_slice passed")

    # Quiz Tests
    test_quiz_flow()
    print("test_quiz_flow passed")

    # Follow-up Tests
    test_followup_question()
    print("test_followup_question passed")

    print("ALL TESTS PASSED SUCCESSFULLY!")
