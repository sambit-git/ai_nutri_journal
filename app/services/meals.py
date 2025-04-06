from .nutrition import calculate_meal_nutrition
from app.models import Meal, UserMealLog
from sqlalchemy.orm import Session



def format_meal_response(meal: Meal, db: Session) -> dict:
    """Convert SQLAlchemy Meal to API-ready dict with nutrition"""
    components = db.query(UserMealLog).filter(
        UserMealLog.meal_id == meal.id
    ).all()
    
    # Calculate nutrition
    nutrition = calculate_meal_nutrition(meal, db)
    
    # Format components
    formatted_components = []
    for comp in components:
        formatted_components.append({
            "food_id": comp.food_id,
            "quantity": comp.quantity,
            "preparation_notes": comp.preparation_notes,
            "food_name": comp.food.name  # Added from relationship
        })
    
    return {
        "id": meal.id,
        "meal_type": meal.meal_type,
        "name": meal.name,
        "image_path": meal.image_path,
        "timestamp": meal.timestamp,
        "owner_id": meal.owner_id,
        "nutrition": nutrition,
        "components": formatted_components
    }