# Step 1: Use an official Python base image
FROM python:3.13.5-alpine3.22

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /usr/src/nuages-api

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Start the app using gunicorn with uvicorn workers
CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--reload", "nuages-api"]