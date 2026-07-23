import pytest

import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.document import Document
from app.core.config import get_settings
from app.retrieval.services.retriever_service import RetrieverService
from app.vectorstore.providers.faiss_provider import FAISSVectorProvider
from app.keyword_search.providers.bm25_provider import BM25Provider
from app.embeddings.providers.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from app.chat.services.chat_service import ChatService
from app.db.unit_of_work import SQLAlchemyUnitOfWork

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def uow_factory():
    # Fix the uow_factory to return a UOW initialized with a session factory
    return SQLAlchemyUnitOfWork(AsyncSessionLocal)


@pytest.mark.asyncio
async def test_search():
    settings = get_settings()

    async with AsyncSessionLocal() as session:
        stmt = select(Document).options(
            selectinload(Document.content), selectinload(Document.chunks)
        )
        result = await session.execute(stmt)
        docs = result.scalars().all()

        doc_ews = next((d for d in docs if "EWS" in d.original_filename), None)
        doc_sde = next((d for d in docs if "SDE" in d.original_filename), None)

        embedding_service = SentenceTransformerEmbeddingProvider(
            model_name=settings.EMBEDDING_MODEL
        )

        for doc in [doc_ews, doc_sde]:
            if not doc:
                continue

            print(f"\n{'=' * 60}")
            print(f"TESTING DOCUMENT: {doc.original_filename}")
            print(f"{'=' * 60}")

            # 1. Create fresh indices in memory
            faiss_store = FAISSVectorProvider(embedding_model=settings.EMBEDDING_MODEL)
            bm25_index = BM25Provider()

            # 2. Index the document chunks
            chunks = doc.chunks
            if not chunks:
                print("No chunks found.")
                continue

            # Get embeddings and index to FAISS
            texts = [c.text for c in chunks]
            vector_ids = [c.vector_id for c in chunks]

            embeddings = await embedding_service.generate_embeddings(texts)

            await faiss_store.create_index(len(embeddings[0]))
            await faiss_store.add_vectors(vector_ids, embeddings)

            # Index to BM25
            keyword_chunks = [(c.vector_id, c.text, c.chunk_metadata) for c in chunks]
            bm25_index.create_index()
            bm25_index.add_chunks(keyword_chunks)

            # 3. Retrieve

            # We need to manually load chunks in a patched RetrieverService to avoid the session bug in uow_factory
            class PatchedRetrieverService(RetrieverService):
                async def _load_chunks_by_chunk_ids(self, chunk_ids):
                    # just return the chunks we already loaded
                    return {c.vector_id: c for c in chunks if c.vector_id in chunk_ids}

            retriever = PatchedRetrieverService(
                uow_factory=uow_factory,
                embedding_provider=embedding_service,
                vector_provider=faiss_store,
                keyword_index_provider=bm25_index,
            )

            question = "What is this document about?"
            print(f"Querying: '{question}'")

            # Print intermediate semantic results
            query_embedding = await embedding_service.generate_embedding(question)
            semantic_results = await faiss_store.search(query_embedding, top_k=5)
            print("\nSemantic Results:")
            for r in semantic_results:
                print(f"  {r.vector_id}: {r.similarity_score}")

            results = await retriever.retrieve(
                query=question, document_ids=[doc.id], top_k=5
            )

            print("\nMerged Results:")
            for r in results:
                print(
                    f"  Chunk ID: {r.chunk_id} | Score: {r.similarity_score} | Text: {r.text[:50]!r}"
                )

            chat_service = ChatService(
                uow_factory=uow_factory, llm_provider=None, retriever=retriever
            )

            # Temporarily monkey-patch the original _validate_retrieval
            def original_validate(ch):
                if not ch:
                    return {
                        "is_valid": False,
                        "reason": "No relevant context found in documents.",
                        "highest_similarity": 0.0,
                    }
                similarities = [c.similarity_score for c in ch]
                highest_sim = max(similarities)
                is_valid = highest_sim >= settings.RAG_MIN_SIMILARITY_THRESHOLD
                return {
                    "is_valid": is_valid,
                    "reason": None
                    if is_valid
                    else f"Similarity {highest_sim:.2f} below threshold {settings.RAG_MIN_SIMILARITY_THRESHOLD}",
                    "highest_similarity": highest_sim,
                }

            chat_service._validate_retrieval = original_validate

            validation = chat_service._validate_retrieval(results)
            print(f"\nValidation Result: {validation}")


if __name__ == "__main__":
    asyncio.run(test_search())
