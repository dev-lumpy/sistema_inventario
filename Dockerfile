# 1. Fijar la versión exacta de Python que usas (3.11.9)
FROM python:3.11.9-slim

WORKDIR /app

# 2. Copiar e instalar dependencias exactas primero
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiar el resto del código
COPY . .

# 4. Usuario no-root (opcional pero recomendado)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# 4. Ajusta este CMD a tu framework (ej. FastAPI/Uvicorn)
CMD ["", "manage.py", "--host", "-1.0.0.0", "--port", "8000"]
