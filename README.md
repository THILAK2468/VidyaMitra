# VidyaMitra | విద్యామిత్ర

**Learn in your language. Understand in your way.**  
*మీ భాషలో నేర్చుకోండి. మీ శైలిలో అర్థం చేసుకోండి.*

VidyaMitra is a Telugu-first multilingual AI learning companion for Class 8 Science. Built for the Gnani AI Challenge, it enables students to ask questions by voice or text in Telugu or English, receive curriculum-grounded explanations, listen to spoken audio answers, and test their understanding with interactive quizzes.

---

## ✨ Features Implemented
- 🔐 **First-Screen Authentication**: Beautiful welcome landing screen with interactive Student Login & Registration (Name, Class 6-10 dropdown, Email, Password & Confirm Password with Show/Hide eye buttons) and 1-click Guest access.
- 🎙️ **Voice & Speech-to-Text**: Ask questions by voice in Telugu (`te-IN`) or English using **Gnani Prisma STT** (`prisma-v2.5`), with the transcribed text immediately displayed in a live website banner and input box.
- 🤖 **Curriculum-Grounded AI Tutor**: Explanations powered by **Google Gemini Flash**, strictly grounded in Class 8 Science with dynamic coverage for any science topic.
- 🔊 **Text-to-Speech (TTS)**: Spoken audio answers generated via **Gnani Timbre TTS** (`timbre-v2.5`, voice: `Suhana`).
- 💬 **Follow-Up Questions**: Supports conversation context and previous topic memory for natural learning dialogues.
- 🎯 **Interactive Quizzes**: Multiple-choice assessment for science lessons with instant Telugu explanations and on-the-fly dynamic quiz generation.
- 📊 **Progress & Persistence**: SQLite database (`vidyamitra.db`) tracks student accounts, learning interactions, and quiz scores.
- ☁️ **Render Cloud Deployment**: Production-ready deployment configuration (`render.yaml`, `.python-version`, automated free HTTPS).
- 🖥️ **Responsive Web UI**: Built with HTML5, CSS3 (`Noto Sans Telugu` & `Inter`), and Vanilla JavaScript; served directly by FastAPI.

---

## 🛠️ Tech Stack
- **Backend**: Python 3.11, FastAPI, Uvicorn, HTTPX, Pydantic, python-dotenv
- **Speech Services**: Gnani Prisma (STT) & Gnani Timbre (TTS)
- **Language Model**: Google Gemini (`gemini-3.5-flash-lite`) via Google AI Studio
- **Database**: SQLite 3
- **Frontend**: HTML5, CSS3, JavaScript (Web Audio / `MediaRecorder` API)

---

## 🚀 Quickstart (Windows PowerShell)

### 1. Activate Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Configure Credentials (`.env`)
Ensure `.env` contains your API credentials:
```env
GNANI_API_KEY="your_gnani_api_key"
GNANI_STT_URL=https://api.vachana.ai/stt/v3
GNANI_TTS_URL=https://api.vachana.ai/api/v1/tts/inference
GNANI_TTS_MODEL=timbre-v2.5
GNANI_TTS_VOICE=Suhana
GNANI_TTS_LANGUAGE=te-IN

GEMINI_API_KEY=your_gemini_api_key
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.5-flash-lite
```

### 3. Launch the Application
```powershell
python -m uvicorn app.main:app --reload
```

### 4. Open in Browser
- **Student Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Run Automated Verification Tests
```powershell
python tests/test_voice_and_tutor.py
```
Verifies health endpoints, curriculum retrieval, Gnani STT, full voice vertical slice, Gemini AI grounding, Gnani TTS playback, interactive quizzes, and follow-up question context.

---

## 📁 Project Architecture
```text
VidyaMitra/
├── app/
│   ├── main.py              # Application entry point & router mounting
│   ├── routes/
│   │   ├── auth.py          # Student login & registration endpoints
│   │   ├── tutor.py         # Text tutor & topic routes
│   │   ├── voice.py         # STT, TTS, and /voice/ask vertical slice
│   │   └── quiz.py          # Interactive quiz & scoring routes
│   ├── services/
│   │   ├── curriculum.py    # Curriculum loader with whitespace-normalized matching
│   │   ├── gnani_stt.py     # Gnani Prisma STT integration with audio validation
│   │   ├── gnani_tts.py     # Gnani Timbre TTS speech synthesis wrapper
│   │   ├── tutor_engine.py  # Grounded Gemini tutor prompt engine
│   │   └── database.py      # SQLite models, user auth, quiz seeds & progress
│   ├── data/
│   │   └── class8_science.json  # Curated Class 8 Science lesson notes
│   └── static/
│       ├── index.html       # Responsive student interface with Auth & Live STT banner
│       ├── style.css        # Design system & Telugu typography styling
│       ├── app.js           # Client voice recording, STT display & auth controller
│       └── audio/           # Generated speech audio files
├── tests/
│   └── test_voice_and_tutor.py  # Full integration test suite
├── render.yaml              # Render.com Blueprint configuration
├── .python-version          # Python 3.11 runtime lock
├── vidyamitra.db            # SQLite persistence
├── requirements.txt         # Project dependencies
└── README.md
```
