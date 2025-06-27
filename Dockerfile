# Dockerfile for containerized deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for audio files
RUN mkdir -p static/audio

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000

# Command to run the application
CMD ["uvicorn", "api_backend:app", "--host", "0.0.0.0", "--port", "8000"]
