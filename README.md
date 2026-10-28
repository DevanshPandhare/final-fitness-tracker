# 🏃 NutriPulse AI — Intelligent Indian Fitness & Nutrition Tracker

A full-stack AI-powered fitness and nutrition tracking application built with **FastAPI**, **SQLAlchemy**, **ChromaDB**, **Google Gemini AI**, and **TypeScript/Vite**.

---

## 🌟 Features

| Feature | Description |
|---|---|
| 🔐 **Auth** | JWT-based registration & login |
| 💪 **Workout Tracker** | Log exercises with auto calorie calculation |
| 🥗 **Nutrition Tracker** | Track Indian meals with full macro breakdown |
| 🤖 **AI Coach (Gemini)** | Personalized BMR/TDEE/macro goal setting |
| 🔍 **RAG Chat** | ChromaDB vector search + Gemini for grounded nutrition advice |
| 📊 **Dashboard** | Live stats, weekly charts, BMI, water tracker |
| 🇮🇳 **Indian Food DB** | 30+ Indian foods pre-seeded with nutritional data |

---

## 🏗️ Tech Stack

### Backend
- **FastAPI** — High-performance REST API
- **SQLAlchemy** — ORM with SQLite database
- **ChromaDB** — Vector database for RAG (Retrieval-Augmented Generation)
- **Google Gemini AI** — Personalized nutrition goal calculation + chat
- **python-jose** — JWT authentication
- **bcrypt** — Secure password hashing
- **sentence-transformers** — Semantic embeddings for food search

### Frontend
- **TypeScript** — Type-safe JavaScript
- **Vite** — Lightning-fast build tool
- **Vanilla CSS** — Custom dark theme with glassmorphism effects
- **Google Fonts (Inter)** — Modern typography

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js 18+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

---

### 1. Clone the Repository
```bash
git clone <repo-url>
cd "final fitness tracker"
```

---

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set your Gemini API key (required for AI features)
# Windows PowerShell:
$env:GEMINI_API_KEY = "your_api_key_here"

# Windows CMD:
set GEMINI_API_KEY=your_api_key_here

# Start the backend server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will:
1. Create SQLite database (`nutripulse.db`)
2. Auto-seed 30+ Indian food items
3. Build ChromaDB vector index for RAG search
4. Start API at `http://localhost:8000`

📚 **API Docs:** http://localhost:8000/docs

---

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install Node dependencies (already done if node_modules exists)
npm install

# Start the development server
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## 📱 Application Pages

### 🏠 Dashboard
- Daily calorie balance (consumed vs burned)
- Protein, carb, fat progress bars
- 7-day trend chart
- Macro pie chart
- Water intake tracker with quick-add buttons
- BMI display

### 💪 Workout Log
- Log workouts by type (Cardio, Strength, Yoga, HIIT, Sports)
- Auto-calculate calories burned based on duration & body weight
- View all past workouts with delete option

### 🥗 Nutrition Tracker
- Search Indian food database (paneer, dal, roti, etc.)
- Auto-fill nutritional values from database
- Group meals by Breakfast, Lunch, Dinner, Snack
- Daily macro summary

### 🤖 AI Coach
- **Goal Setting:** Enter your profile → Gemini calculates personalized BMR, TDEE, calorie & macro targets
- **RAG Chat:** Ask questions → ChromaDB retrieves relevant Indian foods → Gemini gives grounded advice

### 👤 Profile
- Edit personal details (weight, height, age, gender)
- Change fitness goal and dietary preference
- Recalculate AI targets

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes* | Google Gemini API key for AI features |

> *Without the API key, all features except AI Coach work fine. The AI Coach will return a 503 error.

---

## 📂 Project Structure

```
final fitness tracker/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy models
│   ├── auth.py              # JWT + bcrypt authentication
│   ├── schemas.py           # Pydantic schemas
│   ├── seed_data.py         # Indian food database + ChromaDB indexer
│   ├── requirements.txt     # Python dependencies
│   └── routes/
│       ├── auth_routes.py   # Register, login, profile
│       ├── workout_routes.py # CRUD for workouts
│       ├── meal_routes.py   # CRUD for meals + food search
│       ├── dashboard_routes.py # Analytics + water tracking
│       └── ai_routes.py     # Gemini goal-setting + RAG chat
└── frontend/
    ├── index.html           # Entry HTML
    ├── package.json         # Node config
    └── src/
        ├── main.ts          # Full SPA (TypeScript)
        └── index.css        # Design system (dark theme)
```

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/auth/me` | Get profile |
| PUT | `/api/v1/auth/me` | Update profile |
| POST | `/api/v1/workouts/` | Log workout |
| GET | `/api/v1/workouts/` | Get all workouts |
| DELETE | `/api/v1/workouts/{id}` | Delete workout |
| POST | `/api/v1/meals/` | Log meal |
| GET | `/api/v1/meals/today` | Today's meals grouped by category |
| GET | `/api/v1/meals/search-food` | Search Indian food DB |
| GET | `/api/v1/dashboard/summary` | Daily stats summary |
| GET | `/api/v1/dashboard/weekly-chart` | 7-day trend data |
| PATCH | `/api/v1/dashboard/water` | Log water intake |
| POST | `/api/v1/ai/set-goals` | Gemini goal calculation |
| GET | `/api/v1/ai/targets` | Get AI targets |
| POST | `/api/v1/ai/chat` | RAG-powered nutrition chat |

---

## 🎨 Design System

- **Dark theme** with `#09090b` base
- **Emerald** (#10b981) — Health metrics
- **Violet** (#8b5cf6) — AI features  
- **Amber** (#f59e0b) — Calories/warnings
- **Sky** (#38bdf8) — Hydration
- **Rose** (#f43f5e) — Alerts/delete
- Glassmorphism cards, smooth animations, micro-interactions

---

## 🤖 AI Architecture

```
User Query
    │
    ▼
ChromaDB Vector Search (cosine similarity)
    │
    ├── Found relevant foods → inject into Gemini context
    └── Not found → SQL LIKE search fallback
         │
         ▼
    Gemini 1.5 Flash
         │
         ▼
    Grounded Response (with actual calorie values)
```

---

## 📝 Notes

- The SQLite database is created at `backend/nutripulse.db` on first run
- ChromaDB index is stored at `backend/chroma_db/`
- All API endpoints require JWT Bearer token (except `/auth/register` and `/auth/login`)
- AI features require a valid `GEMINI_API_KEY` environment variable

---

*Built with ❤️ using FastAPI + Gemini AI + TypeScript*
