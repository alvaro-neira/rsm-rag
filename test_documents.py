from app.services.document_service import DocumentService


def test_document_loading():
    doc_service = DocumentService()

    # Test loading all documents
    documents = doc_service.load_all_documents()

    print(f"\n📊 Summary:")
    print(f"Total chunks: {len(documents)}")

    # Show first chunk from each source
    sources = set(doc.metadata['source'] for doc in documents)
    for source in sources:
        source_docs = [doc for doc in documents if doc.metadata['source'] == source]
        print(f"\n📖 {source}: {len(source_docs)} chunks")
        if source_docs:
            print(f"First chunk preview: {source_docs[0].page_content[:200]}...")


if __name__ == "__main__":
    test_document_loading()
