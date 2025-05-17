from pytest_httpx import HTTPXMock


def test_search_and_add_food_success(client, httpx_mock):
    httpx_mock.add_response(
        url="https://api.nal.usda.gov/fdc/v1/foods/search",
        method="GET",
        json={
            "foods": [
                {
                    "description": "Milk",
                    "foodNutrients": [
                        {"nutrientName": "Energy", "value": 60.0},
                        {"nutrientName": "Protein", "value": 3.2},
                        {"nutrientName": "Total lipid (fat)", "value": 3.3},
                        {"nutrientName": "Carbohydrate, by difference", "value": 4.8},
                    ],
                }
            ]
        },
    )
    response = client.post("/auth/token", data={"username": "Test", "password": "1111"})
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    response = client.post(
        "/food/search-and-add-food/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "milk"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Milk"
    assert data["calories"] == 60.0
    assert data["proteins"] == 3.2
    assert data["fats"] == 3.3
    assert data["carbs"] == 4.8


def test_search_and_add_food_unauthorized(client):
    response = client.post("/food/search-and-add-food/", json={"name": "milk"})
    assert response.status_code == 401


def test_search_and_add_food_not_found(client, httpx_mock):
    httpx_mock.add_response(
        url="https://api.nal.usda.gov/fdc/v1/foods/search",
        method="GET",
        json={"foods": []},
    )
    response = client.post("/auth/token", data={"username": "Test", "password": "1111"})
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    response = client.post(
        "/food/search-and-add-food/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "nonexistentfood"},
    )
    assert response.status_code == 404
