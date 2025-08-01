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

- Used OpenAI API because that API is the one that I am more familiar width. 
- Used LangChain and not LangGraph because the latter would have added unnecessary complexity for this project.
- The needed environment variables are set in the `.env` file:
  - OPENAI_API_KEY=...
  - LANGFUSE_PUBLIC_KEY=pk-...
  - LANGFUSE_SECRET_KEY=sk-...
  - LANGFUSE_HOST=https://....cloud.langfuse.com

## 4. Observability & Logging

### Langfuse Tracing
* Used Langfuse for observability and not LangSmith because the former allows explicit tracing control.

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
  "path": "/query",
  "client_ip": "127.0.0.1",
  "user_agent": "curl/7.68.0"
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
  "duration_ms": 1250.5,
  "client_ip": "127.0.0.1"
}
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