from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from typing import List
from app.core.logging_config import get_logger, log_event, log_error
import os
from dotenv import load_dotenv

load_dotenv()


class EmbeddingService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",  # Cost-effective and good quality
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.logger = get_logger("embedding_service")

    def generate_embeddings(self, documents: List[Document]) -> List[List[float]]:
        """Generate embeddings for a list of documents"""
        log_event(
            self.logger, 
            "embedding_generation_started", 
            "Starting embedding generation",
            document_count=len(documents)
        )

        # Extract text content from documents
        texts = [doc.page_content for doc in documents]

        try:
            # Generate embeddings in batches to avoid rate limits
            embeddings = self.embeddings.embed_documents(texts)
            log_event(
                self.logger, 
                "embedding_generation_completed", 
                "Embedding generation completed",
                embeddings_generated=len(embeddings)
            )
            return embeddings

        except Exception as e:
            log_error(self.logger, e, {
                "operation": "embedding_generation",
                "document_count": len(documents)
            })
            raise

    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a single query"""
        try:
            embedding = self.embeddings.embed_query(query)
            return embedding
        except Exception as e:
            log_error(self.logger, e, {
                "operation": "query_embedding_generation",
                "query": query
            })
            raise