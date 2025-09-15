import grpc
import asyncio
import logging
import os
from typing import Optional

# Import the generated gRPC files
import text_processor_pb2
import text_processor_pb2_grpc

logger = logging.getLogger(__name__)

class GRPCClient:
    def __init__(self, host: str = None, port: int = None):
        self.host = host or os.getenv('PROCESSING_HOST', 'localhost')
        self.port = port or int(os.getenv('PROCESSING_PORT', '50051'))
        self.channel = None
        self.stub = None
        
    async def connect(self):
        """Establish connection to gRPC server"""
        try:
            self.channel = grpc.aio.insecure_channel(f'{self.host}:{self.port}')
            self.stub = text_processor_pb2_grpc.TextProcessorStub(self.channel)
            logger.info(f"Connected to gRPC server at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to gRPC server: {str(e)}")
            raise

    async def close(self):
        """Close gRPC connection"""
        if self.channel:
            await self.channel.close()
            logger.info("gRPC channel closed")

    async def health_check(self) -> bool:
        """Check if gRPC server is healthy"""
        try:
            if not self.stub:
                return False
            
            # Send a simple request to check connectivity
            request = text_processor_pb2.ProcessTextRequest(text="health check")
            await asyncio.wait_for(self.stub.ProcessText(request), timeout=5.0)
            return True
        except Exception as e:
            logger.warning(f"gRPC health check failed: {str(e)}")
            return False

    async def process_text(self, text: str) -> Optional[text_processor_pb2.ProcessTextResponse]:
        """Send text to processing service"""
        try:
            if not self.stub:
                logger.error("gRPC stub not initialized")
                return None
                
            request = text_processor_pb2.ProcessTextRequest(text=text)
            
            # Add timeout for the request
            response = await asyncio.wait_for(
                self.stub.ProcessText(request), 
                timeout=30.0
            )
            
            logger.info("Successfully processed text via gRPC")
            return response
            
        except asyncio.TimeoutError:
            logger.error("gRPC request timed out")
            return None
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in gRPC call: {str(e)}")
            return None
