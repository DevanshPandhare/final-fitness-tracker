from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from database import get_db, User, MealLog, DailyLog, IndianFoodItem
from schemas import MealLogCreate, MealLogResponse, MealLogUpdate, IndianFoodItemResponse
from auth import get_current_user

router = APIRouter(prefix="/meals", tags=["Meal Logs & Nutrition"])


def _update_daily_log(user_id: int, log_date: date, db: Session):
    """Recalculate and update DailyLog totals from MealLog entries."""
    meals = db.query(MealLog).filter(
        MealLog.user_id == user_id,
        MealLog.meal_date >= datetime.combine(log_date, datetime.min.time()),
        MealLog.meal_date <= datetime.combine(log_date, datetime.max.time()),
    ).all()

    daily_log = db.query(DailyLog).filter(
        DailyLog.user_id == user_id, DailyLog.log_date == log_date
    ).first()

    if not daily_log:
        daily_log = DailyLog(user_id=user_id, log_date=log_date)
        db.add(daily_log)

    daily_log.total_calories_consumed = round(sum(m.calories for m in meals), 1)
    daily_log.total_protein_g = round(sum(m.protein_g or 0 for m in meals), 1)
    daily_log.total_carbs_g = round(sum(m.carbs_g or 0 for m in meals), 1)
    daily_log.total_fat_g = round(sum(m.fat_g or 0 for m in meals), 1)
    db.commit()


@router.post("/", response_model=MealLogResponse, status_code=status.HTTP_201_CREATED)
def log_meal(
    data: MealLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log a new meal and automatically update the daily totals."""
    meal_datetime = data.meal_date or datetime.utcnow()
    meal = MealLog(
        user_id=current_user.id,
        meal_category=data.meal_category,
        food_item_name=data.food_item_name,
        serving_size=data.serving_size,
        serving_unit=data.serving_unit,
        calories=data.calories,
        protein_g=data.protein_g,
        carbs_g=data.carbs_g,
        fat_g=data.fat_g,
        fiber_g=data.fiber_g,
        notes=data.notes,
        meal_date=meal_datetime,
    )
    db.add(meal)
    db.commit()
    db.refresh(meal)

    # Update daily log totals
    _update_daily_log(current_user.id, meal_datetime.date(), db)
    return meal


@router.get("/", response_model=List[MealLogResponse])
def get_meals(
    skip: int = 0,
    limit: int = 100,
    meal_category: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all meal logs with optional filters."""
    query = db.query(MealLog).filter(MealLog.user_id == current_user.id)
    if meal_category:
        query = query.filter(MealLog.meal_category == meal_category)
    if from_date:
        query = query.filter(MealLog.meal_date >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        query = query.filter(MealLog.meal_date <= datetime.combine(to_date, datetime.max.time()))
    return query.order_by(MealLog.meal_date.desc()).offset(skip).limit(limit).all()


@router.get("/today", response_model=dict)
def get_today_meals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's meal logs grouped by meal category."""
    today = datetime.utcnow().date()
    meals = db.query(MealLog).filter(
        MealLog.user_id == current_user.id,
        MealLog.meal_date >= datetime.combine(today, datetime.min.time()),
        MealLog.meal_date <= datetime.combine(today, datetime.max.time()),
    ).order_by(MealLog.meal_date.asc()).all()

    grouped = {"Breakfast": [], "Lunch": [], "Dinner": [], "Snack": []}
    for m in meals:
        cat = m.meal_category if m.meal_category in grouped else "Snack"
        grouped[cat].append({
            "id": m.id,
            "food_item_name": m.food_item_name,
            "serving_size": m.serving_size,
            "serving_unit": m.serving_unit,
            "calories": m.calories,
            "protein_g": m.protein_g,
            "carbs_g": m.carbs_g,
            "fat_g": m.fat_g,
            "meal_date": m.meal_date.isoformat(),
        })

    return {
        "date": today.isoformat(),
        "meals_by_category": grouped,
        "totals": {
            "calories": round(sum(m.calories for m in meals), 1),
            "protein_g": round(sum(m.protein_g or 0 for m in meals), 1),
            "carbs_g": round(sum(m.carbs_g or 0 for m in meals), 1),
            "fat_g": round(sum(m.fat_g or 0 for m in meals), 1),
        },
    }


@router.get("/search-food", response_model=List[IndianFoodItemResponse])
def search_food(
    q: str = Query(..., description="Search term (e.g. 'Paneer Bhurji', 'dal')"),
    limit: int = 10,
    vegetarian_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search the Indian food database by name or tags."""
    query = db.query(IndianFoodItem)
    if q:
        search = f"%{q}%"
        query = query.filter(
            IndianFoodItem.food_name.ilike(search) |
            IndianFoodItem.tags.ilike(search) |
            IndianFoodItem.description.ilike(search)
        )
    if vegetarian_only:
        query = query.filter(IndianFoodItem.is_vegetarian == True)
    return query.limit(limit).all()


@router.get("/{meal_id}", response_model=MealLogResponse)
def get_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific meal by ID."""
    meal = db.query(MealLog).filter(
        MealLog.id == meal_id, MealLog.user_id == current_user.id
    ).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    return meal


@router.put("/{meal_id}", response_model=MealLogResponse)
def update_meal(
    meal_id: int,
    data: MealLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a meal log entry and recalculate daily totals."""
    meal = db.query(MealLog).filter(
        MealLog.id == meal_id, MealLog.user_id == current_user.id
    ).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(meal, field, value)
    db.commit()
    db.refresh(meal)
    _update_daily_log(current_user.id, meal.meal_date.date(), db)
    return meal


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a meal log entry and recalculate daily totals."""
    meal = db.query(MealLog).filter(
        MealLog.id == meal_id, MealLog.user_id == current_user.id
    ).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    meal_date = meal.meal_date.date()
    db.delete(meal)
    db.commit()
    _update_daily_log(current_user.id, meal_date, db)
