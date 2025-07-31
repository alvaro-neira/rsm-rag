# RSM RAG Test Microservice with Langfuse Observability

**Author:** Alvaro Neira  
**Email:** alvaroneirareyes@gmail.com

* Used Python 3.11.9

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

# Build and start service with docker
docker compose up --build

# Access the API
curl http://localhost:8000/health
```

It can be run without docker:
```bash
python -m app.main
```

## Unit Tests
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