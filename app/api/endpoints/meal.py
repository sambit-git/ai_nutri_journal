# Standard Library
import json
import os
import uuid
from datetime import datetime
from typing import List, Optional

# Third Party
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func

# Local Application
from app.core.auth import get_current_active_user
from app.core.config import settings
from app.api.dependencies import get_db
from app.models import Meal, User, UserMealLog, FoodItem
from app.schemas import (
    Meal as MealSchema,
    MealResponse, MealType,
    MealComponent
    )
from app.services.nutrition import calculate_meal_nutrition
from app.services.meals import format_meal_response
from app.services.nutrition import fetch_and_store_nutrition_data

router = APIRouter(prefix="/meals", tags=["Meals"])

@router.post("", response_model=MealResponse)
async def create_meal(
    meal_type: MealType = Form(...),
    # components: str = Form(...),  # JSON string of components
    name: Optional[str] = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    image_path = None
    file_ext = os.path.splitext(image.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    image_path = os.path.join(settings.STATIC_FILES_DIR, filename)
    
    with open(image_path, "wb") as buffer:
        buffer.write(await image.read())
    
    detection_result = settings.IMAGE_CLASSIFIER_MODEL.predict(image_path)
    detected_food = detection_result["class"]
    
    image_path = f"/static/{filename}"

    food_item = db.query(FoodItem).filter(
        func.lower(FoodItem.name) == func.lower(detected_food)
    ).first()

    if not food_item:
        food_item = await fetch_and_store_nutrition_data(db, detected_food)
        if not food_item:
            print(f"Nutrition data not available for {detected_food}")

    # Create meal
    db_meal = Meal(
        meal_type=meal_type,
        name=name,
        image_path=image_path,
        owner_id=current_user.id,
        timestamp=datetime.utcnow()
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)

    db_component = UserMealLog(
        meal_id=db_meal.id,
        food_id=food_item.id,
        quantity=food_item.typical_serving_size,
        preparation_notes=None,
    )
    db.add(db_component)
    
    db.commit()
    db.refresh(db_meal)

    # Calculate nutrition
    nutrition = calculate_meal_nutrition(db_meal, db)
    
    return {
        **MealSchema.model_validate(db_meal).model_dump(),
        "nutrition": nutrition,
        "components": [
            {
                "food_id": db_component.food_id,
                "food_name": food_item.name,
                "quantity": db_component.quantity
            }
        ]
    }


@router.get("", response_model=List[MealResponse])
def get_meals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all meals with nutrition data"""
    meals = db.query(Meal).filter(
        Meal.owner_id == current_user.id
    ).order_by(Meal.timestamp.desc()).offset(skip).limit(limit).all()

    return [format_meal_response(meal, db) for meal in meals]


@router.get("/{meal_id}", response_model=MealResponse)
def get_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed meal data with nutrition"""
    meal = db.query(Meal).filter(
        Meal.id == meal_id,
        Meal.owner_id == current_user.id
    ).first()
    
    if not meal:
        raise HTTPException(404, detail="Meal not found")
    
    return format_meal_response(meal, db)

