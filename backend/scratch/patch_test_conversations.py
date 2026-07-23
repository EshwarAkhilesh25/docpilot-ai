import os
import re

def fix_test_conversations():
    filepath = "tests/api/test_conversations.py"
    with open(filepath, 'r') as f:
        content = f.read()

    # Add fixture for override_dependencies
    fixture_code = """
from app.api.dependencies import get_current_user
from app.api.v1.chat import get_conversation_service

@pytest.fixture(autouse=True)
def override_dependencies(mock_current_user):
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    yield
    app.dependency_overrides.clear()

"""
    if "override_dependencies" not in content:
        content = content.replace("class TestListConversations:", fixture_code + "class TestListConversations:")
    
    # We still need mock_uow for ConversationService which is created directly by UnitOfWorkFactory.create in the endpoint!
    # Wait, in app.api.v1.chat, how is ConversationService instantiated?
    # Let's check app.api.v1.chat for get_conversations endpoint.
    
    # For now, let's just write the patched test_conversations.py
    
    # The unauthorized tests need to override get_current_user to raise HTTPException
    # We'll just patch the tests manually to raise HTTPException in mock_current_user? 
    # Or override the dependency per-test. Let's do it per test.

    with open(filepath, 'w') as f:
        f.write(content)

fix_test_conversations()
