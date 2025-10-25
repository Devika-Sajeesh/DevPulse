# backend/Dockerfile
FROM python:3.11-slim

# install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cloc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# set workdir
WORKDIR /app

# copy requirements first for caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# copy code
COPY . /app

# expose port
EXPOSE 8000

# run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
