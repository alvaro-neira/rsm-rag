# RSM RAG Test Microservice with Langfuse Observability

**Author:** Alvaro Neira  
**Email:** alvaroneirareyes@gmail.com

### Prerequisites

- Python 3.11+ (I used 3.11.9)
- Docker & Docker Compose
- OpenAI API key
- Langfuse account

## How to use deploy this service

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

## 1. Indexing

- **Engine**: Chroma (local, persistent). The reasons for using Chroma are its
simplicity and lightweight, compared to other alternatives such as Pinecone or FAISS.
- **Embedding Model**: OpenAI text-embedding-3-small (1536 dimensions)
- **Chunk Size**: 1000 characters with 200 character overlap

## 2. API Endpoints (FastAPI)

- `GET http://localhost:8000/health` → returns 200 OK.  
- `POST http://localhost:8000/ingest` → triggers the ingestion. The 2 documents ("Think Python" and "PEP 8") are automatically ingested when the service starts.
It doesn't accept any parameters. It returs:
```json
{
    "status": "success",
    "message": "Successfully ingested 616 documents",
    "total_documents": 616,
    "sources": {
        "Think Python": 556,
        "PEP 8": 60
    }
}
```
- `POST http://localhost:8000/query` → accepts:

  ```json
  { "question": "<text>" }
  ```

  and returns:

  ```json
  {
    "answer": "<generated answer>",
    "sources": [
      { "page": <number>, "text": "<passage text>" },
        ...
    ]
  }
  ```

## 3. LLM Integration with LangChain

- Used OpenAI API because that API is the one that I am most familiar with. 
- Used LangChain and not LangGraph because the latter would have added unnecessary complexity for this project.
- The needed environment variables are set in the `.env` file:
  - OPENAI_API_KEY=...
  - LANGFUSE_PUBLIC_KEY=pk-...
  - LANGFUSE_SECRET_KEY=sk-...
  - LANGFUSE_HOST=https://....cloud.langfuse.com

## 4. Observability

### Langfuse Tracing
* Used Langfuse for observability and not LangSmith because the former allows explicit tracing control.
To see the instrumented spans, see them in https://cloud.langfuse.com/

### Structured Logging
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

**Example:**

```json
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

```
### System Metrics
The application exposes comprehensive metrics for monitoring and alerting at `/metrics` endpoint:

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
```

Prometheus and Grafana are included in the Docker Compose setup for easy monitoring and visualization of these metrics:
* Prometheus: http://localhost:9090
* Grafana: http://localhost:3000 (User: admin/ Pass: admin)

(Only if the FastAPI server is run with Docker)

### Create Useful Queries In Prometheus (http://localhost:9090):

**1. Query Processing Rate:**
```promql
rate(rag_queries_total[5m])
```

**2. Average Query Duration:**
```promql
rate(rag_query_duration_seconds_sum[5m]) / rate(rag_query_duration_seconds_count[5m])
```

**3. Request Error Rate:**
```promql
rate(http_requests_total{status_code!="200"}[5m]) / rate(http_requests_total[5m])
```

**4. 95th Percentile Response Time:**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Set Up Grafana Dashboard

### 1. Access Grafana:
- Go to http://localhost:3000
- Login: admin/admin
- Change password when prompted

### 2. Add Prometheus Data Source:
- Click "Add data source"
- Select "Prometheus"
- URL: `http://prometheus:9090`
- Click "Save & Test"

### 3. Create RAG Dashboard:

**Create panels for:**

**Panel 1: RAG Queries per Second**
```promql
rate(rag_queries_total[1m])
```

**Panel 2: Average Query Duration**
```promql
rate(rag_query_duration_seconds_sum[5m]) / rate(rag_query_duration_seconds_count[5m])
```

**Panel 3: HTTP Request Duration by Endpoint**
```promql
http_request_duration_seconds{method="POST"}
```

**Panel 4: Error Rate**
```promql
(rate(http_requests_total{status_code!="200"}[5m]) / rate(http_requests_total[5m])) * 100
```

## Testing
```bash
# Install test dependencies
pip install pytest pytest-mock

# Run tests (unit tests, integration tests, end-to-end tests)
pytest -v
```

