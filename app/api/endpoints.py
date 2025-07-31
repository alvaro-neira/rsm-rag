from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.rag_service import RAGService

# Initialize RAG service
rag_service = RAGService()

router = APIRouter()


# Request/Response Models
class QueryRequest(BaseModel):
    question: str


class SourceResponse(BaseModel):
    page: int
    text: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]


class IngestResponse(BaseModel):
    status: str
    message: str
    total_documents: int
    sources: Dict[str, int]


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents():
    """Trigger document ingestion"""
    try:
        result = rag_service.ingest_documents()
        return IngestResponse(
            status=result["status"],
            message=result["message"],
            total_documents=result["total_documents"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents using RAG"""
    try:
        result = rag_service.query(request.question)
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
