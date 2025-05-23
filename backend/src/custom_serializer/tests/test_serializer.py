import pytest
import os
# Adjust imports to absolute paths from the project root
from backend.src.custom_serializer.formats.json_serializer import JsonSerializer


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

