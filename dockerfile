FROM python:3.11-slim AS base
WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc \
 && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 100 --retries 10 -r requirements.txt



# COPY . /app

EXPOSE 8080
ENV PYTHONUNBUFFERED=1 APP_ENV=production

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080","--reload", "--log-level", "info"]
