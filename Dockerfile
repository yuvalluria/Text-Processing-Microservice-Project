FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY processor/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir grpcio grpcio-tools nltk textblob

# Copy proto file and generate gRPC files
COPY processor/text_processor.proto .
RUN python -m grpc_tools.protoc \
    --proto_path=. \
    --python_out=. \
    --grpc_python_out=. \
    text_processor.proto

# Copy application code
COPY processor/ .

# Expose gRPC port
EXPOSE 50051

# Run the server
CMD ["python", "server.py"]