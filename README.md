Text Processing Microservices
A distributed system for text processing consisting of two microservices:

Processing Service (gRPC): Performs NLP tasks including summarization, sentiment analysis, and keyword extraction
Serving Service (FastAPI): HTTP API that forwards requests to the processing service

Features

Text Summarization: Extractive summarization based on sentence scoring
Sentiment Analysis: Positive/negative/neutral sentiment detection using TextBlob
Keyword Extraction: Top-N important words extraction using frequency analysis
Async/Await: Full async support for optimal performance
Docker Support: Containerized services with docker-compose
Health Checks: Built-in health monitoring for both services
Error Handling: Comprehensive error handling and logging

Architecture
Client Request → FastAPI (Port 8000) → gRPC Service (Port 50051) → Response
Quick Start with Docker
Prerequisites

Docker
Docker Compose

Run the System
bash# Clone and navigate to the project
cd PROJECT2

# Start both services
docker-compose up --build

# The services will be available at:
# - FastAPI: http://localhost:8000
# - gRPC: localhost:50051
Test the API
bash# Health check
curl http://localhost:8000/health

# Process text
curl -X POST "http://localhost:8000/summarize" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Artificial intelligence is revolutionizing the way we work and live. Machine learning algorithms can process vast amounts of data to find patterns and make predictions. Natural language processing allows computers to understand and generate human language. Deep learning neural networks have achieved remarkable success in image recognition, speech processing, and game playing. However, AI also raises important questions about job displacement, privacy, and ethical considerations that society must address."
     }'
Development Setup
Prerequisites

Python 3.11+
pip

Setup Processing Service
bashcd processing/processor

# Install dependencies
pip install -r requirements.txt

# Generate gRPC files
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. text_processor.proto

# Run the service
python server.py
Setup Serving Service
bashcd serving/app

# Install dependencies
pip install -r requirements.txt

# Copy generated gRPC files from processing service
cp ../../processing/processor/text_processor_pb2.py .
cp ../../processing/processor/text_processor_pb2_grpc.py .

# Run the service
uvicorn main:app --reload --host 0.0.0.0 --port 8000
API Documentation
Endpoints
GET /
Health check endpoint.
Response:
json{
  "message": "Text Processing API is running",
  "status": "healthy"
}
GET /health
Detailed health check including gRPC connection status.
Response:
json{
  "status": "healthy",
  "grpc_connection": "ok"
}
POST /summarize
Process text to get summary, sentiment analysis, and keywords.
Request Body:
json{
  "text": "Your text to process here..."
}
Response:
json{
  "success": true,
  "result": {
    "summary": "Extracted summary of the text...",
    "sentiment": "positive",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "original_length": 256,
    "processed_length": 128
  }
}
GET /stats
Get API statistics and status information.
Example Usage
Python Client Example
pythonimport requests

# Text to process
text = """
Artificial intelligence is transforming our world in unprecedented ways. 
From healthcare to transportation, AI systems are becoming integral to modern life. 
However, we must carefully consider the ethical implications of these technologies.
"""

# Send request
response = requests.post(
    "http://localhost:8000/summarize",
    json={"text": text}
)

result = response.json()
print(f"Summary: {result['result']['summary']}")
print(f"Sentiment: {result['result']['sentiment']}")
print(f"Keywords: {result['result']['keywords']}")
JavaScript Client Example
javascriptconst text = `
Artificial intelligence is transforming our world in unprecedented ways. 
From healthcare to transportation, AI systems are becoming integral to modern life. 
However, we must carefully consider the ethical implications of these technologies.
`;

fetch('http://localhost:8000/summarize', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ text })
})
.then(response => response.json())
.then(data => {
  console.log('Summary:', data.result.summary);
  console.log('Sentiment:', data.result.sentiment);
  console.log('Keywords:', data.result.keywords);
});
Testing
Run Tests
bash# Test processing service
cd processing/tests
python -m pytest test_processing.py -v

# Test serving service
cd serving/tests
python -m pytest test_client.py -v
Monitoring and Logs
View Logs
bash# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs processing
docker-compose logs serving

# Follow logs
docker-compose logs -f
Health Monitoring
Both services include health check endpoints that are monitored by Docker Compose:

Processing service: gRPC connectivity check
Serving service: HTTP health endpoint + gRPC connectivity check

Configuration
Environment Variables
Processing Service

PYTHONPATH: Python path configuration

Serving Service

PROCESSING_HOST: gRPC service hostname (default: localhost)
PROCESSING_PORT: gRPC service port (default: 50051)
PYTHONPATH: Python path configuration

Troubleshooting
Common Issues

gRPC Connection Failed

Ensure processing service is running on port 50051
Check Docker network configuration
Verify firewall settings


NLTK Data Download Issues

The processing service automatically downloads required NLTK data
In some environments, you may need to pre-download the data


Port Conflicts

Default ports: 8000 (FastAPI), 50051 (gRPC)
Modify docker-compose.yml to use different ports if needed



Debug Mode
bash# Run with debug logging
docker-compose up --build -e LOG_LEVEL=DEBUG
Project Structure
PROJECT2/
├── processing/
│   ├── processor/
│   │   ├── text_processor.proto
│   │   ├── server.py
│   │   └── requirements.txt
│   ├── tests/
│   └── Dockerfile
├── serving/
│   ├── app/
│   │   ├── main.py
│   │   ├── grpc_client.py
│   │   └── requirements.txt
│   ├── tests/
│   └── Dockerfile
├── docker-compose.yml
└── README.md
License
