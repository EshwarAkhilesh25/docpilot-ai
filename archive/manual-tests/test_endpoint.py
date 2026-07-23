if __name__ == "__main__":
    import requests
    import uuid

    # get a conversation first or just send a fresh session id
    session_id = str(uuid.uuid4())
    payload = {
        "question": "pick up some topic and explain me very clearly",
        "session_id": session_id,
        "user_id": "test_user",
        "document_ids": [],
    }

    response = requests.post("http://localhost:8000/api/v1/chat/", json=payload)
    print(response.json())
