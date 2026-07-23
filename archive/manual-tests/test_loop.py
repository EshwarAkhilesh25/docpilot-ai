if __name__ == "__main__":
    import asyncio
    import sys
    from pathlib import Path
    from sqlalchemy import select

    sys.path.insert(0, str(Path(__file__).parent))

    from app.db.session import AsyncSessionLocal
    from app.models.document import Document
    from app.models.document_content import DocumentContent
    from app.chunking.strategies.recursive_text_chunk_strategy import (
        RecursiveTextChunkStrategy,
    )

    async def test():
        async with AsyncSessionLocal() as s:
            doc = (
                await s.execute(
                    select(Document)
                    .where(Document.original_filename == "Interview.pdf")
                    .limit(1)
                )
            ).scalar_one()
            content = (
                await s.execute(
                    select(DocumentContent)
                    .where(DocumentContent.document_id == doc.id)
                    .limit(1)
                )
            ).scalar_one()
            strat = RecursiveTextChunkStrategy(chunk_size=1000, chunk_overlap=200)
            strat.chunk(content.raw_text)

    asyncio.run(test())
