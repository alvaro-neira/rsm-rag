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

## 4. Observability
* Used Langfuse for observability and not LangSmith because the former allows explicit tracing control.

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