import asyncio
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.user import User
from app.api.dependencies import get_llm_provider, get_vector_index_provider, get_embedding_provider
from app.chat.classification.rule_based_classifier import RuleBasedClassifier
from app.chat.pipeline.orchestrator import ChatPipelineService
from app.db.unit_of_work import UnitOfWorkFactory

async def run_chat():
    async with async_session_maker() as session:
        result = await session.execute(select(User).limit(1))
        user = result.scalars().first()
    
    if not user:
        print("No user found")
        return
        
    print(f"Using user: {user.id}")
    
    # We need to manually instantiate providers or just use them if they don't need app state
    try:
        from app.core.bootstrap import initialize_application
        await initialize_application()
    except Exception as e:
        pass
        
    from app.main import app
    # Actually it's easier to just call the API with a JWT.
    
asyncio.run(run_chat())
