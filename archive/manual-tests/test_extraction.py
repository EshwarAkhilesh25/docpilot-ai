"""Script to directly test PDF extraction for the failing document."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ingestion.factory.processor_factory import ProcessorFactory
from app.ingestion.pipeline.ingestion_pipeline import IngestionPipeline
from app.core.config import get_settings

settings = get_settings()


async def main():
    """Test PDF extraction for the failing document."""
    document_id = "18fee765-96d2-4cbf-b84d-83ee5bb93e34"  # LOR HOD - Charan.pdf

    print(f"Testing extraction for document: {document_id}")

    # Get document from database
    import psycopg2

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="eshwar",
        database="docmind",
    )
    cur = conn.cursor()
    cur.execute("SELECT storage_path FROM documents WHERE id = %s", (document_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if not result:
        print("Document not found in database")
        return

    storage_path = result[0]
    print(f"Storage path: {storage_path}")

    # Build full file path
    file_path = str(Path(settings.STORAGE_PATH) / storage_path)
    print(f"Full file path: {file_path}")

    # Check if file exists
    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        return

    # Create processor factory
    processor_factory = ProcessorFactory()

    # Create ingestion pipeline
    ingestion_pipeline = IngestionPipeline(
        processor_factory=processor_factory,
        text_normalizer=None,
    )

    # Extract text
    from app.models.enums import FileType

    try:
        # First, try to open the PDF directly with fitz to debug
        import fitz

        doc = fitz.open(file_path)
        print("\nDirect PyMuPDF debug:")
        print(f"Page count: {doc.page_count}")
        print(f"Is encrypted: {doc.is_encrypted}")
        print(f"Metadata: {doc.metadata}")
        print(f"Is PDF: {doc.is_pdf}")

        # Try to get text from first page if it exists
        if doc.page_count > 0:
            page = doc[0]
            text = page.get_text()
            print(f"First page text length: {len(text)}")
            print(f"First page text preview: {text[:200] if text else 'EMPTY'}")
        doc.close()

        result = await ingestion_pipeline.process(Path(file_path), FileType.PDF)
        print("\nExtraction successful!")
        print(f"Page count: {result.page_count}")
        print(f"Character count: {result.character_count}")
        print(
            f"First 500 chars: {result.raw_text[:500] if result.raw_text else 'EMPTY'}"
        )
        print(
            f"Last 500 chars: {result.raw_text[-500:] if result.raw_text and len(result.raw_text) > 500 else 'EMPTY'}"
        )
    except Exception as e:
        print(f"Extraction failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
