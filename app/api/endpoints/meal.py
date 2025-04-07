# Standard Library
import json
import os
import uuid
from datetime import datetime
from typing import List, Optional

# Third Party
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

# Local Application
from app.core.auth import get_current_active_user
from app.core.config import settings
from app.api.dependencies import get_db
from app.models import Meal, User, UserMealLog
from app.schemas import (
    Meal as MealSchema,
    MealResponse, MealType,
    MealComponent
    )
from app.services.nutrition import calculate_meal_nutrition
from app.services.meals import format_meal_response

router = APIRouter(prefix="/meals", tags=["Meals"])

@router.post("", response_model=MealResponse)
async def create_meal(
    meal_type: MealType = Form(...),
    components: str = Form(...),  # JSON string of components
    name: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Parse components JSON
    try:
        component_data = json.loads(components)
        validated_components = [MealComponent(**c) for c in component_data]
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(400, detail=f"Invalid components format: {str(e)}")

    # Handle image upload (keep your existing logic)
    image_path = None
    if image:
        file_ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        image_path = os.path.join(settings.STATIC_FILES_DIR, filename)
        
        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())
        
        image_path = f"/static/{filename}"

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

    # Add meal components
    for component in validated_components:
        db_component = UserMealLog(
            meal_id=db_meal.id,
            food_id=component.food_id,
            quantity=component.quantity,
            preparation_notes=component.preparation_notes
        )
        db.add(db_component)
    
    db.commit()
    db.refresh(db_meal)

    # Calculate nutrition
    nutrition = calculate_meal_nutrition(db_meal, db)
    
    return {
        **MealSchema.model_validate(db_meal).model_dump(),
        "nutrition": nutrition,
        "components": validated_components
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

