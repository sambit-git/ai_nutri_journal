from collections import defaultdict
from sqlalchemy.orm import Session
from app.models import Meal, UserMealLog
import httpx
from sqlalchemy.orm import Session
from app.models import FoodItem, NutritionalValue
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def fetch_and_store_nutrition_data(db: Session, food_name: str, food_condition: str='raw') -> FoodItem | None:
    """Fetch nutrition data from USDA API and store in database"""
    api_url = f"https://api.nal.usda.gov/fdc/v1/foods/search"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                api_url,
                params={
                    "api_key": settings.USDA_API_KEY,
                    "query": f"{food_condition} {food_name}",
                    "pageSize": 1  # Get only the top result
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            if not data.get('foods'):
                return None

            # Get the most relevant food item
            data = filter(lambda x: x['dataType'] in ("Survey (FNDDS)", "Foundation"), data['foods'])
            food_data = next(data)
            nutrients = food_data.get('foodNutrients', [])

            # Create FoodItem
            food_item = FoodItem(
                name=food_name,
                description=food_data.get('description', ''),
                food_type=food_data.get('foodCategory', 'other'),  # Add your own logic
                state='raw',
                is_verified=False,
                typical_serving_size=food_data.get('servingSize', 100),
                serving_unit=food_data.get('servingSizeUnit', 'g')
            )
            db.add(food_item)
            db.flush()  # Get the ID before creating nutritional values

            # Helper function to find nutrient value
            def get_nutrient(nutrient_id):
                return next(
                    (n['value'] for n in nutrients if n.get('nutrientId') == nutrient_id),
                    None
                )

            # Create NutritionalValue
            nutrition = NutritionalValue(
                food_id = food_item.id,
                food_name = food_name,
                calories = get_nutrient(1008),           # Energy (kcal)
                protein = get_nutrient(1003),            # Protein (g)
                carbs = get_nutrient(1005),              # Carbohydrate, by difference (g)
                fiber = get_nutrient(1079),              # Fiber, total dietary (g)
                sugars = get_nutrient(2000),             # Total Sugars (g)
                fats = get_nutrient(1004),               # Total lipid (fat) (g)
                saturated_fats = get_nutrient(1258),     # Fatty acids, total saturated (g)
                vitamin_c = get_nutrient(1162),          # Vitamin C, total ascorbic acid (mg)
                vitamin_b6 = get_nutrient(1175),         # Vitamin B-6 (mg)
                vitamin_b12 = get_nutrient(1178),        # Vitamin B-12 (mcg)
                vitamin_a_rae = get_nutrient(1106),          # Vitamin A, RAE (mcg)
                calcium = get_nutrient(1087),            # Calcium, Ca (mg)
                iron = get_nutrient(1089),               # Iron, Fe (mg)
                potassium = get_nutrient(1092),          # Potassium, K (mg)
                sodium = get_nutrient(1093),             # Sodium, Na (mg)

                # Additional Vitamins
                vitamin_a_iu = get_nutrient(1104),       # Vitamin A, IU (International Units)
                vitamin_b1 = get_nutrient(1165),         # Vitamin B1 (Thiamin) (mg)
                vitamin_b2 = get_nutrient(1166),         # Vitamin B2 (Riboflavin) (mg)
                vitamin_b3 = get_nutrient(1167),         # Vitamin B3 (Niacin) (mg)
                vitamin_b7 = get_nutrient(1176),         # Biotin (mcg)
                vitamin_b9 = get_nutrient(1187),         # Folate, food (mcg)
                vitamin_d2_d3 = get_nutrient(1104),      # Vitamin D (D2 + D3) (IU)
                vitamin_d3 = get_nutrient(1112),         # Vitamin D3 (cholecalciferol) (IU)
                vitamin_e = get_nutrient(1109),          # Vitamin E (Alpha-tocopherol) (mg)
                vitamin_k_mk = get_nutrient(1183),       # Vitamin K (Menaquinone-4) (mcg)
                vitamin_k_pk = get_nutrient(1185),       # Vitamin K (Phylloquinone) (mcg)

                # Minerals
                magnesium = get_nutrient(1090),          # Magnesium, Mg (mg)
                phosphorus = get_nutrient(1091),         # Phosphorus, P (mg)
                zinc = get_nutrient(1095),               # Zinc, Zn (mg)
                selenium = get_nutrient(1103),           # Selenium, Se (mcg)
                copper = get_nutrient(1098),             # Copper, Cu (mg)
                manganese = get_nutrient(1101),          # Manganese, Mn (mg)

                # Fatty Acids
                monounsaturated_fats = get_nutrient(1292), # Fatty acids, total monounsaturated (g)
                polyunsaturated_fats = get_nutrient(1293), # Fatty acids, total polyunsaturated (g)
                saturated_fats_specific = get_nutrient(1258), # Saturated fats (g)

                # Amino Acids
                lysine = get_nutrient(1214),             # Lysine (g)
                isoleucine = get_nutrient(1212),         # Isoleucine (g)
                alanine = get_nutrient(1222),            # Alanine (g)
                threonine = get_nutrient(1211),          # Threonine (g)
                methionine = get_nutrient(1215),         # Methionine (g)
                histidine = get_nutrient(1221),          # Histidine (g)
                leucine = get_nutrient(1213),            # Leucine (g)
                valine = get_nutrient(1219),             # Valine (g)

                # Other Nutrients
                caffeine = get_nutrient(1057),           # Caffeine (mg)
                water = get_nutrient(1051),              # Water (g)
                ash = get_nutrient(1007),                # Ash (g)
                starch = get_nutrient(1009),             # Starch (g)

                # Optional: Other Nutrients and Compounds (specific cases)
                # galactose = get_nutrient(1075),          # Galactose (g)
                # theobromine = get_nutrient(1058),        # Theobromine (mg)
                # beta_sitosterol = get_nutrient(1288),    # Beta-sitosterol (mg)
                # maltose = get_nutrient(1014),           # Maltose (g)
                # fructose = get_nutrient(1012),           # Fructose (g)
                # lactose = get_nutrient(1013),            # Lactose (g)
                # sucrose = get_nutrient(1010),            # Sucrose (g)
                # glucose = get_nutrient(1011)             # Glucose (g)
            )
            db.add(nutrition)
            db.commit()
            return food_item

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to fetch/store nutrition data: {str(e)}")
        return None

def calculate_meal_nutrition(meal: Meal, db: Session) -> dict:
    """Calculate nutrition from meal components"""
    totals = defaultdict(float)
    components = db.query(UserMealLog).filter(
        UserMealLog.meal_id == meal.id
    ).all()

    for comp in components:
        nutrition = comp.food.nutrition  # Assumes FoodItem.nutrition relationship
        ratio = comp.quantity / 100.0  # Calculate per-gram values
        
        # Sum all nutrients
        for field in ['calories', 'protein', 'carbs', 'fats']:
            totals[field] += getattr(nutrition, field) * ratio
    
    # Convert to schema
    return dict(totals)