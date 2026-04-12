FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Create data directory for SQLite persistence
RUN mkdir -p /data

# Set environment variable for data path
ENV DATABASE_PATH=/data/capybara.db

# Run the bot
CMD ["python", "main.py"]
