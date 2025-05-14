FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for queue data persistence
RUN mkdir -p /app/queue_data && chmod 777 /app/queue_data

# Expose the port
EXPOSE 7500

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV QUEUE_CONFIG_PATH=/app/config.json

# Command to run the application
CMD ["python", "-m", "app.main"]
