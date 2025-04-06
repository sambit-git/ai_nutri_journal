from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models import Meal, User
from app.core.auth import get_current_active_user
from app.schemas.nutrition import DailyNutritionResponse
from app.services.nutrition import calculate_meal_nutrition
from app.services.meals import format_meal_response


router = APIRouter(prefix="/nutrition", tags=["Nutrition"])

@router.get("/daily", response_model=DailyNutritionResponse)
def get_daily_nutrition(
    date: str,  # Expects YYYY-MM-DD format
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get aggregated nutrition for a specific day"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, detail="Invalid date format. Use YYYY-MM-DD")

    # Calculate date range (00:00 to 23:59)
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)

    # Get all meals for the day
    meals = db.query(Meal).filter(
        Meal.owner_id == current_user.id,
        Meal.timestamp >= start_datetime,
        Meal.timestamp < end_datetime
    ).all()

    # Calculate totals
    totals = {
        "date": target_date,
        "total_calories": 0,
        "total_protein": 0,
        "total_carbs": 0,
        "total_fats": 0,
        "meals": []
    }

    for meal in meals:
        nutrition = calculate_meal_nutrition(meal, db)
        totals["total_calories"] += nutrition["calories"]
        totals["total_protein"] += nutrition["protein"]
        totals["total_carbs"] += nutrition["carbs"]
        totals["total_fats"] += nutrition["fats"]
        totals["meals"].append(format_meal_response(meal, db))

    return totals