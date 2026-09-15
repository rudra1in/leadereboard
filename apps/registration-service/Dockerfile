# --- Build Stage ---
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv for faster dependency installation
RUN pip install --no-cache-dir uv

# Copy dependency specifications
COPY pyproject.toml .

# Install dependencies into the builder system environment
RUN uv pip install --system -r pyproject.toml

# --- Runtime Stage ---
FROM python:3.13-slim

WORKDIR /app

# 1. Copy the Python site-packages (Fixed path to match 3.13 -> 3.13)
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# 2. Copy the executable binaries (This makes 'uvicorn' accessible!)
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
