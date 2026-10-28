from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, ForeignKey, Text, Boolean, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date

SQLALCHEMY_DATABASE_URL = "sqlite:///./nutripulse.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── User ────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    gender = Column(String, nullable=True)  # male / female / other
    activity_level = Column(String, nullable=True)  # sedentary/light/moderate/active/very_active
    dietary_preference = Column(String, nullable=True)  # Vegetarian / Non-Veg / High-Protein / Vegan
    fitness_goal = Column(String, nullable=True)  # lose_fat / build_muscle / maintain / endurance
    created_at = Column(DateTime, default=datetime.utcnow)

    workout_logs = relationship("WorkoutLog", back_populates="user", cascade="all, delete-orphan")
    meal_logs = relationship("MealLog", back_populates="user", cascade="all, delete-orphan")
    daily_logs = relationship("DailyLog", back_populates="user", cascade="all, delete-orphan")
    ai_targets = relationship("AITargets", back_populates="user", uselist=False, cascade="all, delete-orphan")


# ── AI Targets (Gemini-generated) ───────────────────────────────────────────────
class AITargets(Base):
    __tablename__ = "ai_targets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    bmr = Column(Float, nullable=True)
    tdee = Column(Float, nullable=True)
    target_calories = Column(Float, nullable=True)
    target_protein_g = Column(Float, nullable=True)
    target_carbs_g = Column(Float, nullable=True)
    target_fat_g = Column(Float, nullable=True)
    target_water_ml = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="ai_targets")


# ── Daily Log ────────────────────────────────────────────────────────────────────
class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    log_date = Column(Date, nullable=False, default=date.today)
    total_calories_consumed = Column(Float, default=0.0)
    total_protein_g = Column(Float, default=0.0)
    total_carbs_g = Column(Float, default=0.0)
    total_fat_g = Column(Float, default=0.0)
    water_ml = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="daily_logs")


# ── Workout Log ──────────────────────────────────────────────────────────────────
class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name = Column(String, nullable=False)
    workout_type = Column(String, nullable=False)  # Cardio / Strength / Yoga / HIIT / Sports
    duration_minutes = Column(Integer, nullable=False)
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    calories_burned = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    workout_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="workout_logs")


# ── Meal Log ─────────────────────────────────────────────────────────────────────
class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meal_category = Column(String, nullable=False)  # Breakfast / Lunch / Dinner / Snack
    food_item_name = Column(String, nullable=False)
    serving_size = Column(Float, nullable=False)
    serving_unit = Column(String, nullable=False, default="g")
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    fiber_g = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    meal_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="meal_logs")


# ── Indian Food Item (RAG Dataset) ───────────────────────────────────────────────
class IndianFoodItem(Base):
    __tablename__ = "indian_food_items"

    id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String, nullable=False, index=True)
    serving_unit = Column(String, nullable=False)  # 1 Katori / 100g / 1 Roti
    serving_size_g = Column(Float, nullable=True)  # Weight in grams
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)
    fiber_g = Column(Float, nullable=True)
    tags = Column(String, nullable=True)  # South Indian / Street Food / High-Protein etc.
    description = Column(Text, nullable=True)
    is_vegetarian = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
