# ---------- Build Stage ----------
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Runtime Stage ----------
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (required by pytesseract and CV/ML libraries)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# Copy application code from current build context
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Robust Environment Configuration
ENV PORT=8000
ENV PYTHONPATH=/app
# Long timeout (120s) to allow heavy libraries (torch, shap) to load on limited hardware
ENV GUNICORN_CMD_ARGS="--timeout 120 --workers 1 --threads 4"

# Use gunicorn with uvicorn workers for production
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:${PORT}", "main:app"]
