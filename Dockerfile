FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build and runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip & install requirements
RUN pip install --no-cache-dir uv

# Copy pyproject.toml and install dependencies with uv
COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml

# Install Gunicorn explicitly
RUN uv pip install --system --no-cache gunicorn>=22.0.0

COPY gunicorn.conf.py /app/gunicorn.conf.py

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh

# Copy only necessary app files
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/mediafiles

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]