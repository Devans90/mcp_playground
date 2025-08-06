from __future__ import annotations
from typing import Optional, Dict
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

def setup_tracing(service_name: str):
    provider = TracerProvider()
    processor = SimpleSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)

def start_trace(tracer, span_name: str, attrs: Optional[Dict] = None):
    span = tracer.start_span(span_name)
    if attrs:
        for k, v in attrs.items(): span.set_attribute(k, v)
    return span
