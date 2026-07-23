import asyncio
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.user import User
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_current_user

async def get_real_user():
    async with async_session_maker() as session:
        result = await session.execute(select(User).limit(1))
        return result.scalars().first()

user = asyncio.run(get_real_user())

if not user:
    print("No users in DB!")
else:
    print(f"Testing with User ID: {user.id}")
    
    def mock_get_current_user():
        return user
        
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/chat/",
            json={
                "question": "What is this about?",
                "top_k": 5,
                "search_k": 20
            }
        )
        print("Status:", response.status_code)
        print("Response:", response.text)
