if __name__ == "__main__":
    """Test chat with Blockchain document."""

    import requests

    # Login with existing user
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    print(f"Login Status: {login_response.status_code}")

    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print("Token obtained")

        # Test chat with Blockchain document
        chat_response = requests.post(
            "http://localhost:8000/api/v1/chat/",
            json={
                "question": "What is this document about?",
                "document_ids": ["5fa51bae-9e45-497a-9836-bdbd964a451b"],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        print(f"\nChat Status: {chat_response.status_code}")
        print(chat_response.text)

        # Test with another question
        chat_response2 = requests.post(
            "http://localhost:8000/api/v1/chat/",
            json={
                "question": "What information is in the document?",
                "document_ids": ["5fa51bae-9e45-497a-9836-bdbd964a451b"],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        print(f"\nChat Status 2: {chat_response2.status_code}")
        print(chat_response2.text)
