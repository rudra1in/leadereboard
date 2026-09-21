# --- Build Stage ---
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# 1. Copy the pyproject.toml from registration-service to download base dependencies
COPY registration-service/pyproject.toml .
RUN uv pip install --system -e .
RUN pip install --upgrade pip build 

# 2. Copy and install your common shared Kafka package
COPY gamex-kafka-template/ ./gamex-kafka-template/ 
RUN pip install ./gamex-kafka-template 

# 3. Copy and compile the registration service local project configuration
COPY registration-service/ ./registration-service/ 
WORKDIR /app/registration-service 
RUN pip install .


# --- Runtime Stage ---
FROM python:3.13-slim

WORKDIR /app

# Copy python packages and executable tools compiled in build stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# FIX: Copy the CONTENTS of the registration-service folder directly into /app
# This drops the "registration-service/" nesting folder layout. 
# Your container directory now contains: app/, pyproject.toml, etc.
COPY registration-service/ .

# Setup non-root execution permissions
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check endpoint routing
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

EXPOSE 8000

# Executing Uvicorn (Will now perfectly find /app/app/main.py)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
