# ── Stage: runtime ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

# ── System dependencies ─────────────────────────────────────────────────────────
# libreoffice-writer  → DOCX/ODT support
# libreoffice-calc    → optional spreadsheet support
# fonts-liberation    → MS-compatible fonts (Times, Arial, Courier equivalents)
# fonts-freefont-ttf  → broad Unicode / Arabic coverage
# libglib2.0-0        → required runtime lib for soffice
RUN apt-get update && apt-get install -y --no-install-recommends \
        libreoffice \
        libreoffice-writer \
        libreoffice-calc \
        fonts-liberation \
        fonts-freefont-ttf \
        libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ───────────────────────────────────────────────────────────
WORKDIR /app

# ── Python dependencies ─────────────────────────────────────────────────────────
# Copy requirements first to leverage Docker layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application source ──────────────────────────────────────────────────────────
COPY . .

# ── Runtime directories for generated files ─────────────────────────────────────
RUN mkdir -p download/documents download/pdfs

# Default port — override via .env
ENV PORT=8105
ENV HOME=/tmp

# ── Expose API port (runtime value of $PORT) ────────────────────────────────────
EXPOSE ${PORT}

# ── Start the API — reads $PORT at container start time ─────────────────────────
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT}"
