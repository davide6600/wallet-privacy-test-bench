FROM python:3.13-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 50001

CMD ["python", "-m", "harness.observer_proxy"]
