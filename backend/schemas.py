from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date


# ─── Auth Schemas ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = "moderate"
    dietary_preference: Optional[str] = "Vegetarian"
    fitness_goal: Optional[str] = "maintain"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    dietary_preference: Optional[str] = None
    fitness_goal: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    age: Optional[int]
    weight_kg: Optional[float]
    height_cm: Optional[float]
    gender: Optional[str]
    activity_level: Optional[str]
    dietary_preference: Optional[str]
    fitness_goal: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str


# ─── AI Targets Schemas ────────────────────────────────────────────────────────

class AITargetsResponse(BaseModel):
    id: int
    user_id: int
    bmr: Optional[float]
    tdee: Optional[float]
    target_calories: Optional[float]
    target_protein_g: Optional[float]
    target_carbs_g: Optional[float]
    target_fat_g: Optional[float]
    target_water_ml: Optional[float]
    explanation: Optional[str]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class GoalSetRequest(BaseModel):
    goal_description: Optional[str] = None  # free text from user


# ─── Daily Log Schemas ─────────────────────────────────────────────────────────

class DailyLogResponse(BaseModel):
    id: int
    user_id: int
    log_date: date
    total_calories_consumed: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    water_ml: float
    notes: Optional[str]

    class Config:
        from_attributes = True


class WaterUpdate(BaseModel):
    water_ml: float


# ─── Workout Log Schemas ───────────────────────────────────────────────────────

class WorkoutLogCreate(BaseModel):
    exercise_name: str
    workout_type: str  # Cardio / Strength / Yoga / HIIT / Sports
    duration_minutes: int
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    calories_burned: Optional[float] = None
    notes: Optional[str] = None
    workout_date: Optional[datetime] = None


class WorkoutLogUpdate(BaseModel):
    exercise_name: Optional[str] = None
    workout_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    calories_burned: Optional[float] = None
    notes: Optional[str] = None


class WorkoutLogResponse(BaseModel):
    id: int
    user_id: int
    exercise_name: str
    workout_type: str
    duration_minutes: int
    sets: Optional[int]
    reps: Optional[int]
    weight_kg: Optional[float]
    calories_burned: Optional[float]
    notes: Optional[str]
    workout_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Meal Log Schemas ──────────────────────────────────────────────────────────

class MealLogCreate(BaseModel):
    meal_category: str  # Breakfast / Lunch / Dinner / Snack
    food_item_name: str
    serving_size: float
    serving_unit: str = "g"
    calories: float
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    notes: Optional[str] = None
    meal_date: Optional[datetime] = None


class MealLogUpdate(BaseModel):
    meal_category: Optional[str] = None
    food_item_name: Optional[str] = None
    serving_size: Optional[float] = None
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    notes: Optional[str] = None


class MealLogResponse(BaseModel):
    id: int
    user_id: int
    meal_category: str
    food_item_name: str
    serving_size: float
    serving_unit: str
    calories: float
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    fiber_g: Optional[float]
    notes: Optional[str]
    meal_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Indian Food Schemas ───────────────────────────────────────────────────────

class IndianFoodItemResponse(BaseModel):
    id: int
    food_name: str
    serving_unit: str
    serving_size_g: Optional[float]
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: Optional[float]
    tags: Optional[str]
    description: Optional[str]
    is_vegetarian: bool

    class Config:
        from_attributes = True


# ─── AI Chat Schemas ───────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    retrieved_foods: Optional[List[str]] = []


# ─── Dashboard Schemas ─────────────────────────────────────────────────────────

class DashboardSummary(BaseModel):
    today_calories: float
    today_protein: float
    today_carbs: float
    today_fat: float
    today_water_ml: float
    target_calories: Optional[float]
    target_protein: Optional[float]
    target_water_ml: Optional[float]
    today_calories_burned: float
    today_workouts: int
    bmi: Optional[float]
    latest_weight: Optional[float]
