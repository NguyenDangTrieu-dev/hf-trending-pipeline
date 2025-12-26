import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def setup_tracer():
    provider = TracerProvider(
        resource=Resource.create({
            "service.name": "hf-trending-groq"
        })
    )

    exporter = OTLPSpanExporter(
        endpoint="https://otlp.uptrace.dev/v1/traces",
        headers={"uptrace-dsn": os.environ["UPTRACE_DSN"]}
    )

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    return trace.get_tracer(__name__)
