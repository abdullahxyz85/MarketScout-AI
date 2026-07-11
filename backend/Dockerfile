FROM python:3.11-slim

WORKDIR /app

# Install deps as root before switching to non-root user
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=120 --retries=5 -r requirements.txt

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser

COPY . .
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
