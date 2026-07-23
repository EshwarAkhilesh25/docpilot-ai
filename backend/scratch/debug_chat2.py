from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_current_user
from app.models.user import User
import uuid

# Mock current user
def mock_get_current_user():
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        is_active=True
    )

app.dependency_overrides[get_current_user] = mock_get_current_user

try:
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
except Exception as e:
    import traceback
    traceback.print_exc()
