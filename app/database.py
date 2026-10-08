from sqlalchemy.orm import declarative_base,sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from app.config import DATABASE_URL


engine=create_async_engine(DATABASE_URL,
                           echo=True)
AsyncSessionLocal=sessionmaker(bind=engine,autoflush=True,class_=AsyncSession,expire_on_commit=False)

Base=declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session