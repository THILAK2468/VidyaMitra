import sqlite3
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional

DB_FILE = Path("vidyamitra.db")


def hash_password(password: str) -> str:
    """Hashes password with SHA-256 and salt."""
    salt = "vidyamitra_secure_salt"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def get_db():
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes SQLite database tables and seeds initial quiz questions."""
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        student_class TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at REAL NOT NULL
    )
    """)

    # Quiz Questions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_questions (
        id TEXT PRIMARY KEY,
        topic_id TEXT NOT NULL,
        topic_name TEXT NOT NULL,
        question_te TEXT NOT NULL,
        question_en TEXT NOT NULL,
        options_te TEXT NOT NULL,  -- JSON list of options
        options_en TEXT NOT NULL,
        correct_index INTEGER NOT NULL,
        explanation_te TEXT NOT NULL,
        explanation_en TEXT NOT NULL
    )
    """)

    # Quiz Attempts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        topic_id TEXT NOT NULL,
        score INTEGER NOT NULL,
        total INTEGER NOT NULL,
        percentage REAL NOT NULL
    )
    """)

    # Learning Progress / History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        question TEXT NOT NULL,
        topic TEXT,
        language TEXT NOT NULL,
        source TEXT NOT NULL,
        latency REAL
    )
    """)

    conn.commit()

    # Seed Class 8 Science quiz questions if empty
    cursor.execute("SELECT COUNT(*) as count FROM quiz_questions")
    if cursor.fetchone()["count"] == 0:
        seed_quiz_questions(cursor)
        conn.commit()

    conn.close()


def seed_quiz_questions(cursor):
    sample_questions = [
        # Photosynthesis Questions
        (
            "q_photo_01",
            "science_001",
            "Photosynthesis",
            "మొక్కలలో కిరణజన్య సంయోగక్రియ ప్రధానంగా ఎక్కడ జరుగుతుంది?",
            "Where does photosynthesis primarily take place in plants?",
            json.dumps(["ఆకులు (Leaves)", "వేర్లు (Roots)", "కాండం (Stem)", "పువ్వులు (Flowers)"], ensure_ascii=False),
            json.dumps(["Leaves", "Roots", "Stem", "Flowers"]),
            0,
            "ఆకులలో ఉండే క్లోరోఫిల్ సూర్యరశ్మిని గ్రహించి ఆహారాన్ని తయారుచేస్తుంది.",
            "Chlorophyll present in leaves captures sunlight to prepare food."
        ),
        (
            "q_photo_02",
            "science_001",
            "Photosynthesis",
            "కిరణజన్య సంయోగక్రియ సమయంలో మొక్కలు ఏ వాయువును విడుదల చేస్తాయి?",
            "Which gas is released by plants during photosynthesis?",
            json.dumps(["కార్బన్ డయాక్సైడ్ (Carbon Dioxide)", "ఆక్సిజన్ (Oxygen)", "నైట్రోజన్ (Nitrogen)", "హైడ్రోజన్ (Hydrogen)"], ensure_ascii=False),
            json.dumps(["Carbon Dioxide", "Oxygen", "Nitrogen", "Hydrogen"]),
            1,
            "మొక్కలు కార్బన్ డయాక్సైడ్‌ను పీల్చుకుని మనకు అవసరమైన ప్రాణవాయువు అయిన ఆక్సిజన్‌ను విడుదల చేస్తాయి.",
            "Plants absorb carbon dioxide and release oxygen, which is essential for living beings."
        ),
        # Force and Motion Questions
        (
            "q_force_01",
            "science_002",
            "Force and Motion",
            "ఒక వస్తువును తోయడం లేదా లాగడాన్ని ఏమంటారు?",
            "A push or pull on an object is known as what?",
            json.dumps(["బలం (Force)", "ఘర్షణ (Friction)", "వేగం (Speed)", "పీడనం (Pressure)"], ensure_ascii=False),
            json.dumps(["Force", "Friction", "Speed", "Pressure"]),
            0,
            "ఒక వస్తువుపై జరిగే తోపుడు లేదా లాగుడు చర్యనే బలం అంటారు.",
            "A push or pull acting upon an object is defined as force."
        ),
        (
            "q_force_02",
            "science_002",
            "Force and Motion",
            "బలం ప్రయోగించినప్పుడు వస్తువులో ఏ మార్పు రావచ్చు?",
            "What change can occur when a force is applied to an object?",
            json.dumps(["వేగం మారవచ్చు (Speed can change)", "దిశ మారవచ్చు (Direction can change)", "ఆకారం మారవచ్చు (Shape can change)", "పైవన్నీ (All of the above)"], ensure_ascii=False),
            json.dumps(["Speed can change", "Direction can change", "Shape can change", "All of the above"]),
            3,
            "బలం వల్ల వస్తువు వేగం, కదిలే దిశ మరియు ఆకారం అన్నీ మారవచ్చు.",
            "Force can alter the speed, direction of motion, and shape of an object."
        ),
        # Friction Questions
        (
            "q_frict_01",
            "science_003",
            "Friction",
            "మనం నేలపై జారిపడకుండా సులభంగా నడవడానికి ఏ బలం సహాయపడుతుంది?",
            "Which force helps us walk on the ground without slipping?",
            json.dumps(["గురుత్వాకర్షణ బలం (Gravitational Force)", "ఘర్షణ బలం (Frictional Force)", "అయస్కాంత బలం (Magnetic Force)", "స్థిర విద్యుత్ బలం (Electrostatic Force)"], ensure_ascii=False),
            json.dumps(["Gravitational Force", "Frictional Force", "Magnetic Force", "Electrostatic Force"]),
            1,
            "మన పాదాలకు మరియు నేలకు మధ్య ఏర్పడే ఘర్షణ బలం వల్ల మనం జారకుండా నడవగలుగుతాము.",
            "Friction between our footwear and the floor prevents slipping while walking."
        ),
        (
            "q_frict_02",
            "science_003",
            "Friction",
            "రెండు ఉపరితలాల మధ్య గరుకుతనం (roughness) పెరిగితే ఘర్షణ ఏమవుతుంది?",
            "If the roughness between two surfaces increases, what happens to friction?",
            json.dumps(["ఘర్షణ పెరుగుతుంది (Friction increases)", "ఘర్షణ తగ్గుతుంది (Friction decreases)", "ఎలాంటి మార్పు ఉండదు (No change)", "సున్నా అవుతుంది (Becomes zero)"], ensure_ascii=False),
            json.dumps(["Friction increases", "Friction decreases", "No change", "Becomes zero"]),
            0,
            "ఉపరితలం ఎక్కువ గరుకుగా ఉంటే ఘర్షణ బలం కూడా పెరుగుతుంది.",
            "Rougher surfaces create greater resistance, increasing friction."
        )
    ]

    cursor.executemany("""
    INSERT INTO quiz_questions (
        id, topic_id, topic_name, question_te, question_en,
        options_te, options_en, correct_index, explanation_te, explanation_en
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_questions)


