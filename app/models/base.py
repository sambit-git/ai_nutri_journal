from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    snacks = "snacks"
    dinner = "dinner"
    pre_workout = "pre-workout"
    post_workout = "post-workout"