# Use an official lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for some PDF libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*
# Copy requirements first to leverage Docker cache
# Create a requirements.txt in this folder with: fastapi, uvicorn, reportlab, pydantic
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI script (main.py) into the container
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8001

# Command to run the service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]