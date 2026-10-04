FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PORT=8000

WORKDIR /app

# Install dependencies directly into system Python (no venv)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root system user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/false -M -d /app appuser

# Copy application source code and set ownership
COPY --chown=appuser:appgroup src/ /app/src/

# Switch to non-root user
USER appuser

# Expose HTTP port
EXPOSE 8000

# Health check using Python standard library (no curl/wget dependency required)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)" || exit 1

# Exec form ensures proper SIGTERM / SIGINT signal forwarding for graceful shutdown
CMD ["uvicorn", "cv_analyzer.main:app", "--host", "0.0.0.0", "--port", "8000"]
