from collections import defaultdict
from sqlalchemy.orm import Session
from app.models import Meal, UserMealLog

def calculate_meal_nutrition(meal: Meal, db: Session) -> dict:
    """Calculate nutrition from meal components"""
    totals = defaultdict(float)
    components = db.query(UserMealLog).filter(
        UserMealLog.meal_id == meal.id
    ).all()

    for comp in components:
        nutrition = comp.food.nutrition  # Assumes FoodItem.nutrition relationship
        ratio = comp.quantity / 100.0  # Calculate per-gram values
        
        # Sum all nutrients
        for field in ['calories', 'protein', 'carbs', 'fats']:
            totals[field] += getattr(nutrition, field) * ratio
    
    # Convert to schema
    return dict(totals)