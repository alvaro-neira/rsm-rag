# RSM RAG Test Microservice with Langfuse Observability

**Author:** Alvaro Neira  
**Email:** alvaroneirareyes@gmail.com

### Prerequisites

- Python 3.11+ (I used 3.11.9)
- Docker & Docker Compose
- OpenAI API key
- Langfuse account

## 1. Indexing

- **Engine**: Chroma (local, persistent). The reasons for using Chroma are its
simplicity and lightweight, compared to other alternatives such as Pinecone or FAISS.
- **Embedding Model**: OpenAI text-embedding-3-small (1536 dimensions)
- **Chunk Size**: 1000 characters with 200 character overlap
## 3. LLM Integration with LangChain

- Used OpenAI API because that API is the one that I am most familiar with. 
- Used LangChain and not LangGraph because the latter would have added unnecessary complexity for this project.
- The needed environment variables are set in the `.env` file:
  - OPENAI_API_KEY=...
  - LANGFUSE_PUBLIC_KEY=pk-...
  - LANGFUSE_SECRET_KEY=sk-...
  - LANGFUSE_HOST=https://....cloud.langfuse.com

## 4. Observability & Monitoring

### Langfuse Tracing
* Used Langfuse for observability and not LangSmith because the former allows explicit tracing control.

## Structured Logging
The application emits structured JSON logs for all requests, errors, and significant events. All logs include:

**Standard Fields:**
- `timestamp`: UTC timestamp in ISO format
- `level`: Log level (INFO, ERROR, WARNING)
- `service`: Always "rsm-rag"
- `logger`: Module/component name (e.g., "rsm-rag.api", "rsm-rag.rag_service")
- `message`: Human-readable log message

**Event Types:**
- `request`: Incoming HTTP requests
- `response`: HTTP responses with timing
- `query_started`: RAG query processing begins
- `query_completed`: RAG query processing completed
- `document_ingestion_started`: Document ingestion begins
- `document_ingestion_completed`: Document ingestion completed
- `error`: Error occurred with context

**Example Log Formats:**

```json
// Request Log
{
  "timestamp": "2025-08-01T01:17:39.888Z",
  "level": "INFO",
  "service": "rsm-rag",
  "logger": "rsm-rag.middleware",
  "message": "POST /query",
  "event_type": "request",
  "http_method": "POST",
  "path": "/query"
}

// Query Processing Log
{
  "timestamp": "2025-08-01T01:17:40.123Z",
  "level": "INFO",
  "service": "rsm-rag",
  "logger": "rsm-rag.api",
  "message": "Processing RAG query",
  "event_type": "query_started",
  "question": "What is a variable?",
  "question_length": 18
}

// Error Log
{
  "timestamp": "2025-08-01T01:17:41.456Z",
  "level": "ERROR",
  "service": "rsm-rag",
  "logger": "rsm-rag.rag_service",
  "message": "Error occurred: OpenAI API rate limit exceeded",
  "event_type": "error",
  "error_type": "RateLimitError",
  "error_message": "OpenAI API rate limit exceeded",
  "operation": "rag_query",
  "question": "What is a variable?",
  "exception": "Traceback (most recent call last)..."
}

// Response Log
{
  "timestamp": "2025-08-01T01:17:42.789Z",
  "level": "INFO",
  "service": "rsm-rag",
  "logger": "rsm-rag.middleware",
  "message": "POST /query - 200 (1250.50ms)",
  "event_type": "response",
  "http_method": "POST",
  "path": "/query",
  "status_code": 200,
  "duration_ms": 1250.5
}

```
### System Metrics
The application exposes comprehensive metrics for monitoring and alerting at `/metrics` endpoint using Prometheus format (the most suitable for this kind of metrics).

**HTTP Request Metrics:**
- `http_requests_total` - Total HTTP requests by method, endpoint, and status code
- `http_request_duration_seconds` - Request latency histogram with buckets
- `http_requests_in_progress` - Currently active HTTP requests

**RAG Business Metrics:**
- `rag_queries_total{status="success|error"}` - Total RAG queries processed
- `rag_query_duration_seconds` - RAG query processing time histogram
- `rag_sources_found` - Distribution of sources found per query

**Document Processing Metrics:**
- `document_ingestion_total{status="success|error"}` - Document ingestion operations
- `document_ingestion_duration_seconds` - Ingestion processing time
- `documents_processed_total` - Total documents processed counter

**Vector Store Metrics:**
- `vector_store_operations_total{operation="add|search", status="success|error"}` - Vector store operations
- `vector_store_collection_size` - Current number of documents in collection

**Embedding Metrics:**
- `embeddings_generated_total{type="document|query"}` - Total embeddings generated
- `embedding_generation_duration_seconds{type="document|query"}` - Embedding generation time

**Error Metrics:**
- `errors_total{error_type, operation}` - Error counts by type and operation

**Usage:**
```bash
# Access metrics endpoint
curl http://localhost:8000/metrics

# Example Prometheus scrape config
scrape_configs:
  - job_name: 'rsm-rag'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

## How to use this

```bash
git clone git@github.com:alvaro-neira/rsm-rag.git
cd rsm-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with the environment variables described in point 3
vim .env

# Build and start FastAPI server with Docker (Docker Desktop must be running)
docker compose up --build

# Access the API
curl http://localhost:8000/health
```

The FastAPI server can be run without docker:
```bash
python -m app.main
```

## Testing
```bash
# Install test dependencies
pip install pytest pytest-mock

# Run tests (unit tests, integration tests, end-to-end tests)
pytest -v
```

