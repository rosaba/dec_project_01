## using python base image
From python:3.10-slim

## Setting up working directory in container
Workdir /app

## Copy dependencies list first (for caching)
Copy requirements.txt .

# Install Dependecies

Run pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the entire project to work dir in container

Copy . /app

# Command to run ETL

CMD ["python", "ETL/pipeline.py"]