# --------- Stage 1: Builder (Install dependencies) ---------
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y build-essential gcc libpq-dev --no-install-recommends

# Copy only requirements to leverage Docker cache
COPY requirements.txt .

# Install dependencies in a separate directory
RUN pip install --upgrade pip
RUN pip install --prefix=/install -r requirements.txt

# --------- Stage 2: Final image ---------
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Default command for running FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
