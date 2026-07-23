import pytest

import asyncio
from uuid import uuid4
from app.db.unit_of_work import UnitOfWorkFactory
from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.models.enums import ProcessingStatus, FileType


@pytest.mark.asyncio
async def test_document_creation():
    uow = UnitOfWorkFactory.create()
    try:
        async with uow:
            # Test creating a Document
            document_id = uuid4()
            user_id = uuid4()
            document = Document(
                id=document_id,
                user_id=user_id,
                original_filename="test.pdf",
                stored_filename="test.pdf",
                file_type=FileType.PDF,
                processing_status=ProcessingStatus.UPLOADED,
                storage_path="storage/uploads/test.pdf",
                file_size=1024,
                mime_type="application/pdf",
            )

            await uow.document_repository.create(document)
            await uow.commit()

            print(f"Document created successfully: {document_id}")

            # Test creating a ProcessingJob
            processing_job = ProcessingJob(
                document_id=document_id,
                status=ProcessingStatus.UPLOADED,
                progress=0,
            )

            await uow.processing_job_repository.create(processing_job)
            await uow.commit()

            print(f"ProcessingJob created successfully: {processing_job.id}")

            # Clean up
            await uow.processing_job_repository.delete(processing_job.id)
            await uow.document_repository.delete(document_id)
            await uow.commit()

            print("Cleanup successful")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


asyncio.run(test_document_creation())
