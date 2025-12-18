# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create staticfiles directory
RUN mkdir -p /app/staticfiles

# Ensure startup script is executable
RUN chmod +x /app/scripts/start.sh

# Collect static files (if database fails, continue anyway)
RUN ENVIRONMENT=development python manage.py collectstatic --noinput --clear 2>/dev/null || true

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run startup script that applies migrations then starts gunicorn
CMD ["/app/scripts/start.sh"]
