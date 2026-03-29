# ---------- Build Stage ----------
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
# We use the CPU-specific PyTorch index to avoid massive CUDA libraries (GBs of saved space/RAM)
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# ---------- Runtime Stage ----------
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (required by pytesseract and CV/ML libraries)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
# Copy application code from current build context
COPY . .

# Expose FastAPI port (hint for the platform)
EXPOSE 8000

# Robust Environment Configuration
ENV PORT=8000
ENV PYTHONPATH=/app
# Long timeout (120s) and minimal worker setup (1 worker / 1 thread) to avoid OOM on Render Free tier
ENV GUNICORN_CMD_ARGS="--timeout 120 --workers 1 --threads 1 --worker-tmp-dir /dev/shm"

# Shell form of CMD to ensure ${PORT} is correctly expanded by the shell at runtime
CMD gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT} main:app
