from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from database import get_db, User, WorkoutLog
from schemas import WorkoutLogCreate, WorkoutLogResponse, WorkoutLogUpdate
from auth import get_current_user

router = APIRouter(prefix="/workouts", tags=["Workout Logs"])

# Calorie burn rates (kcal/minute) based on 70kg person average
CALORIES_PER_MINUTE = {
    "Cardio": 9.5,
    "Strength": 6.0,
    "Yoga": 3.5,
    "HIIT": 12.0,
    "Sports": 8.0,
    "Other": 5.0,
}


@router.post("/", response_model=WorkoutLogResponse, status_code=status.HTTP_201_CREATED)
def log_workout(
    data: WorkoutLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log a new workout session. Calories are auto-calculated if not provided."""
    calories = data.calories_burned
    if calories is None:
        rate = CALORIES_PER_MINUTE.get(data.workout_type, 5)
        # Adjust slightly for user weight if known
        weight_factor = (current_user.weight_kg or 70) / 70
        calories = round(rate * data.duration_minutes * weight_factor, 1)

    log = WorkoutLog(
        user_id=current_user.id,
        exercise_name=data.exercise_name,
        workout_type=data.workout_type,
        duration_minutes=data.duration_minutes,
        sets=data.sets,
        reps=data.reps,
        weight_kg=data.weight_kg,
        calories_burned=calories,
        notes=data.notes,
        workout_date=data.workout_date or datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/", response_model=List[WorkoutLogResponse])
def get_workouts(
    skip: int = 0,
    limit: int = 50,
    workout_type: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all workouts for the current user with optional filters."""
    query = db.query(WorkoutLog).filter(WorkoutLog.user_id == current_user.id)
    if workout_type:
        query = query.filter(WorkoutLog.workout_type == workout_type)
    if from_date:
        query = query.filter(WorkoutLog.workout_date >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        query = query.filter(WorkoutLog.workout_date <= datetime.combine(to_date, datetime.max.time()))
    return query.order_by(WorkoutLog.workout_date.desc()).offset(skip).limit(limit).all()


@router.get("/today", response_model=dict)
def get_today_workouts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's workout summary."""
    today = datetime.utcnow().date()
    workouts = db.query(WorkoutLog).filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.workout_date >= datetime.combine(today, datetime.min.time()),
        WorkoutLog.workout_date <= datetime.combine(today, datetime.max.time()),
    ).all()

    return {
        "date": today.isoformat(),
        "workouts": [
            {
                "id": w.id,
                "exercise_name": w.exercise_name,
                "workout_type": w.workout_type,
                "duration_minutes": w.duration_minutes,
                "calories_burned": w.calories_burned,
                "sets": w.sets,
                "reps": w.reps,
                "weight_kg": w.weight_kg,
                "workout_date": w.workout_date.isoformat(),
            }
            for w in workouts
        ],
        "totals": {
            "total_duration": sum(w.duration_minutes for w in workouts),
            "total_calories_burned": round(sum(w.calories_burned or 0 for w in workouts), 1),
            "workout_count": len(workouts),
        },
    }


@router.get("/{workout_id}", response_model=WorkoutLogResponse)
def get_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific workout by ID."""
    log = db.query(WorkoutLog).filter(
        WorkoutLog.id == workout_id, WorkoutLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Workout not found")
    return log


@router.put("/{workout_id}", response_model=WorkoutLogResponse)
def update_workout(
    workout_id: int,
    data: WorkoutLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a workout log entry."""
    log = db.query(WorkoutLog).filter(
        WorkoutLog.id == workout_id, WorkoutLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Workout not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a workout log entry."""
    log = db.query(WorkoutLog).filter(
        WorkoutLog.id == workout_id, WorkoutLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(log)
    db.commit()
