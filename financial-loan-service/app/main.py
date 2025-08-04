from fastapi import FastAPI
from fastapi import Request
from schemas.healthcheck import HealthCheck
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from api.v1 import api_v1

load_dotenv()


## TRACE IMPORT
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.propagators.cloud_trace_propagator import CloudTraceFormatPropagator



# Trace Config
set_global_textmap(CloudTraceFormatPropagator())
tracer_provider = TracerProvider()
cloud_trace_exporter = CloudTraceSpanExporter(project_id=os.getenv("PROJECT_ID"))
tracer_provider.add_span_processor(BatchSpanProcessor(cloud_trace_exporter))
trace.set_tracer_provider(tracer_provider)



BACKEND_CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]


app = FastAPI(
    title="Financial Loan API",
    description="API for managing financial loan operations",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Healthcheck
@app.get("", response_model=HealthCheck, tags=["Healthcheck"])
@app.get("/", response_model=HealthCheck, tags=["Healthcheck"], include_in_schema=False)
async def healthcheck(request: Request):
    return {"message": "OK"}



app.include_router(api_v1.api_router, prefix="/api/v1")

FastAPIInstrumentor.instrument_app(app)
