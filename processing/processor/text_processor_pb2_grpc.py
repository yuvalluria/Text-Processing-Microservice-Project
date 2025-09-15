"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import text_processor_pb2 as text__processor__pb2

class TextProcessorStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ProcessText = channel.unary_unary(
                '/text_processor.TextProcessor/ProcessText',
                request_serializer=text__processor__pb2.ProcessTextRequest.SerializeToString,
                response_deserializer=text__processor__pb2.ProcessTextResponse.FromString,
                )

class TextProcessorServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ProcessText(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_TextProcessorServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ProcessText': grpc.unary_unary_rpc_method_handler(
                    servicer.ProcessText,
                    request_deserializer=text__processor__pb2.ProcessTextRequest.FromString,
                    response_serializer=text__processor__pb2.ProcessTextResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'text_processor.TextProcessor', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

class TextProcessor(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ProcessText(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/text_processor.TextProcessor/ProcessText',
            text__processor__pb2.ProcessTextRequest.SerializeToString,
            text__processor__pb2.ProcessTextResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
