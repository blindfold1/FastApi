from typing import Dict


def parse_food_nutrients(food_data: Dict) -> Dict[str, float]:
    """
    Парсит питательные вещества из данных USDA API.

    Args:
        food_data: Данные о продукте из USDA API.

    Returns:
        Словарь с питательными веществами.
    """
    nutrient_map = {
        "Energy": ("calories", lambda n: n.get("unitName") == "KCAL"),
        "Protein": ("proteins", lambda _: True),
        "Carbohydrate, by difference": ("carbs", lambda _: True),
        "Total lipid (fat)": ("fats", lambda _: True),
        "Vitamin C, total ascorbic acid": ("vitamin_c", lambda _: True),
        "Calcium, Ca": ("calcium", lambda _: True),
    }

    nutrients = {
        "calories": 0.0,
        "proteins": 0.0,
        "carbs": 0.0,
        "fats": 0.0,
        "vitamin_c": 0.0,
        "calcium": 0.0,
    }

    for nutrient in food_data.get("foodNutrients", []):
        nutrient_name = nutrient["nutrientName"]
        if nutrient_name in nutrient_map:
            field, condition = nutrient_map[nutrient_name]
            if condition(nutrient):
                nutrients[field] = float(nutrient.get("value", 0))

    return nutrients
