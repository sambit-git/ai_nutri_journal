from functools import lru_cache
from sqlalchemy.orm import Session
from app.models.meal import Meal
from app.services.nutrition import calculate_nutrition

@lru_cache(maxsize=1000)
def get_cached_nutrition(meal_id: int, db: Session):
    """Cache with 1000 most recent meal calculations"""
    return calculate_nutrition(meal_id, db)