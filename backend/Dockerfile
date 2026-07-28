FROM python:3.12-slim

# Create a non-root user — never run app processes as root
RUN groupadd --system appgroup && \
    useradd --system --gid appgroup --no-create-home appuser

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Transfer ownership to non-root user
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Run DB migrations then start the API server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
