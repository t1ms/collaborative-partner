# ==============================================================================
# Google Cloud Run Container for Collaborative Thinking Partner
# ==============================================================================
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV PYTHONPATH=/app/src

WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY src/thinking_partner/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source code and sample data
COPY src /app/src
COPY data /app/data

# Expose Cloud Run default port
EXPOSE 8080

# Launch FastAPI web application on $PORT
CMD exec uvicorn thinking_partner.server:app --host 0.0.0.0 --port ${PORT}
