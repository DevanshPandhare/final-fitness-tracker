from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from database import get_db, User, WorkoutLog, MealLog, DailyLog
from schemas import DashboardSummary, DailyLogResponse, WaterUpdate
from auth import get_current_user
from typing import Optional

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    log_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get complete dashboard summary for a specific date (defaults to today)."""
    target_date = log_date or datetime.utcnow().date()
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date, datetime.max.time())

    # Today's workouts
    workouts = db.query(WorkoutLog).filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.workout_date.between(day_start, day_end),
    ).all()
    today_calories_burned = round(sum(w.calories_burned or 0 for w in workouts), 1)

    # Daily log (nutrition)
    daily_log = db.query(DailyLog).filter(
        DailyLog.user_id == current_user.id,
        DailyLog.log_date == target_date,
    ).first()

    today_calories = daily_log.total_calories_consumed if daily_log else 0.0
    today_protein = daily_log.total_protein_g if daily_log else 0.0
    today_carbs = daily_log.total_carbs_g if daily_log else 0.0
    today_fat = daily_log.total_fat_g if daily_log else 0.0
    today_water = daily_log.water_ml if daily_log else 0.0

    # AI targets
    ai_targets = current_user.ai_targets

    # BMI
    bmi = None
    latest_weight = current_user.weight_kg
    if latest_weight and current_user.height_cm:
        h = current_user.height_cm / 100
        bmi = round(latest_weight / (h ** 2), 1)

    return DashboardSummary(
        today_calories=today_calories,
        today_protein=today_protein,
        today_carbs=today_carbs,
        today_fat=today_fat,
        today_water_ml=today_water,
        target_calories=ai_targets.target_calories if ai_targets else None,
        target_protein=ai_targets.target_protein_g if ai_targets else None,
        target_water_ml=ai_targets.target_water_ml if ai_targets else None,
        today_calories_burned=today_calories_burned,
        today_workouts=len(workouts),
        bmi=bmi,
        latest_weight=latest_weight,
    )


@router.get("/weekly-chart")
def get_weekly_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get 7-day chart data: calories consumed vs burned."""
    chart = []
    for i in range(6, -1, -1):
        day = (datetime.utcnow() - timedelta(days=i)).date()
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())

        workouts = db.query(WorkoutLog).filter(
            WorkoutLog.user_id == current_user.id,
            WorkoutLog.workout_date.between(day_start, day_end),
        ).all()

        daily_log = db.query(DailyLog).filter(
            DailyLog.user_id == current_user.id,
            DailyLog.log_date == day,
        ).first()

        chart.append({
            "date": day.isoformat(),
            "day": day.strftime("%a"),
            "calories_consumed": daily_log.total_calories_consumed if daily_log else 0,
            "calories_burned": round(sum(w.calories_burned or 0 for w in workouts), 1),
            "protein_g": daily_log.total_protein_g if daily_log else 0,
            "workout_count": len(workouts),
        })
    return {"chart_data": chart}


@router.get("/macro-breakdown")
def get_macro_breakdown(
    log_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get macro breakdown for a specific date (pie chart data)."""
    target_date = log_date or datetime.utcnow().date()
    daily_log = db.query(DailyLog).filter(
        DailyLog.user_id == current_user.id,
        DailyLog.log_date == target_date,
    ).first()

    if not daily_log:
        return {"date": target_date.isoformat(), "macros": {"protein": 0, "carbs": 0, "fat": 0}}

    return {
        "date": target_date.isoformat(),
        "macros": {
            "protein": daily_log.total_protein_g,
            "carbs": daily_log.total_carbs_g,
            "fat": daily_log.total_fat_g,
        },
    }


@router.get("/meal-category-breakdown")
def get_meal_category_breakdown(
    log_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get calories breakdown by meal category for the given date."""
    target_date = log_date or datetime.utcnow().date()
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date, datetime.max.time())

    meals = db.query(MealLog).filter(
        MealLog.user_id == current_user.id,
        MealLog.meal_date.between(day_start, day_end),
    ).all()

    breakdown = {}
    for m in meals:
        breakdown[m.meal_category] = breakdown.get(m.meal_category, 0) + m.calories

    return {"date": target_date.isoformat(), "breakdown": breakdown}


@router.patch("/water", response_model=DailyLogResponse)
def update_water(
    data: WaterUpdate,
    log_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log or update water intake for a date."""
    target_date = log_date or datetime.utcnow().date()
    daily_log = db.query(DailyLog).filter(
        DailyLog.user_id == current_user.id,
        DailyLog.log_date == target_date,
    ).first()

    if not daily_log:
        daily_log = DailyLog(user_id=current_user.id, log_date=target_date)
        db.add(daily_log)

    daily_log.water_ml = data.water_ml
    db.commit()
    db.refresh(daily_log)
    return daily_log
