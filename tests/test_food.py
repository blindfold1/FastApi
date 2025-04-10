# tests/test_food.py
from fastapi import status
from httpx import AsyncClient


def test_search_and_add_food_success(client, httpx_mock):
    mock_response = {
        "foods": [
            {
                "description": "Milk, whole",
                "foodNutrients": [
                    {"nutrientName": "Energy", "value": 60.0},
                    {"nutrientName": "Protein", "value": 3.2},
                    {"nutrientName": "Total lipid (fat)", "value": 3.3},
                    {"nutrientName": "Carbohydrate, by difference", "value": 4.8},
                    {"nutrientName": "Vitamin C, total ascorbic acid", "value": 0.0},
                    {"nutrientName": "Calcium, Ca", "value": 120.0},
                ],
            }
        ]
    }
    for data_type in ["Foundation", "Survey (FNDDS)", "Branded", "SR Legacy"]:
        httpx_mock.add_response(
            url="https://api.nal.usda.gov/fdc/v1/foods/search",
            method="GET",
            match_querystring=True,
            json=mock_response if data_type == "Survey (FNDDS)" else {"foods": []},
        )

    login_response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    access_token = login_response.json()["access_token"]

    response = client.post(
        "/food/search-and-add-food/",
        headers={"Authorization": f"Bearer ${access_token}"},
        json={"name": "milk", "exact_match": False, "data_type": "Foundation"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Milk, whole"
    assert response.json()["calories"] == 60.0
    assert response.json()["proteins"] == 3.2  # Now a float
    assert response.json()["fats"] == 3.3
    assert response.json()["carbs"] == 4.8  # Now a float
    assert response.json()["vitamin_c"] == 0.0
    assert response.json()["calcium"] == 120.0
    assert response.json()["user_id"] == 1


def test_search_and_add_food_unauthorized(client):
    response = client.post(
        "/food/search-and-add-food/",
        json={"name": "milk", "exact_match": False, "data_type": "Foundation"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid token"


def test_search_and_add_food_not_found(client, httpx_mock):
    for data_type in ["Foundation", "Survey (FNDDS)", "Branded", "SR Legacy"]:
        httpx_mock.add_response(
            url="https://api.nal.usda.gov/fdc/v1/foods/search",
            method="GET",
            match_querystring=True,
            json={"foods": []},
        )

    login_response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    access_token = login_response.json()["access_token"]

    response = client.post(
        "/food/search-and-add-food/",
        headers={"Authorization": f"Bearer ${access_token}"},
        json={
            "name": "nonexistentfood",
            "exact_match": False,
            "data_type": "Foundation",
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "No food found for query 'nonexistentfood'"
