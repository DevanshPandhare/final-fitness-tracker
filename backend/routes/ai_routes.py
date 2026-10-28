"""
AI Health Coach routes — Gemini + RAG pipeline for:
1. Goal Setting: Calculate BMR, TDEE, and personalized calorie/macro targets.
2. RAG Chat: Retrieve Indian food items from ChromaDB, inject into Gemini context.
"""
import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, User, AITargets, IndianFoodItem
from schemas import AITargetsResponse, GoalSetRequest, ChatMessage, ChatResponse
from auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Health Coach"])

# REMOVE the global GEMINI_API_KEY variable from here

def _get_gemini_client():
    """Initialize Gemini client."""
    # Fetch the key HERE, after load_dotenv() has run in main.py
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY not configured. Set it as an environment variable.",
        )
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        # Use a valid model name
        return genai.GenerativeModel("gemini-3.6-flash")
    except ImportError:
        raise HTTPException(status_code=503, detail="google-generativeai package not installed.")

# ... keep _get_chroma_collection and the rest of ai_routes.py exactly the same


def _get_chroma_collection():
    """Get ChromaDB collection for Indian foods."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path="./chroma_db")
        return client.get_collection("indian_foods")
    except Exception:
        return None


def _sql_food_search(query: str, db: Session, n: int = 5):
    """Fallback SQL search when ChromaDB is unavailable."""
    terms = query.lower().split()
    results = []
    foods = db.query(IndianFoodItem).all()
    for food in foods:
        score = sum(
            1 for term in terms
            if term in (food.food_name or "").lower()
            or term in (food.tags or "").lower()
            or term in (food.description or "").lower()
        )
        if score > 0:
            results.append((score, food))
    results.sort(key=lambda x: x[0], reverse=True)
    return [f for _, f in results[:n]]


@router.post("/set-goals", response_model=AITargetsResponse)
def set_goals(
    data: GoalSetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Use Gemini to calculate personalized BMR, TDEE, and daily macro targets
    based on the user's stats and fitness goal.
    """
    user = current_user

    # Build user profile context
    profile = {
        "name": user.full_name or user.username,
        "age": user.age or "unknown",
        "weight_kg": user.weight_kg or "unknown",
        "height_cm": user.height_cm or "unknown",
        "gender": user.gender or "unknown",
        "activity_level": user.activity_level or "moderate",
        "dietary_preference": user.dietary_preference or "Vegetarian",
        "fitness_goal": user.fitness_goal or "maintain",
        "custom_goal_text": data.goal_description or "",
    }

    prompt = f"""
You are a certified sports nutritionist and fitness coach. 
Calculate the precise nutritional targets for this user and respond ONLY with valid JSON.

User Profile:
- Name: {profile['name']}
- Age: {profile['age']} years
- Weight: {profile['weight_kg']} kg
- Height: {profile['height_cm']} cm
- Gender: {profile['gender']}
- Activity Level: {profile['activity_level']} (sedentary/light/moderate/active/very_active)
- Dietary Preference: {profile['dietary_preference']}
- Fitness Goal: {profile['fitness_goal']} (lose_fat/build_muscle/maintain/endurance)
- Custom Goal: {profile['custom_goal_text']}

Calculate and return ONLY this JSON object (no markdown, no explanation text):
{{
  "bmr": <number>,
  "tdee": <number>,
  "target_calories": <number>,
  "target_protein_g": <number>,
  "target_carbs_g": <number>,
  "target_fat_g": <number>,
  "target_water_ml": <number>,
  "explanation": "<2-3 sentence explanation of the plan in plain English>"
}}

Use Mifflin-St Jeor formula for BMR. Apply correct TDEE multiplier. 
Adjust calories for goal (deficit for fat loss, surplus for muscle gain).
Protein: 1.6-2.2g/kg for muscle, 1.2g/kg for maintenance, 1.4g/kg for fat loss.
Water: 35ml per kg body weight.
"""

    model = _get_gemini_client()
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        targets_data = json.loads(raw.strip())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini response parsing failed: {str(e)}",
        )

    # Save to database
    existing = db.query(AITargets).filter(AITargets.user_id == user.id).first()
    if existing:
        for k, v in targets_data.items():
            if hasattr(existing, k):
                setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        ai_targets = AITargets(
            user_id=user.id,
            bmr=targets_data.get("bmr"),
            tdee=targets_data.get("tdee"),
            target_calories=targets_data.get("target_calories"),
            target_protein_g=targets_data.get("target_protein_g"),
            target_carbs_g=targets_data.get("target_carbs_g"),
            target_fat_g=targets_data.get("target_fat_g"),
            target_water_ml=targets_data.get("target_water_ml"),
            explanation=targets_data.get("explanation"),
        )
        db.add(ai_targets)
        db.commit()
        db.refresh(ai_targets)
        return ai_targets


