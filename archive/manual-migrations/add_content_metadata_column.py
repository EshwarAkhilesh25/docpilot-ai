import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal


async def add_content_metadata_column():
    """Add content_metadata column to document_contents table if it doesn't exist."""
    async with AsyncSessionLocal() as session:
        try:
            # Check if column exists
            result = await session.execute(
                text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'document_contents' 
                AND column_name = 'content_metadata'
            """)
            )
            column_exists = result.fetchone()

            if not column_exists:
                # Add the column
                await session.execute(
                    text("""
                    ALTER TABLE document_contents 
                    ADD COLUMN content_metadata JSONB
                """)
                )
                await session.commit()
                print(
                    "Successfully added content_metadata column to document_contents table"
                )
            else:
                print(
                    "content_metadata column already exists in document_contents table"
                )

        except Exception as e:
            await session.rollback()
            print(f"Error adding content_metadata column: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(add_content_metadata_column())
