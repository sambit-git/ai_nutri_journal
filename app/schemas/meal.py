from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class MealType(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    snacks = "snacks"
    dinner = "dinner"
    pre_workout = "pre-workout"
    post_workout = "post-workout"

class MealBase(BaseModel):
    meal_type: MealType
    name: Optional[str] = None


class Meal(MealBase):
    id: int
    image_path: Optional[str] = None
    timestamp: datetime
    owner_id: int

    class Config:
        from_attributes = True

class MealComponent(BaseModel):
    food_id: int = Field(..., gt=0, description="ID of the food item")
    quantity: float = Field(..., gt=0, description="Quantity in grams")
    preparation_notes: Optional[str] = None

class MealCreate(MealBase):
    components: List[MealComponent] = Field(..., min_items=1)
    image: Optional[str] = None  # Base64 encoded image if needed

class MealResponse(MealBase):
    id: int
    image_path: Optional[str]
    timestamp: datetime
    owner_id: int
    nutrition: dict  # Will contain calculated values
    components: List[MealComponent]
    
    class Config:
        from_attributes = True

