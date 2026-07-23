from app.chat.workflows.registry import registry

print("Registered:", list(registry._workflows.keys()))
