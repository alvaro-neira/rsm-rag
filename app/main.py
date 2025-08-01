from fastapi import FastAPI
from app.api.endpoints import router
from app.middleware.logging_middleware import LoggingMiddleware
from app.core.logging_config import setup_logging

# Initialize structured logging
setup_logging()

app = FastAPI(title="RSM RAG Test Microservice", version="1.0.0")

# Add logging middleware
app.add_middleware(LoggingMiddleware)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)