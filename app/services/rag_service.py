from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
import os
from dotenv import load_dotenv

load_dotenv()


class RAGService:
    def __init__(self):
        self.document_service = DocumentService()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,  # Low temperature for more consistent answers
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    def ingest_documents(self) -> Dict[str, Any]:
        """Load, embed, and store all documents"""
        print("🚀 Starting document ingestion...")

        # Load documents
        documents = self.document_service.load_all_documents()

        # Generate embeddings for all documents
        embeddings = self.embedding_service.generate_embeddings(documents)

        # Store in vector database
        self.vector_store.add_documents(documents, embeddings)

        # Get statistics
        stats = self.vector_store.get_collection_stats()

        result = {
            "status": "success",
            "total_documents": len(documents),
            "sources": stats['sources'],
            "message": f"Successfully ingested {len(documents)} documents"
        }

        print(f"✅ Ingestion complete: {result['message']}")
        return result

    def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Answer a question using RAG"""
        print(f"🔍 Processing query: '{question}'")

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
        prompt = self._create_rag_prompt(question, context)

        # Generate answer
        try:
            response = self.llm.invoke(prompt)
            answer = response.content

            print(f"✅ Generated answer ({len(answer)} characters)")

            return {
                "answer": answer,
                "sources": sources
            }

        except Exception as e:
            print(f"❌ Error generating answer: {str(e)}")
            return {
                "answer": f"Sorry, I encountered an error while generating the answer: {str(e)}",
                "sources": sources
            }

    def _create_rag_prompt(self, question: str, context: str) -> str:
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
