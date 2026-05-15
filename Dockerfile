FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app
COPY pyproject.toml README.md /app/
RUN pip install ".[test]"
COPY . /app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
