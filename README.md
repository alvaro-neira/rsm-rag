# RAG Microservice with Langfuse Observability

A production-ready Python microservice that implements Retrieval-Augmented Generation (RAG) for answering questions about Python programming using Think Python book and PEP 8 documentation.

## API Endpoints

### `GET /health`
Health check endpoint
```json
{
  "status": "ok"
}
```

### `POST /ingest`
Trigger document ingestion
```json
{
  "status": "success",
  "message": "Successfully ingested 277 documents",
  "total_documents": 277,
  "sources": {
    "Think Python": 217,
    "PEP 8": 60
  }
}
```

### `POST /query`
Query documents using RAG
```json
{
  "question": "What is a variable in Python?"
}
```

Response:
```json
{
  "answer": "A variable in Python is a named storage location that holds a value...",
  "sources": [
    {
      "page": 0,
      "text": "This vocabulary is important – you will need it...",
      "source": "Think Python",
      "distance": 1.121
    }
  ]
}
```

## Installation & Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API key
- Langfuse account (for observability)

### 1. Clone and Setup Environment

```bash
git clone git@github.com:alvaro-neira/rsm-rag.git
cd rsm-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
LANGFUSE_PUBLIC_KEY=pk-lf-your_public_key
LANGFUSE_SECRET_KEY=sk-lf-your_secret_key
LANGFUSE_HOST=https://*.cloud.langfuse.com
```

### 3. Run with Docker Compose (Recommended)

```bash
# Build and start services
docker-compose up --build

# Access the API
curl http://localhost:8000/health
```

### 4. Manual Setup (Development)

```bash
# Start the development server
python -m app.main

# In another terminal, test the endpoints
python test_api.py
```

## Observability

The service includes comprehensive observability through Langfuse:

- **Request Tracing**: Full pipeline traces from query to response
- **Performance Metrics**: Latency, token usage, and throughput
- **Error Monitoring**: Detailed error logs and stack traces
- **Component Insights**: Individual timing for embedding, search, and LLM steps

View traces at your Langfuse dashboard: https://cloud.langfuse.com

## Testing

```bash
# Install test dependencies
pip install pytest

# Run unit tests
pytest tests/ -v

# Test API endpoints
python test_api.py

# Test complete RAG pipeline
python test_rag_complete.py
```

## Configuration

### Vector Database
- **Engine**: Chroma (local, persistent)
- **Embedding Model**: OpenAI text-embedding-3-small (1536 dimensions)
- **Chunk Size**: 1000 characters with 200 character overlap

### LLM Configuration
- **Model**: OpenAI GPT-3.5-turbo
- **Temperature**: 0.1 (for consistent responses)
- **Max Tokens**: Auto-determined based on context

### Document Sources
- **Think Python**: 19 chapters loaded from https://allendowney.github.io/ThinkPython/
- **PEP 8**: Python style guide from https://peps.python.org/pep-0008/
