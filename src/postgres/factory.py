from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.settings.factories.postgres import PostgresSettings


def initialize_postgres_pool(settings: PostgresSettings) -> async_sessionmaker:
    engine = create_async_engine(
        url=settings.dsn,

        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,

        future=True,
        pool_pre_ping=True,
    )
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
