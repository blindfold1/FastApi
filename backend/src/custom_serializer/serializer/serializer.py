from abc import ABC, abstractmethod
import os

class Serializer(ABC):
    @abstractmethod
    def serialize(self, data, filepath):
        pass

    @abstractmethod
    def deserialize(self, content):
        pass

    def save_to_file(self, data, filepath):
        serialized = self.serialize(data, filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            for char in serialized:
                f.write(char)  # Ручная запись побайтово

    def load_from_file(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File {filepath} not found")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = ""
            for line in f:  # Читаем построчно
                content += line.strip()
            return self.deserialize(content)