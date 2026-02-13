# ---------- Stage 1: builder ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# System deps (psycopg, etc.)
RUN apt-get update && apt-get install -y \
    build-essential gcc libpq-dev \
    --no-install-recommends

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt


# ---------- Stage 2: production ----------
FROM python:3.11-slim

WORKDIR /app

# Copy python deps
COPY --from=builder /install /usr/local

# Copy app source
COPY . .

# Optional documentation only
EXPOSE 8000

# --------- PRODUCTION CMD ----------
# Uses Render / cloud injected $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
