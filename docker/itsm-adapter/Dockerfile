FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# Copy source code
COPY src/adapters/itsm/ ./src/adapters/itsm/

# Expose port
EXPOSE 9020

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9020/health')" || exit 1

# Run the application
CMD ["python", "src/adapters/itsm/main.py"]