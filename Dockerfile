# Stage 1: Build & Layer base runtime
FROM python:3.11-slim

# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout/stderr streams
ENV PYTHONUNBUFFERED=1

# Establish execution workspace inside container system
WORKDIR /app

# NEW: Install Linux system dependencies for PDF generation (Cairo)
RUN apt-get update && apt-get install -y \
    pkg-config \
    libcairo2-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements to leverage Docker build layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . /app/

# Expose default binding port for documentation purposes
EXPOSE 8000

# Run system migrations, compress static configurations, and bind application worker engine
CMD sh -c "python manage.py collectstatic --noinput --clear && python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:8000"