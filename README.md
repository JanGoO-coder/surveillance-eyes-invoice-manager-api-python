# Surveillance Eyes — Invoice Manager API

A **FastAPI** service that generates `.docx` invoices from Word templates and converts them to **PDF** using **LibreOffice headless** — fully containerised for VPS deployment.

---

## 🚀 Quick Start (Docker)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd surveillance-eyes-invoice-manager-api-python
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env if you need a different host port (default: 8000)
```

### 3. Build & run

```bash
docker compose up -d --build
```

The API will be available at **`http://<your-vps-ip>:8000`**

### 4. Interactive docs

| UI | URL |
|---|---|
| Swagger | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |

---

## 🛑 Stop / Restart

```bash
docker compose down          # Stop and remove container
docker compose up -d         # Start (without rebuilding)
docker compose up -d --build # Rebuild image and start
```

---

## 📁 File Persistence

Generated files are stored in `./download/` on the **host** (bind-mounted into the container at `/app/download`). They survive container restarts and rebuilds.

```
download/
├── templates/   ← .docx templates (checked into git)
├── documents/   ← generated .docx files (runtime)
└── pdfs/        ← generated .pdf files (runtime)
```

---

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Host port the API is exposed on |

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/generate/invoice/{filename}` | Generate DOCX + PDF invoice |
| `GET` | `/download/documents/{filename}` | Download a generated DOCX |
| `GET` | `/download/pdfs/{filename}` | Download a generated PDF |
| `GET` | `/list/documents` | List all generated documents |
| `GET` | `/list/pdfs` | List all generated PDFs |
| `GET` | `/list/templates` | List available templates |
| `DELETE` | `/delete/documents` | Delete all generated documents |
| `DELETE` | `/delete/pdfs` | Delete all generated PDFs |

### Example request — generate invoice

```bash
curl -X POST "http://localhost:8000/generate/invoice/client-abc" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice": {
      "id": "INV-001",
      "date": "2026-02-26",
      "title": "Security Services",
      "description": "Monthly surveillance package",
      "address": "123 Main St, Karachi",
      "total": 15000,
      "products": [
        { "id": "p1", "name": "Camera Installation", "quantity": 3, "price": 5000 }
      ]
    },
    "template": "surveillance_eyes_invoice_template.docx"
  }'
```

---

## 🖥️ VPS Deployment — Nginx Reverse Proxy (optional)

If you want to serve the API on port 80 / 443 behind Nginx:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }
}
```

Then secure with Certbot:

```bash
sudo certbot --nginx -d api.yourdomain.com
```

---

## 🏗️ Project Structure

```
.
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── requirements.txt
├── main.py               ← FastAPI application
├── models/
│   └── init.py           ← Pydantic models
└── download/
    └── templates/        ← Invoice .docx templates
```
