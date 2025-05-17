from src.custom_serializer.serializer.serializer import Serializer

class JsonSerializer(Serializer):
    def serialize(self, data, filepath):
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        pairs = []
        for key, value in data.items():
            # Преобразуем значение в строку
            if isinstance(value, (int, float)):
                value_str = str(value)
            else:
                value_str = str(value).replace("|", "").replace("=", "")  # Избегаем конфликтов
            pairs.append(f"{key}={value_str}")
        return "|".join(pairs)

    def deserialize(self, content):
        if not content or not isinstance(content, str):
            raise ValueError("Content must be a non-empty string")

        result = {}
        pairs = content.split("|")
        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)  # Разделяем только первое вхождение =
                # Пробуем преобразовать в число, если возможно
                try:
                    if "." in value:
                        result[key] = float(value)
                    elif value.isdigit():
                        result[key] = int(value)
                    else:
                        result[key] = value
                except ValueError:
                    result[key] = value  # Оставляем как строку при ошибке
        return result