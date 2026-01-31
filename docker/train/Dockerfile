FROM python:3.10-slim

WORKDIR /app

COPY docker/train/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src
