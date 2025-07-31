from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class EmbeddingService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",  # Cost-effective and good quality
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    def generate_embeddings(self, documents: List[Document]) -> List[List[float]]:
        """Generate embeddings for a list of documents"""
        print(f"Generating embeddings for {len(documents)} documents...")

        # Extract text content from documents
        texts = [doc.page_content for doc in documents]

        try:
            # Generate embeddings in batches to avoid rate limits
            embeddings = self.embeddings.embed_documents(texts)
            print(f"Generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise

    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a single query"""
        try:
            embedding = self.embeddings.embed_query(query)
            return embedding
        except Exception as e:
            print(f"Error generating query embedding: {str(e)}")
            raise