# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (Postgres, build tools)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run Gunicorn as the application server
# Replace `ecommerceapp.wsgi:application` with your Django project’s WSGI module
CMD ["gunicorn", "ecommerceapp.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
