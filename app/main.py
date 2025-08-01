from fastapi import FastAPI
from app.api.endpoints import router
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.metrics_middleware import MetricsMiddleware
from app.core.logging_config import setup_logging
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize structured logging
setup_logging()

app = FastAPI(title="RSM RAG Test Microservice", version="1.0.0")

# Add middleware (order matters - metrics first, then logging)
app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)