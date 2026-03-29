# ---------- Build Stage ----------
FROM python:3.11-slim AS builder
WORKDIR /app
# Install build dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Runtime Stage ----------
FROM python:3.11-slim
WORKDIR /app
# Copy installed packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# Copy application code
COPY . .
# Expose FastAPI port
EXPOSE 8000
# Run with gunicorn and uvicorn workers
ENV PORT 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:${PORT}", "main:app"]
