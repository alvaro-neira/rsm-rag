import chromadb
from typing import List, Dict, Any
from langchain.schema import Document
import os


class VectorStore:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        """Initialize Chroma vector store"""
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="rag_documents",
            metadata={"description": "RAG microservice document collection"}
        )

        print(f"Vector store initialized. Collection size: {self.collection.count()}")

    def add_documents(self, documents: List[Document], embeddings: List[List[float]]):
        """Add documents and their embeddings to the vector store"""
        print(f"Adding {len(documents)} documents to vector store...")

        # Prepare data for Chroma
        ids = [f"doc_{i}" for i in range(len(documents))]
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        # Add to collection
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        print(f"Added {len(documents)} documents. Total in collection: {self.collection.count()}")

    def similarity_search(self, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })

        return formatted_results

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        count = self.collection.count()

        # Get some sample documents to analyze sources
        sample_results = self.collection.get(limit=count, include=["metadatas"])
        sources = {}

        if sample_results['metadatas']:
            for metadata in sample_results['metadatas']:
                source = metadata.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1

        return {
            'total_documents': count,
            'sources': sources
        }
