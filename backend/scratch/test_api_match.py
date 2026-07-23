import pytest

import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.document import Document
from app.core.security import create_access_token
import requests
import uuid

@pytest.mark.asyncio
async def run_api():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).limit(1))
        user = result.scalars().first()
        
        doc_result = await session.execute(select(Document).limit(1))
        doc = doc_result.scalars().first()
        
    if not user:
        print("No user found in db!")
        return
        
    token = create_access_token(subject=str(user.id))
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "question": "What is this document about?", # Usually hits at least some text!
        "top_k": 5,
        "search_k": 20,
        "document_ids": [str(doc.id)] if doc else []
    }
    
    print(f"Sending POST to http://localhost:8000/api/v1/chat/ with user {user.id} and doc {doc.id if doc else None}")
    try:
        response = requests.post("http://localhost:8000/api/v1/chat/", headers=headers, json=payload)
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(run_api())
