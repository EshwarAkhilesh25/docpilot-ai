import asyncio
import logging
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.embeddings.providers.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from app.keyword_search.providers.bm25_provider import BM25Provider
from app.models.document import Document
from app.vectorstore.providers.faiss_provider import FAISSVectorProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def rebuild_indices():
    settings = get_settings()

    faiss_path = Path(settings.FAISS_INDEX_PATH) / "index.faiss"
    bm25_path = Path(settings.BM25_INDEX_PATH) / "bm25_index.pkl"

    # We will build from scratch
    if faiss_path.exists():
        os.remove(faiss_path)
    if bm25_path.exists():
        os.remove(bm25_path)

    faiss_store = FAISSVectorProvider(index_path=str(faiss_path))
    bm25_index = BM25Provider(index_path=str(bm25_path))

    embedding_service = SentenceTransformerEmbeddingProvider(model_name=settings.EMBEDDING_MODEL)

    async with AsyncSessionLocal() as session:
        stmt = select(Document).options(selectinload(Document.chunks))
        result = await session.execute(stmt)
        docs = result.scalars().all()

        all_chunks = []
        for doc in docs:
            all_chunks.extend(doc.chunks)

        if not all_chunks:
            pass
            return

        pass

        texts = [c.text for c in all_chunks]
        vector_ids = [c.vector_id for c in all_chunks]

        embeddings = await embedding_service.generate_embeddings(texts)

        await faiss_store.create_index(len(embeddings[0]))
        await faiss_store.add_vectors(vector_ids, embeddings)
        await faiss_store.save(str(faiss_path))
        pass

        keyword_chunks = [(c.vector_id, c.text, c.chunk_metadata) for c in all_chunks]
        bm25_index.create_index()
        bm25_index.add_chunks(keyword_chunks)
        bm25_index.save_index(str(bm25_path))
        pass


if __name__ == "__main__":
    asyncio.run(rebuild_indices())
