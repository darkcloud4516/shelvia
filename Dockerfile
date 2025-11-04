FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Sistem bağımlılıkları: derleyiciler, libpq ve python başlıkları
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    python3-dev \
    pkg-config \
    ca-certificates \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pip, setuptools, wheel güncelle
RUN python -m pip install --upgrade pip setuptools wheel

# Bağımlılıkları kopyala ve kur
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Uygulamayı kopyala
COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

