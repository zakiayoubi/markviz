FROM python:3.11-slim

WORKDIR /app
COPY . .

# Install everything you need
RUN pip install fastapi uvicorn httpx python-dotenv pytest

# This tells FastAPI to automatically read your .env file
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]