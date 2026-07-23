if __name__ == "__main__":
    import asyncio
    from app.db.session import async_session_maker
    from app.db.uow import UnitOfWork
    from app.services.vector_index_service import VectorIndexService
    from app.vectorstore.providers.faiss_provider import FAISSProvider
    from app.services.llm.openai_provider import OpenAIProvider
    from app.services.embedding_service import EmbeddingService
    from app.chat.strategies.hybrid_retrieval import HybridRetrievalStrategy
    from app.core.config import get_settings
    from pathlib import Path

    settings = get_settings()

    def uow_factory():
        return UnitOfWork(async_session_maker)

    async def main():
        index_path = str(Path(settings.FAISS_INDEX_PATH) / "index.faiss")
        faiss_provider = FAISSProvider(index_path=index_path)
        vector_service = VectorIndexService(faiss_provider)
        openai = OpenAIProvider()
        embedding_service = EmbeddingService(openai)

        strategy = HybridRetrievalStrategy()

        question = "pick up some topic and explain me very clearly"

        uow = uow_factory()

        # Check FAISS first
        query_embedding = await embedding_service.generate_embeddings([question])
        semantic_results = await vector_service.search(query_embedding[0], top_k=20)
        print(f"FAISS returned {len(semantic_results)} results")
        if semantic_results:
            print(
                f"Top FAISS result: {semantic_results[0].vector_id}, score: {semantic_results[0].similarity_score}"
            )
        else:
            print("NO SEMANTIC RESULTS!")

        # Check hybrid retrieval
        chunks = await strategy.retrieve(
            question=question,
            document_ids=None,
            vector_index_service=vector_service,
            embedding_service=embedding_service,
            uow=uow,
            top_k=5,
            search_k=20,
        )

        print(f"Hybrid retrieval returned {len(chunks)} chunks.")

    if __name__ == "__main__":
        asyncio.run(main())
