FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8105 \
    WORKERS=2

WORKDIR /app

# System dependencies (add if docx libs require more later)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libxml2 libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure runtime directories exist (mounted volume will merge)
RUN mkdir -p download/documents download/pdfs

EXPOSE 8105

# Allow overriding port/workers via env when starting container
CMD ["sh","-c","uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS} --proxy-headers"]
