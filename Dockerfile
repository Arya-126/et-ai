# Fraud Network Intelligence + Citizen Fraud Shield — single-image deployment.
# Serves the unified platform SPA + the whole API on :8000.
#
#   docker build -t fraud-shield .
#   docker run -p 8000:8000 fraud-shield      # open http://localhost:8000

# ---- stage 1: build the React platform ----------------------------------
FROM node:20-slim AS frontend
WORKDIR /platform
COPY platform/package.json platform/package-lock.json* ./
RUN npm ci || npm install
COPY platform/ ./
RUN npm run build         # outputs /platform/dist

# ---- stage 2: python runtime --------------------------------------------
FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    PIP_DEFAULT_TIMEOUT=120 PIP_RETRIES=10 \
    GRAPH_BACKEND=networkx \
    OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    OLLAMA_MODEL=llama3.2:3b \
    CORS_ORIGINS=http://localhost:8000

# libgomp1 is needed by torch (OpenMP); opencv uses the -headless wheel (no GUI libs).
RUN apt-get update -o Acquire::Retries=10 \
 && apt-get install -y --no-install-recommends -o Acquire::Retries=10 libgomp1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# WITH_CNN=1 (default) installs torch + trains the currency CNN; WITH_CNN=0 builds
# a lean image where the scanner runs OpenCV features-only (no 200MB torch wheel).
#   docker build --build-arg WITH_CNN=0 -t fraud-shield:lite .
ARG WITH_CNN=1

# torch in its own layer so it stays cached across requirements.txt edits.
RUN if [ "$WITH_CNN" = "1" ]; then \
      pip install --no-cache-dir torch==2.12.1 torchvision==0.27.1 \
        --index-url https://download.pytorch.org/whl/cpu ; \
    fi
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
# bake demo data (+ the trained currency CNN when WITH_CNN=1) into the image
RUN python -m data.generate \
 && python -m cv.generate_notes \
 && if [ "$WITH_CNN" = "1" ]; then python -m cv.train ; fi

# built SPA from stage 1 -> /app/platform/dist (matches app.main._DIST)
COPY --from=frontend /platform/dist /app/platform/dist

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
