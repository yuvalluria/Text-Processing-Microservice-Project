import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
import sys
import os

# Add the parent directory to Python path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app

# Mock the gRPC client for testing
class MockGRPCClient:
    def __init__(self):
        self.connected = True
    
    async def connect(self):
        pass
    
    async def close(self):
        pass
    
    async def health_check(self):
        return True
    
    async def process_text(self, text):
        # Mock response
        mock_response = Mock()
        mock_response.summary = f"Summary of: {text[:50]}..."
        mock_response.sentiment = "neutral"
        mock_response.keywords = ["test", "mock", "keywords"]
        mock_response.original_length = len(text)
        mock_response.processed_length = len(mock_response.summary)
        return mock_response

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def mock_grpc_client(monkeypatch):
    """Mock the gRPC client"""
    mock_client = MockGRPCClient()
    
    # Replace the global grpc_client
    import main
    monkeypatch.setattr(main, 'grpc_client', mock_client)
    
    return mock_client

class TestFastAPIService:
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["status"] == "healthy"

    def test_stats_endpoint(self, client, mock_grpc_client):
        """Test stats endpoint"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "api_version" in data
        assert "available_endpoints" in data

    def test_summarize_valid_text(self, client, mock_grpc_client):
        """Test summarize endpoint with valid text"""
        test_text = "This is a test text for processing. It contains multiple sentences for testing."
        
        response = client.post(
            "/summarize",
            json={"text": test_text}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert "summary" in data["result"]
        assert "sentiment" in data["result"]
        assert "keywords" in data["result"]

    def test_summarize_empty_text(self, client, mock_grpc_client):
        """Test summarize endpoint with empty text"""
        response = client.post(
            "/summarize",
            json={"text": ""}
        )
        
        # Should return validation error for empty text
        assert response.status_code == 422

    def test_summarize_no_text_field(self, client, mock_grpc_client):
        """Test summarize endpoint without text field"""
        response = client.post(
            "/summarize",
            json={}
        )
        
        # Should return validation error
        assert response.status_code == 422

    def test_summarize_invalid_json(self, client, mock_grpc_client):
        """Test summarize endpoint with invalid JSON"""
        response = client.post(
            "/summarize",
            data="invalid json"
        )
        
        assert response.status_code == 422

class TestGRPCClient:
    @pytest.mark.asyncio
    async def test_grpc_client_health_check(self):
        """Test gRPC client health check"""
        client = MockGRPCClient()
        result = await client.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_grpc_client_process_text(self):
        """Test gRPC client text processing"""
        client = MockGRPCClient()
        result = await client.process_text("test text")
        
        assert result is not None
        assert hasattr(result, 'summary')
        assert hasattr(result, 'sentiment')
        assert hasattr(result, 'keywords')

if __name__ == '__main__':
    pytest.main([__file__])
