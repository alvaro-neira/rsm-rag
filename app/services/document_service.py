import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os
from dotenv import load_dotenv

load_dotenv()


def load_think_python() -> str:
    """Load the Think Python book content"""
    print("Loading Think Python book...")

    # Think Python has multiple chapters, let's get the main chapters
    base_url = "https://allendowney.github.io/ThinkPython/"
    # TODO: In production, use all 19 chapters
    chapters = [f"chap{i:02d}.html" for i in range(1, 9)]

    all_content = []

    for chapter in chapters:
        try:
            url = base_url + chapter
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract main content (remove navigation, headers, etc.)
            main_content = soup.find('main') or soup.find('div', class_='content') or soup.body
            if main_content:
                text = main_content.get_text(strip=True, separator=' ')
                all_content.append(f"Chapter: {chapter}\n\n{text}")
                print(f"✓ Loaded {chapter}")

        except Exception as e:
            print(f"❌ Failed to load {chapter}: {str(e)}")
            continue

    return "\n\n".join(all_content)


def load_pep8() -> str:
    """Load PEP 8 content"""
    print("Loading PEP 8...")

    try:
        url = "https://peps.python.org/pep-0008/"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # PEP 8 content is in the main section
        main_content = soup.find('section', id='pep-content') or soup.find('div', class_='section')
        if main_content:
            text = main_content.get_text(strip=True, separator=' ')
            print("✓ Loaded PEP 8")
            return text
        else:
            print("❌ Could not find PEP 8 main content")
            return ""

    except Exception as e:
        print(f"❌ Failed to load PEP 8: {str(e)}")
        return ""


class DocumentService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def chunk_text(self, text: str, source: str) -> List[Document]:
        """Split text into chunks"""
        print(f"Chunking {source}...")
        chunks = self.text_splitter.split_text(text)
        documents = []

        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={"source": source, "chunk_id": i, "total_chunks": len(chunks)}
            )
            documents.append(doc)

        print(f"✓ Created {len(chunks)} chunks for {source}")
        return documents

    def load_all_documents(self) -> List[Document]:
        """Load and chunk all documents"""
        all_documents = []

        # Load Think Python
        think_python_text = load_think_python()
        if think_python_text:
            think_python_docs = self.chunk_text(think_python_text, "Think Python")
            all_documents.extend(think_python_docs)

        # Load PEP 8
        pep8_text = load_pep8()
        if pep8_text:
            pep8_docs = self.chunk_text(pep8_text, "PEP 8")
            all_documents.extend(pep8_docs)

        print(f"✓ Total documents loaded: {len(all_documents)}")
        return all_documents