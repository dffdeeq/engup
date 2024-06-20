FROM python:3.11-slim

WORKDIR /app

COPY ./requirements/dev.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip \
    && apt-get update \
    && apt-get install gcc -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .
