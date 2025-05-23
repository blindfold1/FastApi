FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/src /app/backend/src
COPY frontend/src /app/frontend/src

ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8000"]