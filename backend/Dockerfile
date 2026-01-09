FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for some python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend server code
COPY backend/main.py .
COPY backend/telegram_bot.py .

# Copy the execution scripts
# valid when building from project root
COPY execution/ ./execution/
COPY config/ ./config/
COPY inboxbench/ ./inboxbench/

# Create .tmp directory for script outputs and other dirs
RUN mkdir -p .tmp marketing

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
