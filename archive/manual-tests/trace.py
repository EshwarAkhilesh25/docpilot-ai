import asyncio
import os
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

# Configure basic logging to see everything
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def uow_factory():
    return SQLAlchemyUnitOfWork(AsyncSessionLocal)


async def list_documents():
    async with AsyncSessionLocal() as session:
        stmt = select(Document)
        result = await session.execute(stmt)
        docs = result.scalars().all()
        print("Documents in DB:")
        for d in docs:
            print(f" - {d.original_filename}")


async def trace_document(filename: str):
    settings = get_settings()

    print("=" * 60)
    print(f"TRACING DOCUMENT: {filename}")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        # Find document
        stmt = (
            select(Document)
            .where(Document.original_filename.ilike(f"%{filename}%"))
            .options(selectinload(Document.content), selectinload(Document.chunks))
        )
        result = await session.execute(stmt)
        docs = result.scalars().all()

        if not docs:
            print(f"Document '{filename}' not found in DB.")
            return

        doc = docs[0]

        print("\n" + "-" * 57)
        print("1. FILE VALIDATION")
        print("-" * 57)
        print(f"filename: {doc.original_filename}")
        print(f"mime type: {doc.mime_type}")
        print(f"file size: {doc.file_size}")

        print("\n" + "-" * 57)
        print("2. PDF EXTRACTION & 3. DATABASE")
        print("-" * 57)

        if not doc.content:
            print("No DocumentContent found in DB.")
        else:
            content = doc.content
            print(f"pages detected: {content.page_count}")
            print(f"total characters: {content.character_count}")
            raw_text = content.raw_text or ""
            print(f"document_contents length: {len(raw_text)}")
            print(f"first 1000 characters: {raw_text[:1000]!r}")
            print(f"last 1000 characters: {raw_text[-1000:]!r}")

        print("\n" + "-" * 57)
        print("4. CHUNKING & 5. EMBEDDINGS")
        print("-" * 57)

        chunks = doc.chunks
        print(f"chunk count: {len(chunks)}")
        if chunks:
            # Sort chunks by chunk_index
            chunks.sort(key=lambda c: c.chunk_index)
            # Estimate chunk size
            sizes = [len(c.text) for c in chunks]
            avg_size = sum(sizes) / len(sizes) if sizes else 0
            print(f"chunk size (average): {avg_size}")

            print("\nFirst five chunks:")
            for c in chunks[:5]:
                print(
                    f"  Chunk {c.chunk_index} | ID: {c.id} | Vector ID: {c.vector_id} | Length: {len(c.text)}"
                )

            print("\nLast five chunks:")
            for c in chunks[-5:]:
                print(
                    f"  Chunk {c.chunk_index} | ID: {c.id} | Vector ID: {c.vector_id} | Length: {len(c.text)}"
                )
        else:
            print("Zero chunks found in DB.")

        # 6. FAISS & 7. BM25 & 8. RETRIEVER
        print("\n" + "-" * 57)
        print("6. FAISS & 7. BM25 & 8. RETRIEVER")
        print("-" * 57)

        embedding_service = SentenceTransformerEmbeddingProvider(
            model_name=settings.EMBEDDING_MODEL
        )
        faiss_store = FAISSVectorProvider(
            embedding_model=settings.EMBEDDING_MODEL
        )  # index_path param is not used like this, load is called explicitly
        bm25_index = BM25Provider()

        # Load indexes explicitly if possible
        if os.path.exists(settings.FAISS_INDEX_PATH):
            print(f"FAISS index found at {settings.FAISS_INDEX_PATH}.")
            try:
                await faiss_store.load(settings.FAISS_INDEX_PATH)
                print(
                    f"Total vectors: {faiss_store._index.ntotal if faiss_store._index else 0}"
                )
            except Exception as e:
                print(f"FAISS load error: {e}")
        else:
            print("FAISS index not found.")

        if os.path.exists(settings.BM25_INDEX_PATH):
            print(f"BM25 index found at {settings.BM25_INDEX_PATH}.")
            try:
                bm25_index.load_index(settings.BM25_INDEX_PATH)
                print(
                    f"Total documents indexed in BM25: {len(bm25_index._corpus) if hasattr(bm25_index, '_corpus') else 'Unknown'}"
                )
            except Exception as e:
                print(f"BM25 load error: {e}")
        else:
            print("BM25 index not found.")

        print("\nPerforming manual similarity search:")
        question = "What is this document about?"

        retriever = RetrieverService(
            uow_factory=uow_factory,
            embedding_provider=embedding_service,
            vector_provider=faiss_store,
            keyword_index_provider=bm25_index,
        )

        print(f"Query: '{question}' for document: {doc.id}")

        try:
            results = await retriever.retrieve(
                query=question, document_ids=[doc.id], top_k=10
            )
            print("\nRetriever merged results:")
            for r in results:
                print(
                    f"  Chunk ID: {r.chunk_id}, Score: {r.similarity_score}, Content: {r.text[:100]!r}"
                )

            print("\n" + "-" * 57)
            print("9. LLM INPUT & 10. CHAT SERVICE")
            print("-" * 57)

            chat_service = ChatService(
                uow_factory=uow_factory,
                llm_provider=None,  # Not needed for validate_retrieval
                retriever=retriever,
            )
            # test validate_retrieval
            is_valid = chat_service._validate_retrieval(results)
            print(f"_validate_retrieval() returns: {is_valid}")

            if not results:
                print("highest similarity: N/A (0 chunks)")
            else:
                highest_sim = max([r.similarity_score for r in results])
                avg_sim = sum([r.similarity_score for r in results]) / len(results)
                print(f"chunk count: {len(results)}")
                print(f"highest similarity: {highest_sim}")
                print(f"average similarity: {avg_sim}")
                print(f"threshold: {settings.RAG_MIN_SIMILARITY_THRESHOLD}")

        except Exception as e:
            print(f"Retrieval error: {e}")
            import traceback

            traceback.print_exc()


async def main():
    await list_documents()
    await trace_document("ESHWAR EWS certificate")
    await trace_document("SDE assignment")


if __name__ == "__main__":
    asyncio.run(main())