def get_quiz_by_topic(topic_id: str, language: str = "te") -> List[Dict[str, Any]]:
    """Fetches quiz questions for a topic. If not in DB, dynamically generates them via Gemini."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, topic_id, topic_name, question_te, question_en,
           options_te, options_en, explanation_te, explanation_en
    FROM quiz_questions
    WHERE topic_id = ? OR LOWER(topic_name) = LOWER(?) OR LOWER(topic_name) LIKE LOWER(?)
    """, (topic_id, topic_id, f"%{topic_id}%"))

    rows = cursor.fetchall()
    conn.close()

    # If no questions exist for this topic, dynamically generate with Gemini and persist!
    if not rows:
        return generate_dynamic_quiz_questions(topic_id, language=language)

    questions = []
    is_te = language.lower().startswith("te")
    for r in rows:
        options = json.loads(r["options_te"] if is_te else r["options_en"])
        questions.append({
            "id": r["id"],
            "topic_id": r["topic_id"],
            "topic_name": r["topic_name"],
            "question": r["question_te"] if is_te else r["question_en"],
            "options": options
        })
    return questions


def generate_dynamic_quiz_questions(topic_name: str, language: str = "te") -> List[Dict[str, Any]]:
    """Uses Google Gemini to generate 2 Class 8 Science MCQs in real-time and persists them in SQLite."""
    import os
    import httpx
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")
    if not api_key:
        return []

    prompt = f"""
You are a Class 8 Science teacher.
Generate 2 multiple-choice questions with 4 options each for Class 8 Science topic: '{topic_name}'.
Return STRICTLY a JSON list of 2 objects with this schema:
[
  {{
    "id": "q_{abs(hash(topic_name)) % 10000}_1",
    "question_te": "తెలుగులో స్పష్టమైన ప్రశ్న",
    "question_en": "Question in English",
    "options_te": ["ఆప్షన్ 1", "ఆప్షన్ 2", "ఆప్షన్ 3", "ఆప్షన్ 4"],
    "options_en": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "correct_index": 0,
    "explanation_te": "తెలుగులో సరైన వివరణ",
    "explanation_en": "Clear explanation in English"
  }}
]
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json", "temperature": 0.2}
    }

    try:
        res = httpx.post(url, json=payload, timeout=20.0)
        if res.status_code == 200:
            data = res.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            q_list = json.loads(raw_text)

            conn = get_db()
            cursor = conn.cursor()
            saved_questions = []

            for idx, q in enumerate(q_list):
                qid = f"dyn_{abs(hash(topic_name)) % 10000}_{idx}"
                cursor.execute("""
                INSERT OR REPLACE INTO quiz_questions (
                    id, topic_id, topic_name, question_te, question_en,
                    options_te, options_en, correct_index, explanation_te, explanation_en
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    qid,
                    topic_name,
                    topic_name,
                    q["question_te"],
                    q["question_en"],
                    json.dumps(q["options_te"], ensure_ascii=False),
                    json.dumps(q["options_en"]),
                    q["correct_index"],
                    q["explanation_te"],
                    q["explanation_en"]
                ))
                is_te = language.lower().startswith("te")
                saved_questions.append({
                    "id": qid,
                    "topic_id": topic_name,
                    "topic_name": topic_name,
                    "question": q["question_te"] if is_te else q["question_en"],
                    "options": q["options_te"] if is_te else q["options_en"]
                })
            conn.commit()
            conn.close()
            return saved_questions
    except Exception as e:
        pass

    return []


