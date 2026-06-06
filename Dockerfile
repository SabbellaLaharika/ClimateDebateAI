FROM python:3.10-slim

WORKDIR /app

# Optimize Python execution environment & CPU threads
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    UV_LINK_MODE=copy \
    HF_HOME="/app/.cache/huggingface"

# Install curl (used for the HEALTHCHECK)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install requirements using uv (cache mount enabled for local docker speedups)
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Create dedicated non-root user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /bin/bash appuser && \
    mkdir -p $HF_HOME && chown -R appuser:appgroup /app

# Run as non-root user
USER appuser

# Pre-download model into cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code with non-root ownership
COPY --chown=appuser:appgroup . .

# Expose port and configure service healthcheck
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
