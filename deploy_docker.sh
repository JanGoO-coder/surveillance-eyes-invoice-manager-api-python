#!/usr/bin/env bash
set -euo pipefail

# Simple deployment helper for the FastAPI invoice service (Option 2 containerization)

IMAGE_NAME="invoice-api"
CONTAINER_NAME="invoice-api"
HOST_PORT="8105"
NETWORK_NAME="web"
WORKERS="2"
REBUILD=0
ORIGINS="" # e.g. https://invoice.jangoo.org,https://other.domain

usage() {
  cat <<EOF
Usage: $0 [options]
  -p <port>        Host port to expose (default: 8105)
  -n <network>     Docker network to attach/create (default: web)
  -i <image>       Image name (default: invoice-api)
  -c <container>   Container name (default: invoice-api)
  -w <workers>     Uvicorn workers (default: 2)
  -o <origins>     Comma-separated CORS allowed origins (default: unset => *)
  -r               Force rebuild even if image exists
  -h               Show this help
Environment overrides: PORT, WORKERS, ALLOWED_ORIGINS
Examples:
  ./deploy_docker.sh -p 8200
  PORT=9000 WORKERS=4 ./deploy_docker.sh
  ./deploy_docker.sh -o https://invoice.jangoo.org
EOF
}

while getopts ":p:n:i:c:w:o:rh" opt; do
  case "$opt" in
    p) HOST_PORT="$OPTARG" ;;
    n) NETWORK_NAME="$OPTARG" ;;
    i) IMAGE_NAME="$OPTARG" ;;
    c) CONTAINER_NAME="$OPTARG" ;;
    w) WORKERS="$OPTARG" ;;
    o) ORIGINS="$OPTARG" ;;
    r) REBUILD=1 ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

echo "[+] Settings:" \
  "IMAGE=$IMAGE_NAME" \
  "CONTAINER=$CONTAINER_NAME" \
  "PORT=$HOST_PORT" \
  "NETWORK=$NETWORK_NAME" \
  "WORKERS=$WORKERS" \
  "ORIGINS=${ORIGINS:-*}"

# Create network if missing
if ! docker network ls --format '{{.Name}}' | grep -q "^${NETWORK_NAME}$"; then
  echo "[+] Creating network ${NETWORK_NAME}"
  docker network create "$NETWORK_NAME"
fi

# Build image (conditional)
if ! docker image inspect "$IMAGE_NAME:latest" >/dev/null 2>&1 || [ "$REBUILD" -eq 1 ]; then
  echo "[+] Building image ${IMAGE_NAME}"
  docker build -t "$IMAGE_NAME:latest" .
else
  echo "[=] Image exists (use -r to force rebuild)"
fi

# Stop & remove existing container
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "[+] Removing existing container ${CONTAINER_NAME}"
  docker rm -f "$CONTAINER_NAME" >/dev/null
fi

# Ensure host data directories exist for persistence
mkdir -p download/documents download/pdfs

echo "[+] Starting container ${CONTAINER_NAME} on port ${HOST_PORT}"
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  --network "$NETWORK_NAME" \
  -p "${HOST_PORT}:8105" \
  -e PORT=8105 \
  -e WORKERS="$WORKERS" \
  ${ORIGINS:+-e ALLOWED_ORIGINS="$ORIGINS"} \
  -v "$(pwd)/download:/app/download" \
  "$IMAGE_NAME:latest"

echo "[+] Logs (first 5s)"
sleep 2
docker logs --tail 50 "$CONTAINER_NAME" || true

echo "[✓] Deployed. Test: curl http://localhost:${HOST_PORT}/ | jq .  (jq optional)"
