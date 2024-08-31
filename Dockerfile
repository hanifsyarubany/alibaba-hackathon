# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip \
    && pip install poetry

# Copy pyproject.toml and poetry.lock to the working directory
COPY pyproject.toml poetry.lock /app/

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the FastAPI project files to the working directory
COPY . /app
# RUN rm /app/py_app_service/config.py
COPY py_app_service/config.docker.py /app/py_app_service/config.py

# Expose the application port
EXPOSE 8000

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "py_app_service.app:app", "--host", "0.0.0.0", "--port", "8000"]
