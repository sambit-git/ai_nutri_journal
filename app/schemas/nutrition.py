# app/schemas/nutrition.py
from datetime import date
from pydantic import BaseModel
from typing import List
from .meal import MealResponse

class DailyNutritionResponse(BaseModel):
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fats: float
    meals: List[MealResponse]