FROM python:3.9.24-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
CMD ["python", "-m", "ETL.pipeline"]