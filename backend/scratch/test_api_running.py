if __name__ == '__main__':
    import asyncio
    from sqlalchemy import select
    from app.db.session import async_session_maker
    from app.models.user import User
    from app.core.security import create_access_token
    import requests
    
    async def test_api():
        async with async_session_maker() as session:
            result = await session.execute(select(User).limit(1))
            user = result.scalars().first()
        
        if not user:
            print("No user found in db!")
            return
            
        token = create_access_token(subject=str(user.id))
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "question": "What is this about?",
            "top_k": 5,
            "search_k": 20
        }
        
        print(f"Sending POST to http://localhost:8000/api/v1/chat/ with user {user.id}")
        try:
            response = requests.post("http://localhost:8000/api/v1/chat/", headers=headers, json=payload)
            print("Status Code:", response.status_code)
            print("Response JSON:", response.json())
        except Exception as e:
            print("Error:", e)
    
    asyncio.run(test_api())
    
