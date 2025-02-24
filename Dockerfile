FROM python:3.11-slim

WORKDIR /app

COPY ./requirements/dev.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

COPY . .
