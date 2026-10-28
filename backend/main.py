from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables from the .env file BEFORE importing routes
load_dotenv()

from database import create_tables
from seed_data import seed_indian_foods, build_chroma_index
from routes.auth_routes import router as auth_router
# ... keep the rest of main.py exactly the same
from routes.workout_routes import router as workout_router
from routes.meal_routes import router as meal_router
from routes.dashboard_routes import router as dashboard_router
from routes.ai_routes import router as ai_router

app = FastAPI(
    title="🥗 NutriPulse AI API",
    description="""
## NutriPulse AI — Intelligent Indian Fitness & Nutrition Tracking

A production-grade REST API powering the NutriPulse AI health platform:

- 🔐 **Authentication** — JWT-based secure login & registration
- 💪 **Workout Logs** — Log exercises with auto calorie calculation
- 🥗 **Meal Logs** — Indian nutrition tracking with automatic macro summation
- 🤖 **AI Health Coach** — Gemini-powered goal setting + RAG chat
- 📊 **Dashboard** — Real-time analytics and weekly trend charts

Built with FastAPI + SQLAlchemy + ChromaDB + Google Gemini
    """,
    version="2.0.0",
    contact={"name": "NutriPulse AI", "email": "support@nutripulse.ai"},
)

# CORS — allow frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database tables and seed Indian food data on startup."""
    create_tables()
    seed_indian_foods()
    build_chroma_index()


# Register all routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(workout_router, prefix="/api/v1")
app.include_router(meal_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "message": "NutriPulse AI API is running 🚀"}


@app.get("/", tags=["Root"])
def root():
    return {
        "name": "NutriPulse AI",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "running",
    }
