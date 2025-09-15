import grpc
from concurrent import futures
import logging
import asyncio
from grpc import aio
import nltk
from textblob import TextBlob
from collections import Counter
import re
import sys
import os

# Import the generated gRPC files
import text_processor_pb2
import text_processor_pb2_grpc

# Download required NLTK data
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

class TextProcessorService(text_processor_pb2_grpc.TextProcessorServicer):
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        logger.info("TextProcessorService initialized")

    async def ProcessText(self, request, context):
        """Process text with summarization and sentiment analysis"""
        try:
            logger.info(f"Processing text request with {len(request.text)} characters")
            
            if not request.text.strip():
                logger.warning("Empty text received")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Text cannot be empty")
                return text_processor_pb2.ProcessTextResponse()

            # Perform text processing
            summary = self._extractive_summarization(request.text)
            sentiment = self._analyze_sentiment(request.text)
            keywords = self._extract_keywords(request.text, top_n=5)
            
            # Create response
            response = text_processor_pb2.ProcessTextResponse(
                summary=summary,
                sentiment=sentiment,
                keywords=keywords,
                original_length=len(request.text),
                processed_length=len(summary)
            )
            
            logger.info("Text processing completed successfully")
            return response

        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Processing error: {str(e)}")
            return text_processor_pb2.ProcessTextResponse()

    def _extractive_summarization(self, text, num_sentences=2):
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
            return text[:200] + "..." if len(text) > 200 else text

    def _analyze_sentiment(self, text):
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
            return "neutral"

    def _extract_keywords(self, text, top_n=5):
        """Extract keywords using simple frequency analysis"""
        try:
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalnum() and len(word) > 2 and word not in self.stop_words]
            
            word_freq = Counter(words)
            top_words = word_freq.most_common(top_n)
            
            return [word for word, _ in top_words]
            
        except Exception as e:
            logger.error(f"Error in keyword extraction: {str(e)}")
            return []

async def serve():
    """Start the gRPC server"""
    server = aio.server(futures.ThreadPoolExecutor(max_workers=10))
    text_processor_pb2_grpc.add_TextProcessorServicer_to_server(
        TextProcessorService(), server)
    
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting gRPC server on {listen_addr}")
    await server.start()
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server")
        await server.stop(0)

if __name__ == '__main__':
    asyncio.run(serve())
