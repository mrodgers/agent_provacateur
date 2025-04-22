FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data/vectors

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8083
ENV VECTOR_DB_TYPE=faiss
ENV VECTOR_DB_PATH=/app/data/vectors/faiss
ENV LOG_LEVEL=info

# Expose the port
EXPOSE 8083

# Run the server
CMD ["python", "-m", "graphrag_mcp_py.src"]