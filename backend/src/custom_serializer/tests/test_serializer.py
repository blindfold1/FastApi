import pytest
import os
from custom_serializer.formats.json_serializer import JsonSerializer
from custom_serializer.formats.customtext_serializer import CustomTextSerializer

@pytest.fixture
def cleanup():
    yield
    for file in ["test.json", "test.txt"]:
        if os.path.exists(file):
            os.remove(file)

def test_json_serializer(cleanup):
    serializer = JsonSerializer()
    data = {"name": "Milk", "calories": 60}
    serializer.save_to_file(data, "test.json")
    loaded_data = serializer.load_from_file("test.json")
    assert loaded_data == data

def test_customtext_serializer(cleanup):
    serializer = CustomTextSerializer()
    data = {"name": "Milk", "calories": "60"}
    serializer.save_to_file(data, "test.txt")
    loaded_data = serializer.load_from_file("test.txt")
    assert loaded_data == data

def test_invalid_customtext_data():
    serializer = CustomTextSerializer()
    with pytest.raises(ValueError):
        serializer.serialize([1, 2, 3], "test.txt")