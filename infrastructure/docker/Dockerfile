# Match the Python version used for the local checks and CI.
FROM python:3.12-slim

WORKDIR /app

# Install dependencies before copying code so Docker can reuse this layer.
COPY backend/requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY backend/ruff.toml ./
COPY backend/app/ ./app/
COPY backend/tests/ ./tests/

# Windows-mounted WSL checkouts can mark Python source files executable.
RUN find app tests -type f -name '*.py' -exec chmod a-x {} +

# Use Cloud Run's PORT when supplied, or port 8000 for local development.
CMD ["sh", "-c", "exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
