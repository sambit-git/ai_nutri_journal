from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from .base import Base, MealType
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from collections import defaultdict 
from typing import Dict

class UserMealLog(Base):
    __tablename__ = "meal_components"  # Consider renaming to "meal_portions"
    
    id = Column(Integer, primary_key=True)
    meal_id = Column(Integer, ForeignKey('meals.id'))
    food_id = Column(Integer, ForeignKey('food_items.id'))
    quantity = Column(Float)  # in grams
    preparation_notes = Column(String(200), nullable=True)
    
    # Relationships
    meal = relationship("Meal", back_populates="components")
    food = relationship("FoodItem", back_populates="meal_uses")  # Add this to FoodItem


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    meal_type = Column(Enum(MealType), nullable=False)
    name = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="meals")

    components = relationship(
        "UserMealLog", 
        back_populates="meal",
        cascade="all, delete-orphan"
    )
