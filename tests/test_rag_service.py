import pytest
from unittest.mock import Mock, patch
from app.services.rag_service import RAGService

class TestRAGService:
    @pytest.fixture
    def rag_service(self):
        return RAGService()
    
    def test_create_rag_prompt(self, rag_service):
        """Test RAG prompt creation"""
        question = "What is a variable?"
        context = "A variable is a named storage location."
        
        prompt = rag_service._create_rag_prompt(question, context)
        
        assert question in prompt
        assert context in prompt
        assert "Context from relevant documents:" in prompt
    
    @patch('app.services.rag_service.RAGService.__init__')
    def test_query_no_results(self, mock_init, rag_service):
        """Test query when no documents found"""
        mock_init.return_value = None
        rag_service.vector_store = Mock()
        rag_service.embedding_service = Mock()
        
        # Mock empty search results
        rag_service.embedding_service.generate_query_embedding.return_value = [0.1] * 1536
        rag_service.vector_store.similarity_search.return_value = []
        
        result = rag_service.query("test question")
        
        assert "couldn't find any relevant information" in result["answer"]
        assert result["sources"] == []

# Install pytest first: pip install pytest
# Run tests: pytest tests/ -v