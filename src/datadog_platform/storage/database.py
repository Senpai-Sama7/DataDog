
import asyncio
from typing import AsyncGenerator

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from datadog_platform.storage.config import PostgreSQLConfig


class DatabaseManager:
    """Manages asynchronous database connections and sessions."""

    def __init__(self, config: PostgreSQLConfig):
        self.config = config
        self.engine = None
        self.SessionLocal = None

    async def initialize(self):
        """
        Initialize the asynchronous database engine and session factory.
        """
        if self.engine is None:
            database_url = (
                f"postgresql+asyncpg://{self.config.user}:{self.config.password}"
                f"@{self.config.host}:{self.config.port}/{self.config.database}"
            )
            self.engine = create_async_engine(
                database_url,
                echo=False,  # Set to True for SQL logging
                pool_size=self.config.min_size,
                max_overflow=self.config.max_size - self.config.min_size,
            )
            self.SessionLocal = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

    async def close(self):
        """
        Close the database engine.
        """
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.SessionLocal = None

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provide an asynchronous session for database operations.
        """
        if self.SessionLocal is None:
            raise RuntimeError("DatabaseManager not initialized. Call initialize() first.")

        async with self.SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()


# Example usage (for testing/demonstration)
async def main():
    config = PostgreSQLConfig()
    db_manager = DatabaseManager(config)
    await db_manager.initialize()

    async with db_manager.get_session() as session:
        # Perform database operations here
        print("Database session obtained.")

    await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