@router.get("/targets", response_model=AITargetsResponse)
def get_targets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the user's current AI-generated targets."""
    targets = db.query(AITargets).filter(AITargets.user_id == current_user.id).first()
    if not targets:
        raise HTTPException(
            status_code=404,
            detail="No AI targets set yet. Please use /ai/set-goals first.",
        )
    return targets


@router.post("/chat", response_model=ChatResponse)
def ai_chat(
    data: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    RAG-powered AI Health Coach chat.
    1. Query ChromaDB (or SQL fallback) for relevant Indian foods.
    2. Inject retrieved food data into Gemini context.
    3. Return grounded, hallucination-free nutrition advice.
    """
    user_message = data.message
    retrieved_food_names = []
    food_context = ""

    # --- RAG: Retrieve relevant foods ---
    collection = _get_chroma_collection()
    if collection:
        try:
            results = collection.query(query_texts=[user_message], n_results=5)
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            food_context = "\n".join(docs)
            retrieved_food_names = [m.get("food_name", "") for m in metas]
        except Exception:
            collection = None  # fall through to SQL

    if not collection:
        # SQL fallback
        foods = _sql_food_search(user_message, db, n=5)
        if foods:
            food_lines = []
            for f in foods:
                food_lines.append(
                    f"- {f.food_name} ({f.serving_unit}): {f.calories} kcal, "
                    f"Protein {f.protein_g}g, Carbs {f.carbs_g}g, Fat {f.fat_g}g. "
                    f"Tags: {f.tags}. {f.description}"
                )
            food_context = "\n".join(food_lines)
            retrieved_food_names = [f.food_name for f in foods]

    # Build user context
    ai_targets = current_user.ai_targets
    targets_text = ""
    if ai_targets:
        targets_text = (
            f"User's daily targets: {ai_targets.target_calories} kcal, "
            f"{ai_targets.target_protein_g}g protein, "
            f"{ai_targets.target_carbs_g}g carbs, {ai_targets.target_fat_g}g fat."
        )

    system_prompt = f"""You are NutriPulse AI — an expert Indian nutrition and fitness coach.
You ONLY give advice based on factual nutritional data provided to you. Do NOT hallucinate calorie values.

User Profile:
- Dietary Preference: {current_user.dietary_preference or "Vegetarian"}
- Fitness Goal: {current_user.fitness_goal or "maintain"}
- {targets_text}

Relevant Indian Food Database (use THESE values — do not invent others):
{food_context if food_context else "No specific foods retrieved for this query."}

User's Question: {user_message}

Provide a helpful, specific, friendly response. 
If recommending meals, cite exact calorie and protein values from the database above.
Keep response concise but actionable (2-4 short paragraphs max).
"""

    model = _get_gemini_client()
    try:
        response = model.generate_content(system_prompt)
        reply = response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

    return ChatResponse(reply=reply, retrieved_foods=retrieved_food_names)
