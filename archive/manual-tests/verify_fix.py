import asyncio
import sys
from pathlib import Path
from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import AsyncSessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.core.config import get_settings
from app.vectorstore.providers.faiss_provider import FAISSVectorProvider
from app.embeddings.providers.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)


async def main():
    target_filename = "Interview.pdf"

    print("=" * 60)
    print(f"Verifying Document: {target_filename}")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Document)
            .where(Document.original_filename == target_filename)
            .limit(1)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            print("Document not found.")
            return

        print(f"document_id: {doc.id}")

        chunk_result = await session.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == doc.id)
        )
        chunks = chunk_result.scalars().all()
        print(f"chunk count: {len(chunks)}")
        if chunks:
            print(f"first chunk text: {chunks[0].text[:50]}...")

    # FAISS search
    print("\nQuerying FAISS:")
    settings = get_settings()
    faiss_provider = FAISSVectorProvider(
        index_path=str(Path(settings.FAISS_INDEX_PATH) / "index.faiss")
    )
    embedding_provider = SentenceTransformerEmbeddingProvider(
        model_name="BAAI/bge-small-en-v1.5"
    )

    query = "What is this document about?"
    query_vector = await embedding_provider.generate_embedding(query)
    results = await faiss_provider.search(query_vector, top_k=3)

    print(f"FAISS results count: {len(results)}")
    for i, res in enumerate(results):
        print(
            f"Result {i + 1}: vector_id={res.vector_id}, score={res.similarity_score}"
        )


if __name__ == "__main__":
    asyncio.run(main())
