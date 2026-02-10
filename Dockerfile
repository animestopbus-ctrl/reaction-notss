# ---------- BUILDER ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build deps ONLY here
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual env (MUCH cleaner than copying site-packages)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt



# ---------- RUNTIME ----------
FROM python:3.11-slim

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy ONLY the virtualenv (smaller + faster)
COPY --from=builder /opt/venv /opt/venv

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:main_app", "--host", "0.0.0.0", "--port", "8000"]
