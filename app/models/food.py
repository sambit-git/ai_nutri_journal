from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Text
from .base import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

class FoodItem(Base):
    __tablename__ = "food_items"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text, nullable=True)
    food_type = Column(Enum('vegetable','fruit','grain','protein','dairy','snack','beverage','prepared_meal')) 
    state = Column(Enum('raw','cooked','processed','dried','frozen'))  # Physical state
    density = Column(Float)  # g/ml for volume conversion
    typical_serving_size = Column(Float)  # in grams
    serving_unit = Column(String(20))  # 'g', 'ml', 'cup', etc.
    water_content = Column(Float)  # percentage
    is_verified = Column(Boolean, default=False)  # Admin-verified entries
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    meal_uses = relationship("UserMealLog", back_populates="food")
    nutrition = relationship("NutritionalValue", uselist=False)

class NutritionalValue(Base):
    __tablename__ = "nutritional_values"
    
    id = Column(Integer, primary_key=True)
    food_id = Column(Integer, ForeignKey('food_items.id'))
    
    # Macronutrients (per 100g)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fiber = Column(Float)
    sugars = Column(Float)
    fats = Column(Float)
    saturated_fats = Column(Float)
    
    # Vitamins (% Daily Value)
    vitamin_a = Column(Float)
    vitamin_b1 = Column(Float, default=0)
    vitamin_b2 = Column(Float, default=0)
    vitamin_b3 = Column(Float, default=0)
    vitamin_b6 = Column(Float, default=0)
    vitamin_b7 = Column(Float, default=0)
    vitamin_b9 = Column(Float, default=0)
    vitamin_b12 = Column(Float, default=0)
    vitamin_c = Column(Float)
    vitamin_d = Column(Float, default=0)
    vitamin_e = Column(Float, default=0)
    vitamin_k = Column(Float, default=0)
    
    # Minerals
    calcium = Column(Float, default=0)
    iron = Column(Float, default=0)
    magnesium = Column(Float, default=0)
    phosphorus = Column(Float, default=0)
    potassium = Column(Float, default=0)
    sodium = Column(Float, default=0)
    zinc = Column(Float, default=0)
    selenium = Column(Float, default=0)
    copper = Column(Float, default=0)
    manganese = Column(Float, default=0)
    
    # Relationships
    food = relationship("FoodItem", back_populates="nutrition")
