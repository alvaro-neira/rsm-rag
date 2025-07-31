import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class DocumentService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def load_think_python(self) -> str:
        """Load the Think Python book content"""
        # We'll implement this next
        pass

    def load_pep8(self) -> str:
        """Load PEP 8 content"""
        # We'll implement this next
        pass

    def chunk_text(self, text: str, source: str) -> List[Document]:
        """Split text into chunks"""
        chunks = self.text_splitter.split_text(text)
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={"source": source, "chunk_id": i}
            )
            documents.append(doc)
        return documents
