from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging
from typing import List
import nltk
from textblob import TextBlob
from collections import Counter
import re

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Text Processing API",
    description="A microservice for text processing with summarization, sentiment analysis, and keyword extraction",
    version="1.0.0"
)

# Pydantic models
class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to process")

class ProcessingResult(BaseModel):
    summary: str
    sentiment: str
    keywords: List[str]
    original_length: int
    processed_length: int

class SummarizeResponse(BaseModel):
    success: bool
    result: ProcessingResult = None
    error: str = None

# Text processing class
class TextProcessor:
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            # Fallback if NLTK stopwords fail
            self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this', 'that', 'these', 'those'}
        logger.info("TextProcessor initialized successfully")

    def extractive_summarization(self, text, num_sentences=2):
        """Simple extractive summarization based on sentence scoring"""
        try:
            sentences = sent_tokenize(text)
            
            if len(sentences) <= num_sentences:
                return text
            
            # Score sentences based on word frequency
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalnum() and word not in self.stop_words]
            
            word_freq = Counter(words)
            
            sentence_scores = {}
            for sentence in sentences:
                sentence_words = word_tokenize(sentence.lower())
                sentence_words = [word for word in sentence_words if word.isalnum()]
                
                score = 0
                word_count = 0
                for word in sentence_words:
                    if word in word_freq:
                        score += word_freq[word]
                        word_count += 1
                
                if word_count > 0:
                    sentence_scores[sentence] = score / word_count
            
            # Get top sentences
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
            summary_sentences = [sent[0] for sent in top_sentences[:num_sentences]]
            
            # Maintain original order
            summary = []
            for sentence in sentences:
                if sentence in summary_sentences:
                    summary.append(sentence)
            
            return ' '.join(summary)
            
        except Exception as e:
            logger.error(f"Error in summarization: {str(e)}")
            # Fallback: return first few sentences
            sentences = text.split('.')
            return '. '.join(sentences[:2]) + '.' if len(sentences) > 2 else text

    def analyze_sentiment(self, text):
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                return "positive"
            elif polarity < -0.1:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            # Fallback: simple keyword-based sentiment
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'best', 'awesome']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'disgusting', 'annoying', 'frustrating']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"

    def extract_keywords(self, text, top_n=5):
        """Extract keywords using simple frequency analysis"""
        try:
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalnum() and len(word) > 2 and word not in self.stop_words]
            
            word_freq = Counter(words)
            top_words = word_freq.most_common(top_n)
            
            return [word for word, _ in top_words]
            
        except Exception as e:
            logger.error(f"Error in keyword extraction: {str(e)}")
            # Fallback: simple regex-based extraction
            words = re.findall(r'\b\w{3,}\b', text.lower())
            word_freq = Counter(words)
            common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
            filtered_words = {word: count for word, count in word_freq.items() if word not in common_words}
            top_words = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:top_n]
            return [word for word, _ in top_words]

# Initialize processor
processor = TextProcessor()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Text Processing API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "text-processing-api",
        "version": "1.0.0",
        "features": ["summarization", "sentiment_analysis", "keyword_extraction"]
    }

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: TextRequest):
    """
    Process text to get summary, sentiment analysis, and keywords
    """
    try:
        logger.info(f"Processing text with {len(request.text)} characters")
        
        # Process text using internal methods
        summary = processor.extractive_summarization(request.text)
        sentiment = processor.analyze_sentiment(request.text)
        keywords = processor.extract_keywords(request.text)
        
        result = ProcessingResult(
            summary=summary,
            sentiment=sentiment,
            keywords=keywords,
            original_length=len(request.text),
            processed_length=len(summary)
        )
        
        logger.info("Text processing completed successfully")
        return SummarizeResponse(success=True, result=result)
        
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        return SummarizeResponse(
            success=False, 
            error=f"Processing error: {str(e)}"
        )

@app.get("/stats")
async def get_stats():
    """Get API statistics"""
    return {
        "api_version": "1.0.0",
        "service_name": "text-processing-api",
        "available_endpoints": ["/", "/health", "/summarize", "/stats"],
        "processing_features": [
            "extractive_summarization",
            "sentiment_analysis", 
            "keyword_extraction"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)