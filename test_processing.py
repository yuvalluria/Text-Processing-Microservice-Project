import pytest
import grpc
from grpc_testing import server_from_dictionary, strict_real_time
import sys
import os

# Add the parent directory to Python path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'processor'))

import text_processor_pb2
import text_processor_pb2_grpc
from server import TextProcessorService

class TestTextProcessorService:
    def setup_method(self):
        """Setup test fixtures"""
        self.service = TextProcessorService()
        
        # Create test server
        servicers = {
            text_processor_pb2.DESCRIPTOR.services_by_name['TextProcessor']: self.service
        }
        self.test_server = server_from_dictionary(servicers, strict_real_time())

    def test_basic_text_processing(self):
        """Test basic text processing functionality"""
        text = "This is a test sentence. This test sentence contains multiple words for processing."
        
        request = text_processor_pb2.ProcessTextRequest(text=text)
        
        # Call the method directly for unit testing
        response = self.service._extractive_summarization(text)
        sentiment = self.service._analyze_sentiment(text)
        keywords = self.service._extract_keywords(text)
        
        assert len(response) > 0
        assert sentiment in ['positive', 'negative', 'neutral']
        assert isinstance(keywords, list)

    def test_empty_text(self):
        """Test handling of empty text"""
        response = self.service._extractive_summarization("")
        assert response == ""
        
        sentiment = self.service._analyze_sentiment("")
        assert sentiment == "neutral"
        
        keywords = self.service._extract_keywords("")
        assert keywords == []

    def test_sentiment_analysis(self):
        """Test sentiment analysis with different texts"""
        positive_text = "I love this amazing product! It's fantastic and wonderful!"
        negative_text = "This is terrible and awful. I hate it completely."
        neutral_text = "This is a chair. The chair is brown."
        
        assert self.service._analyze_sentiment(positive_text) == "positive"
        assert self.service._analyze_sentiment(negative_text) == "negative"
        assert self.service._analyze_sentiment(neutral_text) == "neutral"

    def test_keyword_extraction(self):
        """Test keyword extraction"""
        text = "machine learning artificial intelligence data science python programming"
        keywords = self.service._extract_keywords(text, top_n=3)
        
        assert len(keywords) <= 3
        assert isinstance(keywords, list)
        assert all(isinstance(keyword, str) for keyword in keywords)

    def test_summarization(self):
        """Test text summarization"""
        text = """
        Artificial intelligence is a fascinating field. 
        It involves creating machines that can think and learn. 
        Machine learning is a subset of artificial intelligence. 
        Deep learning uses neural networks with multiple layers.
        """
        
        summary = self.service._extractive_summarization(text, num_sentences=2)
        
        assert len(summary) > 0
        assert len(summary) < len(text)
        assert isinstance(summary, str)

if __name__ == '__main__':
    pytest.main([__file__])