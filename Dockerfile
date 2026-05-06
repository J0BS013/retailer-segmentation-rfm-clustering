FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies first (Docker layer caching — rebuilds only if requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Default command: run the ETL pipeline
CMD ["python", "src/run_pipeline.py"]
