from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from settings import db_settings

async_engine = create_async_engine(
    db_settings.url,
    pool_pre_ping=True,  # drop connections the server closed while idle
    pool_recycle=1800,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)

# Objects stay readable after commit, so routers can serialize them.
async_session = async_sessionmaker(
    async_engine, expire_on_commit=False, autoflush=False
)