def submit_quiz_answers(topic_id: str, answers: Dict[str, int], language: str = "te") -> Dict[str, Any]:
    """Scores student answers and saves attempt in SQLite."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, correct_index, explanation_te, explanation_en, options_te, options_en
    FROM quiz_questions
    WHERE topic_id = ? OR LOWER(topic_name) = LOWER(?) OR LOWER(topic_name) LIKE LOWER(?)
    """, (topic_id, topic_id, f"%{topic_id}%"))

    rows = cursor.fetchall()
    is_te = language.lower().startswith("te")

    total = len(rows)
    score = 0
    feedback = []

    for r in rows:
        q_id = r["id"]
        correct_idx = r["correct_index"]
        student_choice = answers.get(q_id)
        is_correct = (student_choice == correct_idx)

        if is_correct:
            score += 1

        options = json.loads(r["options_te"] if is_te else r["options_en"])
        feedback.append({
            "question_id": q_id,
            "student_choice": student_choice,
            "correct_choice": correct_idx,
            "correct_option_text": options[correct_idx] if 0 <= correct_idx < len(options) else "",
            "is_correct": is_correct,
            "explanation": r["explanation_te"] if is_te else r["explanation_en"]
        })

    percentage = round((score / total * 100), 1) if total > 0 else 0.0

    # Save attempt
    cursor.execute("""
    INSERT INTO quiz_attempts (timestamp, topic_id, score, total, percentage)
    VALUES (?, ?, ?, ?, ?)
    """, (time.time(), topic_id, score, total, percentage))
    conn.commit()
    conn.close()

    encouragement = (
        "అద్భుతం! మీరు చాలా బాగా అర్థం చేసుకున్నారు!"
        if percentage >= 80 else
        "మంచి ప్రయత్నం! వివరణలు చదివి మరోసారి ప్రయత్నించండి."
        if percentage >= 50 else
        "పర్వాలేదు! పాఠం మళ్లీ విని నేర్చుకోండి, తప్పక మెరుగవుతారు."
    ) if is_te else (
        "Excellent! You understand this concept very well!"
        if percentage >= 80 else
        "Good effort! Review the explanations and try again."
        if percentage >= 50 else
        "Keep going! Listen to the explanation again to improve."
    )

    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "encouragement": encouragement,
        "feedback": feedback
    }


