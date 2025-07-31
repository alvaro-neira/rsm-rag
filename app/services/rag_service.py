from typing import Dict, Any
from langchain_openai import ChatOpenAI
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from langfuse import Langfuse
from langfuse import observe
import os
from dotenv import load_dotenv
import time

load_dotenv()


def _create_rag_prompt(question: str, context: str) -> str:
    """Create a prompt for the LLM with context"""
    return f"""You are a helpful assistant that answers questions about Python programming using the provided context.

Context from relevant documents:
{context}

Question: {question}

Instructions:
- Answer the question based on the provided context
- If the context doesn't contain enough information to answer the question, say so
- Be concise but comprehensive
- Use examples from the context when helpful
- Focus on Python programming concepts and best practices

Answer:"""


class RAGService:
    def __init__(self):
        self.document_service = DocumentService()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Initialize Langfuse
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST")
        )

    @observe()
    def ingest_documents(self) -> Dict[str, Any]:
        """Load, embed, and store all documents with tracing"""
        print("Starting document ingestion...")

        try:
            # Load documents
            documents = self.document_service.load_all_documents()

            # Generate embeddings
            start_time = time.time()
            embeddings = self.embedding_service.generate_embeddings(documents)
            duration = time.time() - start_time

            # Store in vector database
            self.vector_store.add_documents(documents, embeddings)
            stats = self.vector_store.get_collection_stats()

            result = {
                "status": "success",
                "total_documents": len(documents),
                "sources": stats['sources'],
                "message": f"Successfully ingested {len(documents)} documents"
            }

            print(f"Ingestion complete: {result['message']}")
            return result

        except Exception as e:
            print(f"Error during ingestion: {str(e)}")
            raise

    @observe()
    def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Answer a question using RAG with full tracing"""
        print(f"Processing query: '{question}'")

        try:
            # Generate query embedding
            query_embedding = self.embedding_service.generate_query_embedding(question)

            # Search for relevant documents
            search_results = self.vector_store.similarity_search(query_embedding, k=k)

            if not search_results:
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": []
                }

            # Prepare context from search results
            context_chunks = []
            sources = []

            for i, result in enumerate(search_results):
                context_chunks.append(result['text'])
                sources.append({
                    "page": result['metadata'].get('chunk_id', i),
                    "text": result['text'][:200] + "..." if len(result['text']) > 200 else result['text'],
                    "source": result['metadata'].get('source', 'unknown'),
                    "distance": result['distance']
                })

            # Create prompt for LLM
            context = "\n\n".join(context_chunks)
            prompt = _create_rag_prompt(question, context)

            # Generate answer
            response = self.llm.invoke(prompt)
            answer = response.content

            result = {
                "answer": answer,
                "sources": sources
            }

            print(f"Generated answer ({len(answer)} characters)")
            return result

        except Exception as e:
            print(f"Error: {str(e)}")
            raise
