FROM python:3.12-slim-bookworm

WORKDIR /app

COPY /app .

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["python", "-m", "ETL.pipeline"]