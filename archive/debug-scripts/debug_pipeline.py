"""Comprehensive pipeline debugging script."""

import asyncio
import sys
from pathlib import Path
import psycopg2

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.ingestion.factory.processor_factory import ProcessorFactory
from app.ingestion.pipeline.ingestion_pipeline import IngestionPipeline
from app.core.config import get_settings
from app.models.enums import FileType
from app.chunking.strategies.recursive_text_chunk_strategy import (
    RecursiveTextChunkStrategy,
)
from app.embeddings.providers.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from app.vectorstore.providers.faiss_provider import FAISSVectorProvider
from app.keyword_search.providers.bm25_provider import BM25Provider
from app.retrieval.services.retriever_service import RetrieverService
from app.db.unit_of_work import UnitOfWorkFactory

settings = get_settings()


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


async def debug_document(document_id: str, document_name: str):
    """Debug a document through the entire pipeline."""

    print_section(f"DEBUGGING: {document_name} ({document_id})")

    # ---------------------------------------------------------
    # 1. FILE VALIDATION
    # ---------------------------------------------------------
    print_section("1. FILE VALIDATION")

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="eshwar",
        database="docmind",
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT original_filename, file_size, mime_type, storage_path FROM documents WHERE id = %s",
        (document_id,),
    )
    result = cur.fetchone()
    cur.close()
    conn.close()

    if not result:
        print("ERROR: Document not found in database")
        return

    filename, file_size, mime_type, storage_path = result
    print(f"Filename: {filename}")
    print(f"MIME type: {mime_type}")
    print(f"File size: {file_size} bytes")
    print(f"Storage path: {storage_path}")

    # ---------------------------------------------------------
    # 2. PDF EXTRACTION
    # ---------------------------------------------------------
    print_section("2. PDF EXTRACTION")

    file_path = str(Path("backend").absolute() / settings.STORAGE_PATH / storage_path)
    print(f"Full file path: {file_path}")
    print(f"File exists: {Path(file_path).exists()}")

    processor_factory = ProcessorFactory()
    ingestion_pipeline = IngestionPipeline(
        processor_factory=processor_factory, text_normalizer=None
    )

    try:
        extraction_result = await ingestion_pipeline.process(
            Path(file_path), FileType.PDF
        )
        print(f"Pages detected: {extraction_result.page_count}")
        print(f"Total characters: {extraction_result.character_count}")
        print(
            f"First 500 chars: {extraction_result.raw_text[:500] if extraction_result.raw_text else 'EMPTY'}"
        )
        print(
            f"Last 500 chars: {extraction_result.raw_text[-500:] if extraction_result.raw_text and len(extraction_result.raw_text) > 500 else 'EMPTY'}"
        )

        if extraction_result.metadata and "pages" in extraction_result.metadata:
            print("\nPage-by-page extraction:")
            for page_data in extraction_result.metadata["pages"]:
                page_num = page_data.get("page", "N/A")
                page_text = page_data.get("text", "")
                print(f"  Page {page_num}: {len(page_text)} characters")
                print(f"    Preview: {page_text[:200] if page_text else 'EMPTY'}")
    except Exception as e:
        print(f"ERROR: Extraction failed: {e}")
        import traceback

        traceback.print_exc()
        return

    # ---------------------------------------------------------
    # 3. DATABASE
    # ---------------------------------------------------------
    print_section("3. DATABASE VERIFICATION")

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="eshwar",
        database="docmind",
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT raw_text, character_count FROM document_contents WHERE document_id = %s",
        (document_id,),
    )
    content = cur.fetchone()
    cur.close()
    conn.close()

    if content:
        raw_text, char_count = content
        print(f"Document contents length: {char_count}")
        print(f"First 1000 chars: {raw_text[:1000] if raw_text else 'EMPTY'}")
        print(
            f"Last 1000 chars: {raw_text[-1000:] if raw_text and len(raw_text) > 1000 else 'EMPTY'}"
        )
    else:
        print("ERROR: No document content found in database")
        return

    # ---------------------------------------------------------
    # 4. CHUNKING
    # ---------------------------------------------------------
    print_section("4. CHUNKING")

    chunk_strategy = RecursiveTextChunkStrategy(chunk_size=1000, chunk_overlap=200)
    chunks = chunk_strategy.chunk(text=raw_text)

    print(f"Chunk count: {len(chunks)}")
    print("Chunk size: 1000")
    print("Overlap: 200")

    if chunks:
        print("\nFirst 5 chunks:")
        for i, chunk in enumerate(chunks[:5]):
            print(f"  Chunk {i}: {len(chunk.text)} chars, page {chunk.page_number}")
            print(f"    Preview: {chunk.text[:200]}")

        if len(chunks) > 5:
            print("\nLast 5 chunks:")
            for i, chunk in enumerate(chunks[-5:], len(chunks) - 5):
                print(f"  Chunk {i}: {len(chunk.text)} chars, page {chunk.page_number}")
                print(f"    Preview: {chunk.text[:200]}")
    else:
        print("ERROR: No chunks generated")
        print(f"Reason: Text length = {len(raw_text)}, may be too short")
        return

    # ---------------------------------------------------------
    # 5. EMBEDDINGS
    # ---------------------------------------------------------
    print_section("5. EMBEDDINGS")

    embedding_provider = SentenceTransformerEmbeddingProvider(settings.EMBEDDING_MODEL)
    chunk_texts = [chunk.text for chunk in chunks]

    try:
        embeddings = await embedding_provider.generate_embeddings(chunk_texts)
        print(f"Embedding count: {len(embeddings)}")
        print(f"Embedding dimension: {len(embeddings[0]) if embeddings else 0}")

        for i, (chunk, embedding) in enumerate(zip(chunks[:3], embeddings[:3])):
            print(f"  Chunk {i}:")
            print(f"    Chunk text length: {len(chunk.text)}")
            print(f"    Embedding dimension: {len(embedding)}")
            print("    Embedding generated: YES")
    except Exception as e:
        print(f"ERROR: Embedding generation failed: {e}")
        import traceback

        traceback.print_exc()
        return

    # ---------------------------------------------------------
    # 6. FAISS
    # ---------------------------------------------------------
    print_section("6. FAISS INDEX")

    vector_provider = FAISSVectorProvider(
        index_path=str(Path(settings.FAISS_INDEX_PATH) / "index.faiss"),
        embedding_model=settings.EMBEDDING_MODEL,
    )

    # Create index if needed
    try:
        dimension = len(embeddings[0])
        await vector_provider.create_index(dimension)
        print(f"Created FAISS index with dimension: {dimension}")
    except Exception as e:
        print(f"Index creation note: {e}")

    # Add vectors
    vector_ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    try:
        await vector_provider.add_vectors(vector_ids, embeddings)
        print(f"Number of vectors inserted: {len(vector_ids)}")
    except Exception as e:
        print(f"ERROR: Failed to add vectors: {e}")
        return

    # Perform search
    try:
        query_text = "What is this document about?"
        query_embedding = await embedding_provider.generate_embeddings([query_text])
        results = await vector_provider.search(query_embedding[0], top_k=10)

        print(f"\nManual similarity search for: '{query_text}'")
        print("Top 10 results:")
        for i, result in enumerate(results):
            print(
                f"  {i + 1}. Vector ID: {result.vector_id}, Score: {result.score:.4f}"
            )
    except Exception as e:
        print(f"ERROR: Search failed: {e}")
        import traceback

        traceback.print_exc()

    # ---------------------------------------------------------
    # 7. BM25
    # ---------------------------------------------------------
    print_section("7. BM25 INDEX")

    bm25_provider = BM25Provider(
        index_path=str(Path(settings.BM25_INDEX_PATH) / "index.pkl")
    )

    try:
        bm25_chunks = [
            (vector_ids[i], chunks[i].text, chunks[i].metadata)
            for i in range(len(chunks))
        ]
        bm25_provider.index_chunks(bm25_chunks)
        print(f"Tokens indexed: {len(chunks)}")
        print(f"Document IDs indexed: {len(set([vid for vid, _, _ in bm25_chunks]))}")

        # Perform keyword search
        keyword_results = bm25_provider.search(query_text, top_k=10)
        print(f"\nTop 10 keyword results for: '{query_text}'")
        for i, (vector_id, score) in enumerate(keyword_results):
            print(f"  {i + 1}. Vector ID: {vector_id}, Score: {score:.4f}")
    except Exception as e:
        print(f"ERROR: BM25 indexing failed: {e}")
        import traceback

        traceback.print_exc()

    # ---------------------------------------------------------
    # 8. RETRIEVER
    # ---------------------------------------------------------
    print_section("8. RETRIEVER SERVICE")

    try:
        retriever = RetrieverService(
            uow_factory=UnitOfWorkFactory.create,
            embedding_provider=embedding_provider,
            vector_provider=vector_provider,
            keyword_index_provider=bm25_provider,
        )

        retrieval_results = await retriever.retrieve(
            query=query_text,
            document_ids=[document_id],
            top_k=10,
        )

        print(f"Query: '{query_text}'")
        print(f"Total results: {len(retrieval_results)}")

        for i, result in enumerate(retrieval_results):
            print(f"  {i + 1}. Chunk ID: {result.chunk_id}, Score: {result.score:.4f}")
            print(f"      Text preview: {result.text[:100]}")
    except Exception as e:
        print(f"ERROR: Retrieval failed: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Main debugging function."""

    # Test failing PDF
    await debug_document(
        "18fee765-96d2-4cbf-b84d-83ee5bb93e34", "LOR HOD - Charan.pdf (FAILING)"
    )

    # Test working PDF
    await debug_document(
        "a0985118-d845-441c-89ac-66ddef1702b5", "dummy_upload_test.pdf (WORKING)"
    )


if __name__ == "__main__":
    asyncio.run(main())
