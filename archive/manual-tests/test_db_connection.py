import pytest

import asyncio
import asyncpg


@pytest.mark.asyncio
async def test_db_connection():
    # Try common PostgreSQL configurations
    configs = [
        "postgresql://postgres:postgres@localhost:5432/docmind",
        "postgresql://postgres:@localhost:5432/docmind",
        "postgresql://postgres:password@localhost:5432/docmind",
        "postgresql://postgres:123456@localhost:5432/docmind",
        "postgresql://postgres:admin@localhost:5432/docmind",
        "postgresql://postgres:root@localhost:5432/docmind",
        "postgresql://postgres:docmind@localhost:5432/docmind",
    ]

    for config in configs:
        try:
            print(f"Trying: {config}")
            conn = await asyncpg.connect(config)
            print(f"Database connection successful with: {config}")
            version = await conn.fetchval("SELECT version()")
            print(f"PostgreSQL version: {version[:50]}...")
            await conn.close()
            return config
        except Exception as e:
            print(f"Failed: {e}")
            continue

    print("None of the common configurations worked")
    return None


if __name__ == "__main__":
    result = asyncio.run(test_db_connection())
    if result:
        print(f"\nWorking connection string: {result}")
        print("Update your .env file with DATABASE_URL=" + result)
    else:
        print("\nPlease provide your PostgreSQL credentials:")
        print("1. Username")
        print("2. Password")
        print("3. Database name")
        print("4. Port (default: 5432)")
        print("\nOr check if PostgreSQL is running on your system")
