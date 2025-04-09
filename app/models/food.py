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
    food_type = Column(String(100))
        # Enum('vegetable','fruit','grain','protein','dairy','snack','beverage','prepared_meal')) 
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
    
    # General Nutritional Information (per 100g)
    calories = Column(Float, nullable=True)                    # Total calories (kcal)
    protein = Column(Float, nullable=True)                     # Total protein (g)
    carbs = Column(Float, nullable=True)                       # Total carbohydrates (g)
    fiber = Column(Float, nullable=True)                       # Total dietary fiber (g)
    sugars = Column(Float, nullable=True)                      # Total sugars (g)
    fats = Column(Float, nullable=True)                        # Total fats (g)
    saturated_fats = Column(Float, nullable=True)              # Saturated fats (g)

    # Vitamins (% Daily Value or per 100g)
    vitamin_a_iu = Column(Float, nullable=True)                # Vitamin A (IU)
    vitamin_a_rae = Column(Float, nullable=True)               # Vitamin A (RAE)
    vitamin_b1 = Column(Float, default=0, nullable=True)        # Vitamin B1 (Thiamin)
    vitamin_b2 = Column(Float, default=0, nullable=True)        # Vitamin B2 (Riboflavin)
    vitamin_b3 = Column(Float, default=0, nullable=True)        # Vitamin B3 (Niacin)
    vitamin_b6 = Column(Float, default=0, nullable=True)        # Vitamin B6
    vitamin_b7 = Column(Float, default=0, nullable=True)        # Vitamin B7 (Biotin)
    vitamin_b9 = Column(Float, default=0, nullable=True)        # Vitamin B9 (Folate)
    vitamin_b12 = Column(Float, default=0, nullable=True)       # Vitamin B12
    vitamin_c = Column(Float, nullable=True)                    # Vitamin C
    vitamin_d2_d3 = Column(Float, default=0, nullable=True)     # Vitamin D (D2 + D3)
    vitamin_d3 = Column(Float, default=0, nullable=True)        # Vitamin D3 (cholecalciferol)
    vitamin_e = Column(Float, default=0, nullable=True)         # Vitamin E (Alpha-tocopherol)
    vitamin_k_mk = Column(Float, default=0, nullable=True)      # Vitamin K (Menaquinone-4)
    vitamin_k_pk = Column(Float, default=0, nullable=True)      # Vitamin K (Phylloquinone)

    # Minerals (per 100g)
    calcium = Column(Float, default=0, nullable=True)           # Calcium (mg)
    iron = Column(Float, default=0, nullable=True)              # Iron (mg)
    magnesium = Column(Float, default=0, nullable=True)         # Magnesium (mg)
    phosphorus = Column(Float, default=0, nullable=True)        # Phosphorus (mg)
    potassium = Column(Float, default=0, nullable=True)         # Potassium (mg)
    sodium = Column(Float, default=0, nullable=True)            # Sodium (mg)
    zinc = Column(Float, default=0, nullable=True)              # Zinc (mg)
    selenium = Column(Float, default=0, nullable=True)          # Selenium (mcg)
    copper = Column(Float, default=0, nullable=True)            # Copper (mg)
    manganese = Column(Float, default=0, nullable=True)         # Manganese (mg)

    # Fatty Acids (per 100g)
    total_fatty_acids = Column(Float, nullable=True)            # Total Fatty Acids (g)
    monounsaturated_fats = Column(Float, nullable=True)         # Monounsaturated fats (g)
    polyunsaturated_fats = Column(Float, nullable=True)         # Polyunsaturated fats (g)
    saturated_fats_specific = Column(Float, nullable=True)      # Saturated fats (specific)

    # Essential Amino Acids (per 100g)
    lysine = Column(Float, nullable=True)                       # Lysine (g)
    isoleucine = Column(Float, nullable=True)                   # Isoleucine (g)
    alanine = Column(Float, nullable=True)                      # Alanine (g)
    threonine = Column(Float, nullable=True)                    # Threonine (g)
    methionine = Column(Float, nullable=True)                   # Methionine (g)
    histidine = Column(Float, nullable=True)                    # Histidine (g)
    leucine = Column(Float, nullable=True)                      # Leucine (g)
    valine = Column(Float, nullable=True)                       # Valine (g)

    # Other Nutrients
    caffeine = Column(Float, nullable=True)                     # Caffeine (mg)
    water = Column(Float, nullable=True)                        # Water (g)
    ash = Column(Float, nullable=True)                          # Ash (g)
    starch = Column(Float, nullable=True)                       # Starch (g)

    # Additional Information
    food_name = Column(String(255), nullable=False)             # Food name or identifier
    # food_code = Column(String(255), nullable=True)
    
    # Relationships
    food = relationship("FoodItem", back_populates="nutrition")
