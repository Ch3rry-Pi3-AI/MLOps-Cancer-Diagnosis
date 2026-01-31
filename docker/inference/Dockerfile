FROM python:3.10-slim

WORKDIR /app

COPY docker/inference/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src

# Azure ML expects the scoring script path via AZUREML_ENTRY_SCRIPT
ENV AZUREML_ENTRY_SCRIPT=src/inference/score.py
