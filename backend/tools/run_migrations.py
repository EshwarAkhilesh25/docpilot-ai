"""Script to run database migrations manually."""

import asyncio

from sqlalchemy import text

from app.db.session import engine


async def run_migrations():
    """Create chat tables if they don't exist."""
    async with engine.begin() as conn:
        # Create chatrole enum type if it doesn't exist
        result = await conn.execute(
            text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type
                WHERE typname = 'chatrole'
            )
        """)
        )
        chatrole_exists = result.scalar()

        if not chatrole_exists:
            pass
            await conn.execute(
                text("""
                CREATE TYPE chatrole AS ENUM ('USER', 'ASSISTANT')
            """)
            )
            pass
        else:
            pass

        # Check if chat_sessions table exists
        result = await conn.execute(
            text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'chat_sessions'
            )
        """)
        )
        chat_sessions_exists = result.scalar()

        if not chat_sessions_exists:
            pass
            await conn.execute(
                text("""
                CREATE TABLE chat_sessions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    document_ids JSON
                )
            """)
            )
            await conn.execute(
                text("""
                CREATE INDEX ix_chat_sessions_user_id ON chat_sessions(user_id)
            """)
            )
            pass
        else:
            pass

        # Check if chat_messages table exists
        result = await conn.execute(
            text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'chat_messages'
            )
        """)
        )
        chat_messages_exists = result.scalar()

        if not chat_messages_exists:
            pass
            await conn.execute(
                text("""
                CREATE TABLE chat_messages (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                    role chatrole NOT NULL,
                    content TEXT NOT NULL,
                    sources JSON
                )
            """)
            )
            await conn.execute(
                text("""
                CREATE INDEX ix_chat_messages_session_id ON chat_messages(session_id)
            """)
            )
            pass
        else:
            pass

    pass


if __name__ == "__main__":
    asyncio.run(run_migrations())
