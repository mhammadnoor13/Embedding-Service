FROM python:3.11-slim AS base
WORKDIR /app

# System deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc \
 && rm -rf /var/lib/apt/lists/*

 # show progress bars and info logs from transformers/hf_hub
 ENV HF_HUB_ENABLE_PROGRESS_BARS=true  
 ENV TRANSFORMERS_VERBOSITY=info
# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 100 --retries 10 -r requirements.txt



# Copy application code
COPY . /app

EXPOSE 8000
ENV PYTHONUNBUFFERED=1 APP_ENV=production

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