def record_interaction(question: str, topic: Optional[str], language: str, source: str, latency: float):
    """Logs student learning interactions for basic progress reporting."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO learning_history (timestamp, question, topic, language, source, latency)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (time.time(), question, topic, language, source, latency))
        conn.commit()
        conn.close()
    except Exception:
        pass


def get_progress_summary() -> Dict[str, Any]:
    """Returns overall quiz and practice summary."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total_attempts, AVG(percentage) as avg_score FROM quiz_attempts")
    attempt_row = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) as total_questions_asked FROM learning_history")
    history_row = cursor.fetchone()

    conn.close()

    return {
        "total_quizzes_taken": attempt_row["total_attempts"] or 0,
        "average_quiz_score": round(attempt_row["avg_score"] or 0.0, 1),
        "total_questions_asked": history_row["total_questions_asked"] or 0
    }


def register_user(name: str, student_class: str, email: str, password: str) -> Dict[str, Any]:
    """Registers a new student user."""
    name = name.strip()
    email = email.strip().lower()
    student_class = student_class.strip()

    if not name:
        return {"success": False, "message": "దయచేసి మీ పేరు నమోదు చేయండి (Name is required)."}
    if not email or "@" not in email:
        return {"success": False, "message": "సరైన ఈమెయిల్ చిరునామా నమోదు చేయండి (Valid email is required)."}
    if len(password) < 6:
        return {"success": False, "message": "పాస్‌వర్డ్ కనీసం 6 అక్షరాలు ఉండాలి (Password must be at least 6 characters)."}

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "message": "ఈ ఈమెయిల్‌తో ఖాతా ఇప్పటికే ఉంది (Email already registered)."}

    pw_hash = hash_password(password)
    now = time.time()
    cursor.execute("""
    INSERT INTO users (name, student_class, email, password_hash, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (name, student_class, email, pw_hash, now))

    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "నమోదు విజయవంతమైంది! (Registration successful!)",
        "user": {
            "id": user_id,
            "name": name,
            "student_class": student_class,
            "email": email
        }
    }


def login_user(email: str, password: str) -> Dict[str, Any]:
    """Authenticates a student user by email and password."""
    email = email.strip().lower()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, student_class, email, password_hash FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"success": False, "message": "ఈ ఈమెయిల్‌తో ఖాతా కనుగొనబడలేదు (User not found)."}

    pw_hash = hash_password(password)
    if row["password_hash"] != pw_hash:
        return {"success": False, "message": "తప్పుడు పాస్‌వర్డ్ (Incorrect password)."}

    return {
        "success": True,
        "message": "లాగిన్ విజయవంతమైంది! (Login successful!)",
        "user": {
            "id": row["id"],
            "name": row["name"],
            "student_class": row["student_class"],
            "email": row["email"]
        }
    }


