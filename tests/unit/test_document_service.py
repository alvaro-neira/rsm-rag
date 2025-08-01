from unittest.mock import Mock, patch
from app.services.document_service import DocumentService


class TestDocumentService:

    def test_chunk_text(self):
        """Test text chunking without external dependencies"""
        doc_service = DocumentService()

        # Create test text longer than chunk size
        test_text = "A" * 1500  # 1500 characters

        chunks = doc_service.chunk_text(test_text, "test_source")

        assert len(chunks) >= 1  # Should create at least one chunk
        assert all(chunk.metadata["source"] == "test_source" for chunk in chunks)
        assert all(len(chunk.page_content) <= 1200 for chunk in chunks)  # Within chunk size + overlap

    @patch('requests.get')
    def test_load_pep8_success(self, mock_get):
        """Test PEP 8 loading with mocked HTTP request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'<section id="pep-content">PEP 8 content here</section>'
        mock_get.return_value = mock_response

        doc_service = DocumentService()
        result = doc_service.load_pep8()

        assert "PEP 8 content here" in result
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_load_pep8_failure(self, mock_get):
        """Test PEP 8 loading with network failure"""
        mock_get.side_effect = Exception("Network error")

        doc_service = DocumentService()
        result = doc_service.load_pep8()

        assert result == ""  # Should return empty string on failure
