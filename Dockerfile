# ---------- BUILDER ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install ONLY what is needed to build wheels
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt



# ---------- RUNTIME ----------
FROM python:3.11-slim

WORKDIR /app

# Install minimal runtime libs (VERY important)
RUN apt-get update && apt-get install -y \
    libstdc++6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy virtualenv
COPY --from=builder /opt/venv /opt/venv

# Copy app LAST (better caching)
COPY . .

EXPOSE 8000

# ⭐ Use uvloop + httptools (MUCH faster)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--http", "httptools"]
